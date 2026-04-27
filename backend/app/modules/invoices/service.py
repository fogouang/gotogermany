"""
app/modules/invoices/service.py
"""
import logging
from datetime import datetime
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import get_settings
from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.shared.database.session import AsyncSession

settings = get_settings()
logger = logging.getLogger(__name__)


class InvoiceService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.invoices_dir = Path("storage/invoices")
        self.invoices_dir.mkdir(parents=True, exist_ok=True)

    async def generate_invoice_for_payment(self, payment_id: UUID) -> str:
        payment = await self.payment_repo.get_by_id_or_404(payment_id)

        # Infos client
        customer_name = "Client"
        customer_email = ""
        from app.modules.users.models import User
        user = await self.db.get(User, payment.user_id)
        if user:
            customer_name = user.full_name or user.email
            customer_email = user.email

        # Infos exam + plan
        product_description = await self._get_product_description(payment)

        # Infos partenaire (code promo)
        partner_info = await self._get_partner_info(payment)

        # Générer PDF
        pdf_filename = f"{payment.transaction_reference}.pdf"
        pdf_path = self.invoices_dir / pdf_filename

        self._create_pdf(
            pdf_path=str(pdf_path),
            transaction_reference=payment.transaction_reference,
            payment_date=payment.completed_at or payment.created_at,
            customer_name=customer_name,
            customer_email=customer_email,
            product_description=product_description,
            amount_gross=payment.amount_gross,
            amount_paid=payment.amount_paid,
            discount_amount=payment.discount_amount,
            operator=payment.operator or "Mobile Money",
            partner_info=partner_info,
        )

        invoice_url = f"/invoices/{pdf_filename}"
        await self.payment_repo.update(payment_id, invoice_url=invoice_url)
        return invoice_url

    def _create_pdf(
        self,
        pdf_path: str,
        transaction_reference: str,
        payment_date: datetime,
        customer_name: str,
        customer_email: str,
        product_description: str,
        amount_gross: int,
        amount_paid: int,
        discount_amount: int,
        operator: str,
        partner_info: dict | None,
    ):
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=colors.HexColor("#0d6e4f"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=2,
        )
        heading_style = ParagraphStyle(
            "Heading",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
        normal_style = styles["Normal"]
        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#64748b"),
        )
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#94a3b8"),
            alignment=1,
        )

        story = []

        # ── En-tête ──────────────────────────────────────
        story.append(Paragraph("GoToGermany", title_style))
        story.append(Paragraph("Plateforme de préparation aux examens d'allemand", subtitle_style))
        story.append(Paragraph("Douala, Cameroun | gotogermany.cm", subtitle_style))
        story.append(Spacer(1, 0.8 * cm))

        # ── Infos facture ─────────────────────────────────
        story.append(Paragraph(f"<b>REÇU DE PAIEMENT</b>", heading_style))
        invoice_data = [
            ["Référence :", transaction_reference],
            ["Date :", payment_date.strftime("%d/%m/%Y %H:%M")],
        ]
        invoice_table = Table(invoice_data, colWidths=[4 * cm, 13 * cm])
        invoice_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 0.6 * cm))

        # ── Client ────────────────────────────────────────
        story.append(Paragraph("<b>Facturé à :</b>", heading_style))
        story.append(Paragraph(customer_name, normal_style))
        if customer_email:
            story.append(Paragraph(customer_email, small_style))
        story.append(Spacer(1, 0.8 * cm))

        # ── Détail achat ──────────────────────────────────
        story.append(Paragraph("<b>Détail de l'achat :</b>", heading_style))

        rows = [
            ["Description", "Montant"],
            [product_description, f"{amount_gross:,} FCFA"],
        ]
        if discount_amount > 0:
            rows.append(["Réduction (code promo)", f"- {discount_amount:,} FCFA"])

        detail_table = Table(rows, colWidths=[12 * cm, 5 * cm])
        detail_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0fdfa")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            # Ligne réduction en vert
            ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#16a34a")),
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 0.3 * cm))

        # Total
        total_table = Table(
            [["TOTAL PAYÉ", f"{amount_paid:,} FCFA"]],
            colWidths=[12 * cm, 5 * cm]
        )
        total_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 13),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0d6e4f")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor("#0d6e4f")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 0.8 * cm))

        # ── Infos paiement ────────────────────────────────
        story.append(Paragraph("<b>Informations de paiement :</b>", heading_style))
        pay_data = [
            ["Méthode :", operator],
            ["Statut :", "✓ Payé"],
        ]
        pay_table = Table(pay_data, colWidths=[4 * cm, 13 * cm])
        pay_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#16a34a")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(pay_table)

        # ── Partenaire (si code promo utilisé) ───────────
        if partner_info:
            story.append(Spacer(1, 0.6 * cm))
            story.append(Paragraph("<b>Code partenaire utilisé :</b>", heading_style))
            partner_data = [
                ["Code :", partner_info.get("code", "—")],
                ["Partenaire :", partner_info.get("partner_name", "—")],
                ["Commission :", f"{partner_info.get('commission_due', 0):,.0f} FCFA"],
            ]
            partner_table = Table(partner_data, colWidths=[4 * cm, 13 * cm])
            partner_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(partner_table)

        # ── Footer ────────────────────────────────────────
        story.append(Spacer(1, 1.5 * cm))
        story.append(Paragraph("GoToGermany — ITIA Solutions", footer_style))
        story.append(Paragraph("Merci pour votre confiance !", footer_style))

        doc.build(story)

    async def _get_product_description(self, payment: Payment) -> str:
        """Description : Accès à l'exam + durée du plan."""
        try:
            from app.modules.exams.models import Exam
            from app.modules.plans.models import Plan

            exam = await self.db.get(Exam, payment.exam_id)
            plan = await self.db.get(Plan, payment.plan_id)

            exam_name = exam.name if exam else "Examen"
            plan_name = plan.name if plan else "Accès"
            duration = f"{plan.duration_days} jours" if plan else ""

            return f"{exam_name} — {plan_name} ({duration})"
        except Exception:
            return "Accès examen GoToGermany"

    async def _get_partner_info(self, payment: Payment) -> dict | None:
        """Infos partenaire si code promo utilisé."""
        if not payment.promo_code_id:
            return None
        try:
            from app.modules.promo_codes.models import PromoCode
            promo = await self.db.get(PromoCode, payment.promo_code_id)
            if not promo:
                return None

            partner_name = "—"
            # Récupérer le nom du partenaire via le promo code
            if hasattr(promo, "partner_id") and promo.partner_id:
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
            logger.warning(f"Impossible de récupérer infos partenaire: {e}")
            return None

    async def get_invoice_by_payment(self, payment_id: UUID) -> dict:
        payment = await self.payment_repo.get_by_id_or_404(payment_id)

        customer_name = "Client"
        customer_email = ""
        from app.modules.users.models import User
        user = await self.db.get(User, payment.user_id)
        if user:
            customer_name = user.full_name or user.email
            customer_email = user.email

        product_description = await self._get_product_description(payment)
        partner_info = await self._get_partner_info(payment)

        return {
            "transaction_reference": payment.transaction_reference,
            "payment_id": payment.id,
            "amount_gross": payment.amount_gross,
            "amount_paid": payment.amount_paid,
            "discount_amount": payment.discount_amount,
            "operator": payment.operator,
            "payment_date": payment.completed_at or payment.created_at,
            "invoice_url": getattr(payment, "invoice_url", None),
            "customer_name": customer_name,
            "customer_email": customer_email,
            "product_description": product_description,
            "partner_info": partner_info,
        }