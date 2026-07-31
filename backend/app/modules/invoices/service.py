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
from reportlab.platypus import Image
import os

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
        logo_path = "storage/logo.png"  # ← place ton logo ici
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=4*cm, height=1.5*cm)
            logo.hAlign = 'LEFT'
            story.append(logo)
            story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("GoToGermany", title_style))
        story.append(Paragraph("Plateforme de préparation aux examens d'allemand", subtitle_style))
        story.append(Paragraph("Dschang, Cameroun | www.prep-telc-osd.com", subtitle_style))
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
        story.append(Paragraph("GoToGermany - ITIA Solutions", footer_style))
        story.append(Paragraph("Merci pour votre confiance !", footer_style))

        doc.build(story)

    async def _get_product_description(self, payment: Payment) -> str:
        try:
            from app.modules.exams.models import Level, Exam
            from app.modules.plans.models import Plan

            level = await self.db.get(Level, payment.level_id)
            plan = await self.db.get(Plan, payment.plan_id)

            if level:
                exam = await self.db.get(Exam, level.exam_id)
                exam_name = f"{exam.name} - {level.cefr_code}" if exam else f"Niveau {level.cefr_code}"
            else:
                exam_name = "Examen"

            plan_name = plan.name if plan else "Accès"
            duration = f"{plan.duration_days} jours" if plan else ""

            return f"{exam_name} - {plan_name} ({duration})"
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
        
    
    # ── Reçus centres de formation (module enrollments) ──────

    async def generate_invoice_for_formation_payment(self, payment_id: UUID) -> str:
        from app.modules.enrollments.repository import FormationPaymentRepository
        from app.modules.enrollments.models import LevelEnrollment, Cursus, FormationPaymentType
        from app.modules.centers.models import Branch, Center
        from app.modules.users.models import User

        payment_repo = FormationPaymentRepository(self.db)
        payment = await payment_repo.get_by_id_or_404(payment_id)

        enrollment = await self.db.get(LevelEnrollment, payment.enrollment_id)
        cursus = await self.db.get(Cursus, enrollment.cursus_id)
        branch = await self.db.get(Branch, cursus.branch_id)
        center = await self.db.get(Center, branch.center_id)
        student = await self.db.get(User, cursus.student_id)

        inscription_paid = await payment_repo.sum_paid(enrollment.id, FormationPaymentType.inscription)
        formation_paid = await payment_repo.sum_paid(enrollment.id, FormationPaymentType.formation)
        remaining = (
            max(enrollment.inscription_fee_amount - inscription_paid, 0)
            if payment.payment_type == FormationPaymentType.inscription
            else max(enrollment.formation_fee_amount - formation_paid, 0)
        )

        motif = self._build_formation_motif(payment.payment_type, enrollment.level, payment.notes)

        pdf_filename = f"{payment.invoice_number}.pdf"
        pdf_path = self.invoices_dir / pdf_filename

        self._create_formation_pdf(
            pdf_path=str(pdf_path),
            invoice_number=payment.invoice_number,
            payment_date=payment.paid_at,
            student_name=student.full_name if student else "—",
            amount=payment.amount,
            remaining=remaining,
            motif=motif,
            center_name=center.name,
            center_address=getattr(center, "address", None),
            center_logo_path=getattr(center, "logo_path", None),
        )

        invoice_url = f"/invoices/{pdf_filename}"
        await payment_repo.update(payment_id, invoice_url=invoice_url)
        return invoice_url

    def _build_formation_motif(self, payment_type, level, notes: str | None) -> str:
        """Le staff peut surcharger via `notes` ; sinon motif généré automatiquement."""
        if notes:
            return notes
        from app.modules.enrollments.models import FormationPaymentType
        label = "Frais d'inscription" if payment_type == FormationPaymentType.inscription else "Frais de formation"
        return f"{label} - Niveau {level.value}"

    def _create_formation_pdf(
        self, pdf_path: str, invoice_number: str, payment_date: datetime,
        student_name: str, amount: int, remaining: int, motif: str,
        center_name: str, center_address: str | None, center_logo_path: str | None,
    ):
        from num2words import num2words

        doc = SimpleDocTemplate(
            pdf_path, pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "FTitle", parent=styles["Heading1"], fontSize=18,
            textColor=colors.HexColor("#0d6e4f"), spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "FSubtitle", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#64748b"),
        )
        heading_style = ParagraphStyle(
            "FHeading", parent=styles["Heading2"], fontSize=13,
            textColor=colors.HexColor("#0f172a"), spaceAfter=10, alignment=1,
        )
        footer_style = ParagraphStyle(
            "FFooter", parent=styles["Normal"], fontSize=8,
            textColor=colors.HexColor("#94a3b8"), alignment=1,
        )

        story = []

        # ── En-tête : nom à gauche, logo au centre, adresse à droite ──
        left_cell = [Paragraph(center_name, title_style)]
        middle_cell = []
        if center_logo_path and os.path.exists(center_logo_path):
            logo = Image(center_logo_path, width=3 * cm, height=1.3 * cm)
            logo.hAlign = "CENTER"
            middle_cell.append(logo)
        right_cell = [Paragraph(center_address, subtitle_style)] if center_address else []

        header_table = Table(
            [[left_cell, middle_cell, right_cell]],
            colWidths=[5.5 * cm, 6 * cm, 5.5 * cm],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.6 * cm))
        story.append(Paragraph("REÇU DE PAIEMENT", heading_style))

        # ── Corps : reprend fidèlement les champs du reçu papier ──
        amount_words = num2words(amount, lang="fr").capitalize() + " francs CFA"
        rows = [
            ["N°", invoice_number],
            ["Reçu de M./Mme", student_name],
            ["La somme de", amount_words],
            ["Motif", motif],
            ["Date", payment_date.strftime("%d/%m/%Y")],
            ["Reste", f"{remaining:,} FCFA"],
        ]
        table = Table(rows, colWidths=[4 * cm, 13 * cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 2 * cm))

        # ── Signature ──
        sig_table = Table([["Signature"]], colWidths=[17 * cm])
        sig_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.HexColor("#94a3b8")),
            ("TOPPADDING", (0, 0), (-1, -1), 30),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph(f"{center_name} - via GoToGermany", footer_style))

        doc.build(story)