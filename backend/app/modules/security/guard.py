"""
app/modules/security/guard.py

Garde anti-aspiration, appelée en tête des routes qui livrent du contenu :

    await ContentGuard(db).check(request, current_user, "session_start", subject_id)

Chaque appel est journalisé. Selon le comportement de l'élève :
  - rien d'anormal       → la requête passe
  - signal faible        → incident « logged » (pour suivi), la requête passe
  - rafale de requêtes   → 429 + incident « throttled »
  - aspiration probable  → accès aux sujets suspendu + incident « blocked » + 403

Admins, enseignants et personnel de centre ne sont jamais contrôlés.
"""
import logging
import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.security.models import ContentAccessEvent, ContentBlock, SecurityIncident
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import ForbiddenException

logger = logging.getLogger("security")

# ── Seuils (un élève normal ouvre 1 ou 2 sujets par heure) ──────────
SUBJECTS_WARN_10MIN = 5      # sujets différents en 10 min → incident pour suivi
SUBJECTS_BLOCK_10MIN = 8     # sujets différents en 10 min → blocage
SUBJECTS_BLOCK_1H = 20       # sujets différents en 1 h    → blocage
SESSIONS_BLOCK_1H = 12       # sessions démarrées en 1 h   → blocage
RESULTS_BLOCK_1H = 15        # corrigés différents en 1 h  → blocage
REQUESTS_THROTTLE_1MIN = 40  # appels de contenu en 1 min  → 429

# Clients qui ne sont pas un navigateur : scripts, outils d'API, navigateurs pilotés
SCRIPTED_UA = re.compile(
    r"python-requests|python-urllib|aiohttp|httpx|curl/|wget|scrapy|go-http-client|"
    r"okhttp|java/|libwww|postman|insomnia|thunder client|headlesschrome|puppeteer|"
    r"playwright|selenium|phantomjs",
    re.IGNORECASE,
)

STAFF_ROLES = {UserRole.teacher, UserRole.center_director, UserRole.branch_secretary}

BLOCKED_MESSAGE = (
    "Votre accès aux sujets est suspendu suite à une activité inhabituelle sur votre compte. "
    "Contactez le support pour le rétablir."
)


