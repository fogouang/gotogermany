"""
app/modules/invoices/service.py

Reçus de paiement GoToGermany.

Le PDF n'est plus stocké sur le serveur : il est généré en mémoire à chaque
téléchargement (comme les copies Schreiben), puis envoyé au navigateur qui le
récupère en blob. payments.invoice_url sert seulement à signaler qu'un reçu
est disponible pour ce paiement.
"""
import io
import logging
from datetime import datetime
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.users.models import User
from app.shared.database.session import AsyncSession
from app.shared.exceptions.http import NotFoundException

logger = logging.getLogger(__name__)

# ── Couleurs GoToGermany (celles de l'application) ──
INK = colors.HexColor("#18181b")
MUTED = colors.HexColor("#71717a")
LINE = colors.HexColor("#e4e4e7")
SOFT = colors.HexColor("#fafafa")
PRIMARY = colors.HexColor("#f5b400")
PRIMARY_SOFT = colors.HexColor("#fff7db")

PAGE_WIDTH = 17 * cm  # A4 moins les marges

LANGS = ("fr", "en", "de")

# ── Textes du reçu, dans la langue de l'élève ──
TEXTS: dict[str, dict[str, str]] = {
    "fr": {
        "tagline": "Préparation aux examens d'allemand",
        "address": "Dschang, Cameroun · www.prep-telc-osd.com",
        "title": "REÇU DE PAIEMENT",
        "number": "N°",
        "date": "{d} à {h}",
        "billed_to": "FACTURÉ À",
        "payment": "PAIEMENT",
        "paid": "Payé",
        "description": "Description",
        "amount": "Montant",
        "discount": "Réduction (code promo)",
        "total": "TOTAL PAYÉ",
        "card_note": "Payé par carte en euros. Équivalent indicatif : {fcfa}.",
        "partner_title": "CODE PARTENAIRE",
        "partner_code": "Code",
        "partner_name": "Partenaire",
        "commission": "Commission",
        "attest": "Ce reçu atteste le paiement intégral de l'achat décrit ci-dessus.",
        "thanks": "GoToGermany - Fogouang corp · Merci pour votre confiance !",
        "credits": "{n} crédits de correction IA",
        "credits_one": "1 crédit de correction IA",
        "pass": "{exam} - Pass {n} jours",
        "pass_one": "{exam} - Pass 1 jour",
        "plan": "{exam} - {plan} ({n} jours)",
        "access": "{exam} - Accès",
        "exam": "Examen",
        "level": "Niveau {code}",
        "fallback": "Accès GoToGermany",
        "op_card": "Carte bancaire (Visa, Mastercard)",
        "op_manual": "Paiement validé par GoToGermany",
        "op_partner": "Encaissé par le centre ou l'ambassadeur partenaire",
    },
    "en": {
        "tagline": "German exam preparation",
        "address": "Dschang, Cameroon · www.prep-telc-osd.com",
        "title": "PAYMENT RECEIPT",
        "number": "No.",
        "date": "{d} at {h}",
        "billed_to": "BILLED TO",
        "payment": "PAYMENT",
        "paid": "Paid",
        "description": "Description",
        "amount": "Amount",
        "discount": "Discount (promo code)",
        "total": "TOTAL PAID",
        "card_note": "Paid by card in euros. Approximate equivalent: {fcfa}.",
        "partner_title": "PARTNER CODE",
        "partner_code": "Code",
        "partner_name": "Partner",
        "commission": "Commission",
        "attest": "This receipt confirms full payment of the purchase described above.",
        "thanks": "GoToGermany - Fogouang corp · Thank you for your trust!",
        "credits": "{n} AI correction credits",
        "credits_one": "1 AI correction credit",
        "pass": "{exam} - {n}-day pass",
        "pass_one": "{exam} - 1-day pass",
        "plan": "{exam} - {plan} ({n} days)",
        "access": "{exam} - Access",
        "exam": "Exam",
        "level": "Level {code}",
        "fallback": "GoToGermany access",
        "op_card": "Bank card (Visa, Mastercard)",
        "op_manual": "Payment confirmed by GoToGermany",
        "op_partner": "Collected by the partner centre or ambassador",
    },
    "de": {
        "tagline": "Vorbereitung auf Deutschprüfungen",
        "address": "Dschang, Kamerun · www.prep-telc-osd.com",
        "title": "ZAHLUNGSBELEG",
        "number": "Nr.",
        "date": "{d} um {h}",
        "billed_to": "RECHNUNG AN",
        "payment": "ZAHLUNG",
        "paid": "Bezahlt",
        "description": "Beschreibung",
        "amount": "Betrag",
        "discount": "Rabatt (Gutscheincode)",
        "total": "GESAMT BEZAHLT",
        "card_note": "Mit Karte in Euro bezahlt. Ungefährer Gegenwert: {fcfa}.",
        "partner_title": "PARTNERCODE",
        "partner_code": "Code",
        "partner_name": "Partner",
        "commission": "Provision",
        "attest": "Dieser Beleg bestätigt die vollständige Zahlung des oben beschriebenen Kaufs.",
        "thanks": "GoToGermany - Fogouang corp · Vielen Dank für Ihr Vertrauen!",
        "credits": "{n} KI-Korrekturguthaben",
        "credits_one": "1 KI-Korrekturguthaben",
        "pass": "{exam} - {n}-Tage-Pass",
        "pass_one": "{exam} - 1-Tages-Pass",
        "plan": "{exam} - {plan} ({n} Tage)",
        "access": "{exam} - Zugang",
        "exam": "Prüfung",
        "level": "Niveau {code}",
        "fallback": "GoToGermany-Zugang",
        "op_card": "Bankkarte (Visa, Mastercard)",
        "op_manual": "Von GoToGermany bestätigte Zahlung",
        "op_partner": "Vom Partnerzentrum oder Botschafter kassiert",
    },
}


