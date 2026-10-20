"""
app/modules/sales/service.py

Ventes partenaires : règles de commission, activation de comptes,
blocage (délai de paiement + plafond d'impayés) et règlements.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import (
    CommissionRule,
    PartnerSale,
    PartnerSettlement,
    PartnerSettlementAllocation,
)
from app.modules.sales.schemas import (
    ActivationRequest,
    ActivationResponse,
    CommissionRuleCreate,
    CommissionRuleUpdate,
    PartnerSaleResponse,
    PartnerSettingsUpdate,
    PartnerSummaryResponse,
    PlatformRevenueResponse,
    SettlementCreate,
)
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)

logger = logging.getLogger(__name__)

CENTER = "center"
AMBASSADOR = "ambassador"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def compute_partner_share(price: int, rule_type: str, value: Decimal) -> int:
    """Part du partenaire, jamais supérieure au prix."""
    if rule_type == "percent":
        share = (Decimal(price) * Decimal(value) / Decimal(100)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        return int(min(share, Decimal(price)))
    return int(min(Decimal(value), Decimal(price)))


@dataclass
class Partner:
    type: str
    id: UUID
    name: str
    can_activate: bool
    unpaid_limit: int | None
    payment_delay_hours: int
    trial_until: datetime | None = None
    trial_left: int = 0

    @property
    def trial_active(self) -> bool:
        """Essai en cours : centre, activations restantes et date non dépassée."""
        return (
            self.type == CENTER
            and self.trial_left > 0
            and self.trial_until is not None
            and self.trial_until > _now()
        )

    @property
    def sale_filter(self):
        return PartnerSale.center_id == self.id if self.type == CENTER else PartnerSale.user_id == self.id

    @property
    def settlement_filter(self):
        return (
            PartnerSettlement.center_id == self.id
            if self.type == CENTER
            else PartnerSettlement.user_id == self.id
        )


class SalesService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Partenaires ──────────────────────────────────────

    async def get_partner(self, partner_type: str, partner_id: UUID, lock: bool = False) -> Partner:
        if partner_type == CENTER:
            from app.modules.centers.models import Center

            q = select(Center).where(Center.id == partner_id)
            if lock:
                q = q.with_for_update()
            center = (await self.db.execute(q)).scalar_one_or_none()
            if not center:
                raise NotFoundException(resource="Center", identifier=str(partner_id))
            return Partner(
                CENTER, center.id, center.name, center.partner_can_activate,
                center.partner_unpaid_limit, center.partner_payment_delay_hours,
                center.trial_ends_at, center.trial_activations_left or 0,
            )

        if partner_type == AMBASSADOR:
            q = select(User).where(User.id == partner_id)
            if lock:
                q = q.with_for_update()
            user = (await self.db.execute(q)).scalar_one_or_none()
            if not user or not user.is_ambassador:
                raise NotFoundException(resource="Ambassadeur", identifier=str(partner_id))
            return Partner(
                AMBASSADOR, user.id, user.full_name, user.partner_can_activate,
                user.partner_unpaid_limit, user.partner_payment_delay_hours,
            )

        raise BadRequestException(detail="Type de partenaire inconnu.")

    async def partner_for_actor(self, actor: User, lock: bool = False) -> Partner:
        """Centre du directeur/de la secrétaire, ou l'ambassadeur lui-même."""
        if actor.role == UserRole.center_director and actor.center_id:
            return await self.get_partner(CENTER, actor.center_id, lock)
        if actor.role == UserRole.branch_secretary and actor.branch_id:
            from app.modules.centers.models import Branch

            branch = await self.db.get(Branch, actor.branch_id)
            if branch:
                return await self.get_partner(CENTER, branch.center_id, lock)
        if actor.is_ambassador:
            return await self.get_partner(AMBASSADOR, actor.id, lock)
        raise ForbiddenException(
            detail="Action réservée aux centres partenaires et aux ambassadeurs."
        )

    # ── Règles de commission ─────────────────────────────

    async def resolve_rule(self, partner: Partner, plan_id: UUID | None) -> CommissionRule:
        own_col = CommissionRule.center_id if partner.type == CENTER else CommissionRule.user_id
        other_col = CommissionRule.user_id if partner.type == CENTER else CommissionRule.center_id

        plan_cond = (
            or_(CommissionRule.plan_id == plan_id, CommissionRule.plan_id.is_(None))
            if plan_id
            else CommissionRule.plan_id.is_(None)
        )
        result = await self.db.execute(
            select(CommissionRule).where(
                CommissionRule.is_active == True,
                CommissionRule.partner_type == partner.type,
                or_(own_col == partner.id, own_col.is_(None)),
                other_col.is_(None),
                plan_cond,
            )
        )
        rules = list(result.scalars().all())
        if not rules:
            raise BadRequestException(
                detail="Aucune règle de commission active pour ce partenaire. Contactez l'administrateur."
            )

        def specificity(r: CommissionRule):
            own = r.center_id if partner.type == CENTER else r.user_id
            return (own is not None, r.plan_id is not None, r.created_at)

        return max(rules, key=specificity)

    async def list_rules(self) -> list[CommissionRule]:
        result = await self.db.execute(
            select(CommissionRule).order_by(
                CommissionRule.partner_type, CommissionRule.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def create_rule(self, data: CommissionRuleCreate) -> CommissionRule:
        rule = CommissionRule(**data.model_dump(), is_active=True)
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def update_rule(self, rule_id: UUID, data: CommissionRuleUpdate) -> CommissionRule:
        rule = await self.db.get(CommissionRule, rule_id)
        if not rule:
            raise NotFoundException(resource="CommissionRule", identifier=str(rule_id))

        values = data.model_dump(exclude_unset=True, exclude_none=True)
        new_type = values.get("rule_type", rule.rule_type)
        new_value = values.get("value", rule.value)
        if new_type == "percent" and Decimal(new_value) > 100:
            raise BadRequestException(detail="Un pourcentage ne peut pas dépasser 100.")

        for key, val in values.items():
            setattr(rule, key, val)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: UUID) -> None:
        rule = await self.db.get(CommissionRule, rule_id)
        if not rule:
            raise NotFoundException(resource="CommissionRule", identifier=str(rule_id))
        if rule.center_id is None and rule.user_id is None and rule.plan_id is None:
            raise BadRequestException(
                detail="La règle par défaut ne peut pas être supprimée, modifiez-la plutôt."
            )
        await self.db.delete(rule)
        await self.db.commit()

    # ── Soldes et blocage ────────────────────────────────

    async def _sums(self, partner: Partner) -> tuple[int, int, int, int]:
        """(dû à GoToGermany, dû au partenaire, montant en retard, nb ventes en retard)"""
        remaining = PartnerSale.amount_due - PartnerSale.settled_amount
        owes = PartnerSale.direction == "partner_owes"
        late = and_(owes, PartnerSale.due_at.isnot(None), PartnerSale.due_at < _now())

        row = (
            await self.db.execute(
                select(
                    func.coalesce(func.sum(case((owes, remaining), else_=0)), 0),
                    func.coalesce(
                        func.sum(case((PartnerSale.direction == "platform_owes", remaining), else_=0)), 0
                    ),
                    func.coalesce(func.sum(case((late, remaining), else_=0)), 0),
                    func.count(case((late, 1))),
                ).where(partner.sale_filter, PartnerSale.status != "settled")
            )
        ).one()
        return int(row[0]), int(row[1]), int(row[2]), int(row[3])

    @staticmethod
    def _block_reason(
        partner: Partner, owed_to_platform: int, overdue_count: int, new_amount: int
    ) -> str | None:
        if not partner.can_activate:
            return "Les activations sont désactivées pour ce partenaire."
        if overdue_count > 0:
            return (
                "Un règlement est en retard. Réglez les ventes échues pour pouvoir "
                "activer de nouveaux comptes."
            )
        if partner.unpaid_limit is not None and owed_to_platform + new_amount > partner.unpaid_limit:
            return (
                f"Plafond d'impayés atteint ({partner.unpaid_limit} FCFA). "
                "Réglez votre solde pour continuer."
            )
        return None

    async def _earned(self, partner: Partner) -> int:
        """Total gagné par le partenaire : sa part sur toutes ses ventes."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(PartnerSale.partner_share), 0)).where(
                partner.sale_filter
            )
        )
        return int(result.scalar_one())

    async def summary(self, partner: Partner) -> PartnerSummaryResponse:
        owed_platform, owed_partner, overdue_amount, overdue_count = await self._sums(partner)
        earned = await self._earned(partner)
        # new_amount=1 : bloqué si la prochaine activation, quelle qu'elle soit, serait refusée
        reason = self._block_reason(partner, owed_platform, overdue_count, 1)
        return PartnerSummaryResponse(
            partner_type=partner.type,
            partner_id=partner.id,
            name=partner.name,
            can_activate=partner.can_activate,
            unpaid_limit=partner.unpaid_limit,
            payment_delay_hours=partner.payment_delay_hours,
            owed_to_platform=owed_platform,
            owed_to_partner=owed_partner,
            net_balance=owed_platform - owed_partner,
            overdue_amount=overdue_amount,
            overdue_count=overdue_count,
            is_blocked=reason is not None,
            block_reason=reason,
            earned_total=earned,
            trial_active=partner.trial_active,
            trial_ends_at=partner.trial_until,
            trial_activations_left=partner.trial_left,
        )

    # ── Activation d'un compte ───────────────────────────

    async def _assert_student_in_scope(self, actor: User, partner: Partner, student: User) -> None:
        if partner.type == CENTER:
            from app.modules.centers.models import Branch

            branch = await self.db.get(Branch, student.branch_id) if student.branch_id else None
            if not branch or branch.center_id != partner.id:
                raise ForbiddenException(detail="Cet élève n'appartient pas à votre centre.")
            if actor.role == UserRole.branch_secretary and student.branch_id != actor.branch_id:
                raise ForbiddenException(detail="Cet élève n'appartient pas à votre succursale.")
        else:
            if student.referred_by_user_id != partner.id:
                raise ForbiddenException(detail="Vous ne pouvez activer que vos propres filleuls.")

    async def activate(self, actor: User, data: ActivationRequest) -> ActivationResponse:
        from app.modules.exams.models import Level
        from app.modules.payments.models import Payment
        from app.modules.payments.repository import PaymentRepository
        from app.modules.payments.service import PaymentService
        from app.modules.plans.models import Plan

        # Verrou sur la ligne du partenaire : deux activations simultanées
        # ne peuvent pas dépasser le plafond.
        partner = await self.partner_for_actor(actor, lock=True)

        student = await self.db.get(User, data.student_id)
        if not student or student.role != UserRole.student:
            raise NotFoundException(resource="Élève", identifier=str(data.student_id))
        await self._assert_student_in_scope(actor, partner, student)

        level = await self.db.get(Level, data.level_id)
        if not level:
            raise NotFoundException(resource="Level", identifier=str(data.level_id))
        plan = await self.db.get(Plan, data.plan_id)
        if not plan or not plan.is_active:
            raise NotFoundException(resource="Plan", identifier=str(data.plan_id))

        trial = partner.trial_active
        if trial:
            # Essai : activation offerte, rien à encaisser ni à reverser
            price = partner_share = platform_share = 0
            rule_type, rule_value = "percent", Decimal(100)
        else:
            rule = await self.resolve_rule(partner, plan.id)
            price = plan.price
            partner_share = compute_partner_share(plan.price, rule.rule_type, rule.value)
            platform_share = plan.price - partner_share
            rule_type, rule_value = rule.rule_type, rule.value

        owed_platform, _, _, overdue_count = await self._sums(partner)
        reason = self._block_reason(partner, owed_platform, overdue_count, platform_share)
        if reason:
            raise BadRequestException(detail=reason)

        now = _now()
        reference = await PaymentRepository(self.db).generate_transaction_reference()
        reference = reference.replace("GTG-", "GTG-P-", 1)

        payment = Payment(
            user_id=student.id,
            level_id=level.id,
            plan_id=plan.id,
            promo_code_id=None,
            amount_gross=price,
            amount_paid=price,
            commission_due=0.0,
            currency="XAF",
            payment_status="COMPLETED",
            transaction_reference=reference,
            operator="PARTNER",
            completed_at=now,
            pawapay_deposit_id=None,
            validated_manually_by=actor.id,
        )
        self.db.add(payment)
        await self.db.flush()

        sale = PartnerSale(
            payment_id=payment.id,
            student_id=student.id,
            plan_id=plan.id,
            level_id=level.id,
            center_id=partner.id if partner.type == CENTER else None,
            user_id=partner.id if partner.type == AMBASSADOR else None,
            activated_by=actor.id,
            direction="partner_owes",
            price=price,
            partner_share=partner_share,
            platform_share=platform_share,
            amount_due=platform_share,
            settled_amount=0,
            rule_type=rule_type,
            rule_value=rule_value,
            is_trial=trial,
            due_at=now + timedelta(hours=partner.payment_delay_hours),
            status="due" if platform_share > 0 else "settled",
            settled_at=None if platform_share > 0 else now,
        )
        self.db.add(sale)
        await self.db.flush()

        student_name = student.full_name
        plan_name = plan.name
        access_expires_at = now + timedelta(days=plan.duration_days)

        # Essai : une activation offerte de moins (ligne du centre déjà verrouillée)
        if trial:
            from app.modules.centers.models import Center

            center = await self.db.get(Center, partner.id)
            center.trial_activations_left = max(0, (center.trial_activations_left or 0) - 1)

        # Crée/renouvelle l'ExamAccess, ajoute les credits IA du plan
        # et valide toute la transaction (commit)
        payment_service = PaymentService(self.db)
        await payment_service._grant_level_access(payment)
        await payment_service._generate_invoice(payment)

        await self.db.refresh(sale)
        logger.info(
            f"Activation {partner.type} {partner.id} par {actor.id} : élève {student.id}, "
            f"plan {plan.id}, part GoToGermany {platform_share} FCFA"
        )
        return ActivationResponse(
            sale=self._to_sale_response(sale, student_name, plan_name),
            access_expires_at=access_expires_at,
        )

    # ── Vente en ligne d'un filleul (appelé par ReferralService) ──

    async def record_online_referral(
        self, *, payment_id: UUID, payer: User, payment_amount: int
    ) -> PartnerSale | None:
        """Le filleul a payé en ligne : GoToGermany doit sa commission à l'ambassadeur."""
        from app.modules.payments.models import Payment

        if payer.referred_by_user_id is None:
            return None

        existing = (
            await self.db.execute(select(PartnerSale).where(PartnerSale.payment_id == payment_id))
        ).scalar_one_or_none()
        if existing:
            return existing

        referrer = await self.db.get(User, payer.referred_by_user_id)
        if not referrer:
            return None
        partner = Partner(
            AMBASSADOR, referrer.id, referrer.full_name, referrer.partner_can_activate,
            referrer.partner_unpaid_limit, referrer.partner_payment_delay_hours,
        )

        payment = await self.db.get(Payment, payment_id)
        try:
            rule = await self.resolve_rule(partner, payment.plan_id if payment else None)
        except BadRequestException:
            logger.error(f"Aucune règle de commission ambassadeur : paiement {payment_id} ignoré")
            return None

        share = compute_partner_share(payment_amount, rule.rule_type, rule.value)
        if share <= 0:
            return None

        sale = PartnerSale(
            payment_id=payment_id,
            student_id=payer.id,
            plan_id=payment.plan_id if payment else None,
            level_id=payment.level_id if payment else None,
            center_id=None,
            user_id=referrer.id,
            activated_by=None,
            direction="platform_owes",
            price=payment_amount,
            partner_share=share,
            platform_share=payment_amount - share,
            amount_due=share,
            settled_amount=0,
            rule_type=rule.rule_type,
            rule_value=rule.value,
            due_at=None,
            status="due",
        )
        self.db.add(sale)
        await self.db.flush()
        return sale

    # ── Règlements ───────────────────────────────────────

    async def create_settlement(self, admin: User, data: SettlementCreate) -> PartnerSettlement:
        partner = await self.get_partner(data.partner_type, data.partner_id, lock=True)
        sale_direction = "partner_owes" if data.direction == "to_platform" else "platform_owes"

        result = await self.db.execute(
            select(PartnerSale)
            .where(
                partner.sale_filter,
                PartnerSale.direction == sale_direction,
                PartnerSale.status != "settled",
            )
            .order_by(PartnerSale.due_at.asc().nulls_last(), PartnerSale.created_at.asc())
            .with_for_update()
        )
        sales = list(result.scalars().all())
        total_due = sum(s.amount_due - s.settled_amount for s in sales)
        if data.amount > total_due:
            raise BadRequestException(
                detail=f"Le montant dépasse le total dû dans ce sens ({total_due} FCFA)."
            )

        settlement = PartnerSettlement(
            center_id=partner.id if partner.type == CENTER else None,
            user_id=partner.id if partner.type == AMBASSADOR else None,
            direction=data.direction,
            amount=data.amount,
            method=data.method,
            reference=data.reference,
            note=data.note,
            validated_by=admin.id,
        )
        self.db.add(settlement)
        await self.db.flush()

        now = _now()
        left = data.amount
        for sale in sales:
            if left <= 0:
                break
            take = min(left, sale.amount_due - sale.settled_amount)
            if take <= 0:
                continue
            sale.settled_amount += take
            if sale.settled_amount >= sale.amount_due:
                sale.status = "settled"
                sale.settled_at = now
            else:
                sale.status = "partial"
            self.db.add(
                PartnerSettlementAllocation(settlement_id=settlement.id, sale_id=sale.id, amount=take)
            )
            left -= take

        await self.db.commit()
        await self.db.refresh(settlement)
        return settlement

    # ── Listes ───────────────────────────────────────────

    @staticmethod
    def _to_sale_response(sale: PartnerSale, student_name: str, plan_name: str | None) -> PartnerSaleResponse:
        remaining = sale.amount_due - sale.settled_amount
        is_overdue = bool(
            sale.direction == "partner_owes"
            and sale.due_at is not None
            and remaining > 0
            and sale.due_at < _now()
        )
        return PartnerSaleResponse(
            id=sale.id,
            payment_id=sale.payment_id,
            student_id=sale.student_id,
            student_name=student_name,
            plan_name=plan_name,
            level_id=sale.level_id,
            direction=sale.direction,
            price=sale.price,
            partner_share=sale.partner_share,
            platform_share=sale.platform_share,
            amount_due=sale.amount_due,
            settled_amount=sale.settled_amount,
            remaining=remaining,
            rule_type=sale.rule_type,
            rule_value=float(sale.rule_value),
            due_at=sale.due_at,
            is_overdue=is_overdue,
            status=sale.status,
            created_at=sale.created_at,
            is_trial=bool(sale.is_trial),
        )

    async def list_sales(self, partner: Partner, limit: int = 50, offset: int = 0) -> list[PartnerSaleResponse]:
        from app.modules.plans.models import Plan

        result = await self.db.execute(
            select(PartnerSale, User.full_name, Plan.name)
            .join(User, User.id == PartnerSale.student_id)
            .outerjoin(Plan, Plan.id == PartnerSale.plan_id)
            .where(partner.sale_filter)
            .order_by(PartnerSale.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._to_sale_response(s, name, plan) for s, name, plan in result.all()]

    async def list_settlements(self, partner: Partner) -> list[PartnerSettlement]:
        result = await self.db.execute(
            select(PartnerSettlement)
            .where(partner.settlement_filter)
            .order_by(PartnerSettlement.created_at.desc())
        )
        return list(result.scalars().all())

    async def platform_revenue(self) -> PlatformRevenueResponse:
        """Chiffre global : tout ce qui est encaissé, moins la part des partenaires."""
        from app.modules.payments.models import Payment

        now = _now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        in_month = Payment.completed_at >= month_start
        is_partner = Payment.operator == "PARTNER"
        pay = (
            await self.db.execute(
                select(
                    func.coalesce(func.sum(Payment.amount_paid), 0),
                    func.coalesce(func.sum(case((in_month, Payment.amount_paid), else_=0)), 0),
                    func.coalesce(func.sum(case((is_partner, Payment.amount_paid), else_=0)), 0),
                ).where(Payment.payment_status == "COMPLETED")
            )
        ).one()

        sale_in_month = PartnerSale.created_at >= month_start
        com = (
            await self.db.execute(
                select(
                    func.coalesce(func.sum(PartnerSale.partner_share), 0),
                    func.coalesce(
                        func.sum(case((sale_in_month, PartnerSale.partner_share), else_=0)), 0
                    ),
                )
            )
        ).one()

        gross_total, gross_month, partner_total = int(pay[0]), int(pay[1]), int(pay[2])
        commissions_total, commissions_month = int(com[0]), int(com[1])

        return PlatformRevenueResponse(
            gross_total=gross_total,
            commissions_total=commissions_total,
            net_total=gross_total - commissions_total,
            gross_month=gross_month,
            commissions_month=commissions_month,
            net_month=gross_month - commissions_month,
            direct_total=gross_total - partner_total,
            partner_total=partner_total,
        )

    async def admin_overview(self) -> list[PartnerSummaryResponse]:
        from app.modules.centers.models import Center

        out: list[PartnerSummaryResponse] = []
        centers = (await self.db.execute(select(Center).order_by(Center.name))).scalars().all()
        for c in centers:
            out.append(await self.summary(Partner(
                CENTER, c.id, c.name, c.partner_can_activate,
                c.partner_unpaid_limit, c.partner_payment_delay_hours,
                c.trial_ends_at, c.trial_activations_left or 0,
            )))
        ambassadors = (
            await self.db.execute(
                select(User).where(User.is_ambassador == True).order_by(User.full_name)
            )
        ).scalars().all()
        for u in ambassadors:
            out.append(await self.summary(Partner(
                AMBASSADOR, u.id, u.full_name, u.partner_can_activate,
                u.partner_unpaid_limit, u.partner_payment_delay_hours,
            )))
        return out

    # ── Réglages partenaire (admin) ──────────────────────

    async def update_partner_settings(
        self, partner_type: str, partner_id: UUID, data: PartnerSettingsUpdate
    ) -> PartnerSummaryResponse:
        if partner_type == CENTER:
            from app.modules.centers.models import Center
            obj = await self.db.get(Center, partner_id)
        else:
            obj = await self.db.get(User, partner_id)
            if obj and not obj.is_ambassador:
                obj = None
        if not obj:
            raise NotFoundException(resource="Partenaire", identifier=str(partner_id))

        values = data.model_dump(exclude_unset=True)
        if values.get("can_activate") is not None:
            obj.partner_can_activate = values["can_activate"]
        if "unpaid_limit" in values:  # null explicite = plus de plafond
            obj.partner_unpaid_limit = values["unpaid_limit"]
        if values.get("payment_delay_hours") is not None:
            obj.partner_payment_delay_hours = values["payment_delay_hours"]

        # Période d'essai : centres uniquement
        if partner_type == CENTER:
            if "trial_ends_at" in values:  # null explicite = fin de l'essai
                obj.trial_ends_at = values["trial_ends_at"]
            if values.get("trial_activations_left") is not None:
                obj.trial_activations_left = values["trial_activations_left"]

        await self.db.commit()
        return await self.summary(await self.get_partner(partner_type, partner_id))