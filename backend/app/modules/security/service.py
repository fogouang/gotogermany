"""
app/modules/security/service.py

Côté admin : incidents, élèves bloqués, déblocage, bannissement, export des preuves.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.security.models import ContentAccessEvent, ContentBlock, SecurityIncident
from app.modules.users.models import User
from app.shared.exceptions.http import NotFoundException

logger = logging.getLogger("security")


class SecurityService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Lecture ──────────────────────────────────────────

    async def _users(self, ids: set) -> dict:
        if not ids:
            return {}
        users = (await self.db.execute(select(User).where(User.id.in_(ids)))).scalars().all()
        blocked = set(
            (await self.db.execute(select(ContentBlock.user_id).where(ContentBlock.user_id.in_(ids)))).scalars().all()
        )
        return {
            u.id: {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "phone": getattr(u, "phone", None),
                "is_active": u.is_active,
                "is_blocked": u.id in blocked,
            }
            for u in users
        }

    def _incident_dict(self, i: SecurityIncident, users: dict) -> dict:
        return {
            "id": i.id,
            "user": users.get(i.user_id) or {
                "id": i.user_id, "full_name": "(supprimé)", "is_active": False, "is_blocked": False,
            },
            "rule": i.rule,
            "severity": i.severity,
            "action": i.action,
            "ip": i.ip,
            "user_agent": i.user_agent,
            "status": i.status,
            "created_at": i.created_at,
            "resolved_at": i.resolved_at,
            "resolution_note": i.resolution_note,
            "details": i.details or {},
        }

    async def summary(self) -> dict:
        open_q = select(func.count()).select_from(SecurityIncident).where(SecurityIncident.status == "open")
        return {
            "open_incidents": int((await self.db.execute(open_q)).scalar() or 0),
            "open_high": int((await self.db.execute(open_q.where(SecurityIncident.severity == "high"))).scalar() or 0),
            "blocked_users": int(
                (await self.db.execute(select(func.count()).select_from(ContentBlock))).scalar() or 0
            ),
        }

    async def list_incidents(self, status: str | None, limit: int) -> list[dict]:
        stmt = select(SecurityIncident).order_by(SecurityIncident.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(SecurityIncident.status == status)
        incidents = (await self.db.execute(stmt)).scalars().all()
        users = await self._users({i.user_id for i in incidents})
        return [self._incident_dict(i, users) for i in incidents]

    async def get_incident(self, incident_id: UUID) -> dict:
        incident = await self.db.get(SecurityIncident, incident_id)
        if not incident:
            raise NotFoundException(resource="Incident", identifier=str(incident_id))
        users = await self._users({incident.user_id})
        return self._incident_dict(incident, users)

    async def list_blocks(self) -> list[dict]:
        blocks = (await self.db.execute(select(ContentBlock).order_by(ContentBlock.created_at.desc()))).scalars().all()
        users = await self._users({b.user_id for b in blocks})
        return [
            {
                "user": users.get(b.user_id),
                "reason": b.reason,
                "incident_id": b.incident_id,
                "blocked_at": b.created_at,
            }
            for b in blocks
            if users.get(b.user_id)
        ]

    # ── Actions ──────────────────────────────────────────

    async def resolve_incident(self, incident_id: UUID, admin: User, note: str | None) -> dict:
        incident = await self.db.get(SecurityIncident, incident_id)
        if not incident:
            raise NotFoundException(resource="Incident", identifier=str(incident_id))
        incident.status = "resolved"
        incident.resolved_by = admin.id
        incident.resolved_at = datetime.now(timezone.utc)
        incident.resolution_note = note
        await self.db.commit()
        return await self.get_incident(incident_id)

    async def unblock_user(self, user_id: UUID, admin: User) -> None:
        block = await self.db.get(ContentBlock, user_id)
        if block:
            await self.db.delete(block)
        user = await self.db.get(User, user_id)
        if user and not user.is_active:
            user.is_active = True
        await self.db.commit()
        logger.warning(f"[SECURITE] Déblocage de {user_id} par {admin.id}")

    async def ban_user(self, user_id: UUID, admin: User, note: str | None) -> None:
        """Compte désactivé : l'élève ne peut plus se connecter."""
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundException(resource="User", identifier=str(user_id))
        user.is_active = False
        if await self.db.get(ContentBlock, user_id) is None:
            self.db.add(ContentBlock(user_id=user_id, reason="banned"))
        self.db.add(SecurityIncident(
            user_id=user_id,
            rule="manual_ban",
            severity="high",
            action="banned",
            details={"by": str(admin.id), "note": note},
            status="resolved",
            resolved_by=admin.id,
            resolved_at=datetime.now(timezone.utc),
            resolution_note=note,
        ))
        await self.db.commit()
        logger.warning(f"[SECURITE] Bannissement de {user_id} par {admin.id} : {note}")

    async def evidence(self, user_id: UUID) -> dict:
        """Dossier complet d'un élève : identité, incidents, tous ses accès au contenu."""
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundException(resource="User", identifier=str(user_id))

        incidents = (
            await self.db.execute(
                select(SecurityIncident).where(SecurityIncident.user_id == user_id)
                .order_by(SecurityIncident.created_at)
            )
        ).scalars().all()
        events = (
            await self.db.execute(
                select(ContentAccessEvent).where(ContentAccessEvent.user_id == user_id)
                .order_by(ContentAccessEvent.created_at)
            )
        ).scalars().all()
        users = await self._users({user_id})

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "user": {
                **{k: str(v) if isinstance(v, UUID) else v for k, v in users[user_id].items()},
                "created_at": getattr(user, "created_at", None).isoformat() if getattr(user, "created_at", None) else None,
            },
            "incidents": [
                {
                    "at": i.created_at.isoformat(),
                    "rule": i.rule,
                    "severity": i.severity,
                    "action": i.action,
                    "ip": i.ip,
                    "user_agent": i.user_agent,
                    "counts": (i.details or {}).get("counts"),
                    "status": i.status,
                    "note": i.resolution_note,
                }
                for i in incidents
            ],
            "content_access": [
                {
                    "at": e.created_at.isoformat(),
                    "kind": e.kind,
                    "resource_id": e.resource_id,
                    "path": e.path,
                    "ip": e.ip,
                    "user_agent": e.user_agent,
                }
                for e in events
            ],
            "distinct_ips": sorted({e.ip for e in events if e.ip}),
            "distinct_user_agents": sorted({e.user_agent for e in events if e.user_agent}),
        }