def _lang(lang: str | None) -> str:
    return lang if lang in LANGS else "fr"


def _txt(lang: str, key: str, **kwargs) -> str:
    text = TEXTS[_lang(lang)][key]
    return text.format(**kwargs) if kwargs else text


def _operator_label(operator: str | None, lang: str = "fr") -> str:
    op = (operator or "").upper()
    if not op:
        return "Mobile Money"
    return {
        "MTN": "MTN Mobile Money",
        "ORANGE": "Orange Money",
        "STRIPE": _txt(lang, "op_card"),
        "MANUAL": _txt(lang, "op_manual"),
        "PARTNER": _txt(lang, "op_partner"),
    }.get(op, operator)


def _group(n: str, lang: str) -> str:
    """Séparateur de milliers : 5 000 (fr), 5,000 (en), 5.000 (de)."""
    return n.replace(",", {"fr": " ", "en": ",", "de": "."}[_lang(lang)])


def _fcfa(amount: float | int | None, lang: str = "fr") -> str:
    return f"{_group(f'{int(round(amount or 0)):,}', lang)} FCFA"


def _eur(cents: int, lang: str = "fr") -> str:
    """1000 centimes : 10,00 € (fr, de), €10.00 (en)."""
    raw = f"{cents / 100:,.2f}"  # 1,234.50
    if _lang(lang) == "en":
        return f"€{raw}"
    whole, dec = raw.split(".")
    return f"{_group(whole, lang)},{dec} €"


def _date(dt: datetime, lang: str) -> str:
    fmt = "%d.%m.%Y" if _lang(lang) == "de" else "%d/%m/%Y"
    return _txt(lang, "date", d=dt.strftime(fmt), h=dt.strftime("%H:%M"))