def client_ip(request: Request) -> str | None:
    """IP réelle derrière nginx/Docker (X-Forwarded-For ou X-Real-IP)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()[:64]
    return request.client.host if request.client else None


class ContentGuard:

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def is_exempt(user: User) -> bool:
        return bool(getattr(user, "is_admin", False)) or user.role in STAFF_ROLES

    async def is_blocked(self, user_id) -> bool:
        return await self.db.get(ContentBlock, user_id) is not None

    async def check(self, request: Request, user: User, kind: str, resource_id=None) -> None:
        if self.is_exempt(user):
            return

        if await self.is_blocked(user.id):
            raise ForbiddenException(detail=BLOCKED_MESSAGE)

        ip = client_ip(request)
        ua = (request.headers.get("user-agent") or "")[:400]
        now = datetime.now(timezone.utc)

        self.db.add(ContentAccessEvent(
            user_id=user.id,
            kind=kind,
            resource_id=str(resource_id) if resource_id else None,
            path=request.url.path[:255],
            ip=ip,
            user_agent=ua,
            created_at=now,
        ))
        await self.db.flush()

        # ── Client scripté : bloqué tout de suite ──
        if not ua or SCRIPTED_UA.search(ua):
            await self._block(user, "scripted_client", ip, ua, now,
                              {"user_agent": ua or "(vide)"})

        counts = await self._counts(user.id, now)

        # ── Aspiration probable : blocage ──
        if counts["subjects_10min"] > SUBJECTS_BLOCK_10MIN:
            await self._block(user, "too_many_subjects_10min", ip, ua, now, counts)
        if counts["subjects_1h"] > SUBJECTS_BLOCK_1H:
            await self._block(user, "too_many_subjects_1h", ip, ua, now, counts)
        if counts["sessions_1h"] > SESSIONS_BLOCK_1H:
            await self._block(user, "too_many_sessions_1h", ip, ua, now, counts)
        if counts["results_1h"] > RESULTS_BLOCK_1H:
            await self._block(user, "too_many_results_1h", ip, ua, now, counts)

        # ── Rafale : ralentissement ──
        if counts["requests_1min"] > REQUESTS_THROTTLE_1MIN:
            await self._incident(user, "request_burst", "medium", "throttled", ip, ua, now, counts,
                                 dedupe=timedelta(minutes=10))
            await self.db.commit()
            raise HTTPException(status_code=429, detail="Trop de requêtes. Patientez une minute.")

        # ── Signal faible : suivi seulement ──
        if counts["subjects_10min"] > SUBJECTS_WARN_10MIN:
            await self._incident(user, "many_subjects_warning", "low", "logged", ip, ua, now, counts,
                                 dedupe=timedelta(hours=1))

        await self.db.commit()

    # ── Compteurs ────────────────────────────────────────

    async def _counts(self, user_id, now: datetime) -> dict:
        E = ContentAccessEvent

        async def scalar(stmt) -> int:
            return int((await self.db.execute(stmt)).scalar() or 0)

        opening = E.kind.in_(("subject_view", "session_start"))
        return {
            "requests_1min": await scalar(
                select(func.count()).where(E.user_id == user_id, E.created_at >= now - timedelta(minutes=1))
            ),
            "subjects_10min": await scalar(
                select(func.count(func.distinct(E.resource_id)))
                .where(E.user_id == user_id, opening, E.created_at >= now - timedelta(minutes=10))
            ),
            "subjects_1h": await scalar(
                select(func.count(func.distinct(E.resource_id)))
                .where(E.user_id == user_id, opening, E.created_at >= now - timedelta(hours=1))
            ),
            "sessions_1h": await scalar(
                select(func.count())
                .where(E.user_id == user_id, E.kind == "session_start", E.created_at >= now - timedelta(hours=1))
            ),
            "results_1h": await scalar(
                select(func.count(func.distinct(E.resource_id)))
                .where(E.user_id == user_id, E.kind == "result_view", E.created_at >= now - timedelta(hours=1))
            ),
        }

    async def _recent_events(self, user_id, limit: int = 50) -> list[dict]:
        rows = (
            await self.db.execute(
                select(ContentAccessEvent)
                .where(ContentAccessEvent.user_id == user_id)
                .order_by(ContentAccessEvent.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
        return [
            {
                "at": r.created_at.isoformat(),
                "kind": r.kind,
                "resource_id": r.resource_id,
                "path": r.path,
                "ip": r.ip,
                "user_agent": r.user_agent,
            }
            for r in rows
        ]

    # ── Incidents et blocage ─────────────────────────────

    async def _incident(
        self, user: User, rule: str, severity: str, action: str,
        ip: str | None, ua: str, now: datetime, data: dict,
        dedupe: timedelta | None = None,
    ) -> SecurityIncident | None:
        if dedupe:
            existing = (
                await self.db.execute(
                    select(SecurityIncident.id).where(
                        SecurityIncident.user_id == user.id,
                        SecurityIncident.rule == rule,
                        SecurityIncident.created_at >= now - dedupe,
                    ).limit(1)
                )
            ).scalar()
            if existing:
                return None

        incident = SecurityIncident(
            user_id=user.id,
            rule=rule,
            severity=severity,
            action=action,
            ip=ip,
            user_agent=ua,
            details={
                "counts": data,
                "user": {"full_name": user.full_name, "email": user.email, "phone": getattr(user, "phone", None)},
                "recent_events": await self._recent_events(user.id),
            },
            status="open",
        )
        self.db.add(incident)
        await self.db.flush()
        logger.warning(
            f"[SECURITE] {action.upper()} {rule} — user={user.id} ({user.email}) ip={ip} ua={ua!r} data={data}"
        )
        return incident

    async def _block(self, user: User, rule: str, ip, ua, now, data: dict) -> None:
        incident = await self._incident(user, rule, "high", "blocked", ip, ua, now, data)
        if await self.db.get(ContentBlock, user.id) is None:
            self.db.add(ContentBlock(
                user_id=user.id,
                reason=rule,
                incident_id=incident.id if incident else None,
            ))
        await self.db.commit()
        raise ForbiddenException(detail=BLOCKED_MESSAGE)