def _esc(text: str | None) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class InvoiceService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)

    # ── Appelé à la validation d'un paiement ─────────────

    async def generate_invoice_for_payment(self, payment_id: UUID) -> str:
        """Marque le reçu comme disponible. Le PDF est généré au téléchargement."""
        invoice_url = f"/api/v1/invoices/{payment_id}/pdf"
        await self.payment_repo.update(payment_id, invoice_url=invoice_url)
        return invoice_url

    # ── Téléchargement ───────────────────────────────────

    async def render_invoice_pdf(
        self, payment_id: UUID, current_user: User, lang: str = "fr"
    ) -> tuple[str, bytes]:
        """Retourne (nom du fichier, contenu PDF) dans la langue demandée.
        Réservé au payeur et aux admins."""
        lang = _lang(lang)
        payment = await self.payment_repo.get_by_id_or_404(payment_id)
        is_staff = bool(getattr(current_user, "is_admin", False))
        if payment.user_id != current_user.id and not is_staff:
            raise NotFoundException(resource="Invoice", identifier=str(payment_id))
        if payment.payment_status != "COMPLETED":
            raise NotFoundException(resource="Invoice", identifier=str(payment_id))

        data = await self.get_invoice_by_payment(payment_id, lang=lang)
        pdf = self._build_pdf(payment=payment, data=data, lang=lang)
        prefix = {"fr": "recu", "en": "receipt", "de": "beleg"}[lang]
        return f"{prefix}_{payment.transaction_reference}.pdf", pdf

    def _build_pdf(self, *, payment: Payment, data: dict, lang: str = "fr") -> bytes:
        T = lambda key, **kw: _esc(_txt(lang, key, **kw))  # noqa: E731
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.6 * cm,
            bottomMargin=1.6 * cm,
            title=f"{_txt(lang, 'title').capitalize()} {payment.transaction_reference}",
            author="GoToGermany",
        )

        brand = ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK)
        tagline = ParagraphStyle("Tagline", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED)
        doc_title = ParagraphStyle(
            "DocTitle", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=INK, alignment=TA_RIGHT
        )
        doc_meta = ParagraphStyle(
            "DocMeta", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED, alignment=TA_RIGHT
        )
        label = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=MUTED)
        value = ParagraphStyle("Value", fontName="Helvetica", fontSize=10, leading=14, textColor=INK)
        value_bold = ParagraphStyle("ValueBold", parent=value, fontName="Helvetica-Bold")
        cell = ParagraphStyle("Cell", fontName="Helvetica", fontSize=10, leading=14, textColor=INK)
        cell_right = ParagraphStyle("CellRight", parent=cell, alignment=TA_RIGHT)
        note = ParagraphStyle("Note", fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED)
        footer = ParagraphStyle(
            "Footer", fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED, alignment=TA_CENTER
        )

        paid_at: datetime = data["payment_date"]
        story = []

        # ── En-tête : marque à gauche, reçu à droite ──
        left = [
            Paragraph("GoToGermany", brand),
            Paragraph(T("tagline"), tagline),
            Paragraph(T("address"), tagline),
        ]
        right = [
            Paragraph(T("title"), doc_title),
            Paragraph(f"{T('number')} {_esc(payment.transaction_reference)}", doc_meta),
            Paragraph(_esc(_date(paid_at, lang)), doc_meta),
        ]

        header = Table([[left, right]], colWidths=[PAGE_WIDTH * 0.55, PAGE_WIDTH * 0.45])
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LINEBELOW", (0, 0), (-1, 0), 3, PRIMARY),
        ]))
        story += [header, Spacer(1, 0.7 * cm)]

        # ── Client et paiement côte à côte ──
        client_block = [Paragraph(T("billed_to"), label), Spacer(1, 3), Paragraph(_esc(data["customer_name"]), value_bold)]
        if data["customer_email"]:
            client_block.append(Paragraph(_esc(data["customer_email"]), value))

        pay_block = [
            Paragraph(T("payment"), label),
            Spacer(1, 3),
            Paragraph(_esc(data["operator"]), value_bold),
            Paragraph(f'<font color="#059669"><b>{T("paid")}</b></font>', value),
        ]

        info = Table([[client_block, pay_block]], colWidths=[PAGE_WIDTH / 2, PAGE_WIDTH / 2])
        info.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), SOFT),
            ("BOX", (0, 0), (0, 0), 0.6, LINE),
            ("BOX", (1, 0), (1, 0), 0.6, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story += [info, Spacer(1, 0.8 * cm)]

        # ── Détail de l'achat ──
        head_l = ParagraphStyle("HeadL", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
        head_r = ParagraphStyle("HeadR", parent=head_l, alignment=TA_RIGHT)
        rows = [
            [Paragraph(T("description"), head_l), Paragraph(T("amount"), head_r)],
            [Paragraph(_esc(data["product_description"]), cell), Paragraph(_fcfa(data["amount_gross"], lang), cell_right)],
        ]
        discount = data["discount_amount"] or 0
        if discount > 0:
            rows.append([
                Paragraph(T("discount"), cell),
                Paragraph(f'<font color="#059669">- {_fcfa(discount, lang)}</font>', cell_right),
            ])

        detail = Table(rows, colWidths=[PAGE_WIDTH * 0.7, PAGE_WIDTH * 0.3])
        detail.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("LINEBELOW", (0, 1), (-1, -1), 0.6, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story += [detail, Spacer(1, 0.4 * cm)]

        # ── Total ──
        is_card = bool(payment.charged_amount) and payment.charged_currency == "EUR"
        total_value = _eur(payment.charged_amount, lang) if is_card else _fcfa(data["amount_paid"], lang)
        total_style = ParagraphStyle("Total", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK)
        total = Table(
            [[Paragraph(T("total"), total_style),
              Paragraph(total_value, ParagraphStyle("TotalR", parent=total_style, alignment=TA_RIGHT))]],
            colWidths=[PAGE_WIDTH * 0.6, PAGE_WIDTH * 0.4],
        )
        total.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_SOFT),
            ("LINEABOVE", (0, 0), (-1, 0), 2, PRIMARY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ]))
        story.append(total)
        if is_card:
            story += [
                Spacer(1, 4),
                Paragraph(T("card_note", fcfa=_fcfa(data["amount_paid"], lang)), note),
            ]

        # ── Code partenaire ──
        partner = data.get("partner_info")
        if partner:
            story.append(Spacer(1, 0.7 * cm))
            partner_rows = [
                [Paragraph(T("partner_title"), label), ""],
                [Paragraph(T("partner_code"), value), Paragraph(_esc(partner.get("code")) or "-", value_bold)],
                [Paragraph(T("partner_name"), value), Paragraph(_esc(partner.get("partner_name")) or "-", value)],
                [Paragraph(T("commission"), value), Paragraph(_fcfa(partner.get("commission_due"), lang), value)],
            ]
            ptable = Table(partner_rows, colWidths=[PAGE_WIDTH * 0.3, PAGE_WIDTH * 0.7])
            ptable.setStyle(TableStyle([
                ("SPAN", (0, 0), (-1, 0)),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(ptable)

        # ── Pied de page ──
        story += [
            Spacer(1, 1.4 * cm),
            Paragraph(T("attest"), footer),
            Paragraph(T("thanks"), footer),
        ]

        doc.build(story)
        return buffer.getvalue()

    # ── Données du reçu ──────────────────────────────────

    async def _get_product_description(self, payment: Payment, lang: str = "fr") -> str:
        try:
            # Achat de crédits IA
            from app.modules.ai_credit_purchases.repository import AICreditPurchaseRepository

            purchase = await AICreditPurchaseRepository(self.db).get_by_payment_id(payment.id)
            if purchase:
                n = purchase.credits_purchased
                return _txt(lang, "credits_one") if n == 1 else _txt(lang, "credits", n=n)

            from app.modules.exams.models import Exam, Level
            from app.modules.plans.models import Plan

            plan = await self.db.get(Plan, payment.plan_id) if payment.plan_id else None

            if payment.sd_level:
                exam_name = f"Start Deutsch {payment.sd_level}"
            else:
                level = await self.db.get(Level, payment.level_id) if payment.level_id else None
                if level:
                    exam = await self.db.get(Exam, level.exam_id)
                    exam_name = (
                        f"{exam.name} - {level.cefr_code}" if exam else _txt(lang, "level", code=level.cefr_code)
                    )
                else:
                    exam_name = _txt(lang, "exam")

            # Pass journalier (paiement manuel admin, sans formule)
            if payment.duration_days:
                n = payment.duration_days
                key = "pass_one" if n == 1 else "pass"
                return _txt(lang, key, exam=exam_name, n=n)

            if plan:
                return _txt(lang, "plan", exam=exam_name, plan=plan.name, n=plan.duration_days)

            return _txt(lang, "access", exam=exam_name)
        except Exception as e:
            logger.warning(f"Description du reçu impossible pour {payment.id} : {e}")
            return _txt(lang, "fallback")

    async def _get_partner_info(self, payment: Payment) -> dict | None:
        """Infos partenaire si un code promo a été utilisé."""
        if not payment.promo_code_id:
            return None
        try:
            from app.modules.promo_codes.models import PromoCode

            promo = await self.db.get(PromoCode, payment.promo_code_id)
            if not promo:
                return None

            partner_name = "-"
            if getattr(promo, "partner_id", None):
                from app.modules.partners.models import Partner

                partner = await self.db.get(Partner, promo.partner_id)
                if partner:
                    partner_name = partner.name

            return {
                "code": promo.code,
                "partner_name": partner_name,
                "commission_due": payment.commission_due,
            }
        except Exception as e:
            logger.warning(f"Impossible de récupérer les infos partenaire : {e}")
            return None

    async def get_invoice_by_payment(self, payment_id: UUID, lang: str = "fr") -> dict:
        payment = await self.payment_repo.get_by_id_or_404(payment_id)

        customer_name = "Client"
        customer_email = ""
        user = await self.db.get(User, payment.user_id)
        if user:
            customer_name = user.full_name or user.email
            customer_email = user.email

        return {
            "transaction_reference": payment.transaction_reference,
            "payment_id": payment.id,
            "amount_gross": payment.amount_gross,
            "amount_paid": payment.amount_paid,
            "charged_amount": payment.charged_amount / 100 if payment.charged_amount else None,
            "charged_currency": payment.charged_currency,
            "discount_amount": payment.discount_amount,
            "operator": _operator_label(payment.operator, lang),
            "payment_date": payment.completed_at or payment.created_at,
            "invoice_url": getattr(payment, "invoice_url", None),
            "customer_name": customer_name,
            "customer_email": customer_email,
            "product_description": await self._get_product_description(payment, lang),
            "partner_info": await self._get_partner_info(payment),
        }