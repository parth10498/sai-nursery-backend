import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PDFGenerator:
    @staticmethod
    def _create_header(title: str):
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#0F5132'),
            alignment=1, # Center
            spaceAfter=4,
        )
        sub_style = ParagraphStyle(
            'SubHeaderStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#6B7280'),
            alignment=1,
            spaceAfter=15,
        )
        elements = [
            Paragraph("SAI NURSERY MANAGEMENT SYSTEM", header_style),
            Paragraph(f"{title} | Generated: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}", sub_style),
            Spacer(1, 10),
        ]
        return elements

    @classmethod
    def generate_customer_list_pdf(cls, customers: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
        elements = cls._create_header("CUSTOMER DIRECTORY & OUTSTANDING DUES REPORT")

        data = [["Sr.", "Farmer Name", "Mobile", "Town/Village", "Total Purchases", "Total Paid", "Balance Due"]]
        for i, c in enumerate(customers, 1):
            data.append([
                str(i),
                c.get("name", ""),
                c.get("mobile", "-"),
                c.get("city_name") or c.get("state_name") or "-",
                f"Rs. {c.get('total_sales', 0):,.2f}",
                f"Rs. {c.get('total_paid', 0):,.2f}",
                f"Rs. {c.get('balance', 0):,.2f}",
            ])

        t = Table(data, colWidths=[25, 140, 80, 85, 80, 75, 75])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAF9')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_sale_invoice_pdf(cls, sale_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = cls._create_header("OFFICIAL SALE INVOICE / RECEIPT")

        styles = getSampleStyleSheet()
        info_data = [
            [f"Invoice Ref: {sale_data.get('id', '')[:8].upper()}", f"Date: {sale_data.get('sale_date', '')}"],
            [f"Customer: {sale_data.get('customer_name', '')}", f"Variety: {sale_data.get('sugarcane_name', 'Sugarcane')}"],
        ]
        info_table = Table(info_data, colWidths=[270, 270])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111827')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        table_data = [
            ["Item / Product", "Unit", "Quantity", "Rate (Rs.)", "Total Amount (Rs.)"],
            [
                sale_data.get('sugarcane_name', 'Sugarcane Seedlings'),
                "Plants",
                f"{sale_data.get('quantity', 0):,.2f}",
                f"{sale_data.get('rate', 0):,.2f}",
                f"{sale_data.get('total_amount', 0):,.2f}",
            ],
            ["", "", "", "Grand Total:", f"Rs. {sale_data.get('total_amount', 0):,.2f}"],
        ]
        items_table = Table(table_data, colWidths=[180, 60, 90, 90, 120])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F5132')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E5E7EB')),
            ('FONTNAME', (3, 2), (4, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (3, 2), (4, 2), colors.HexColor('#D1E7DD')),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(items_table)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_payment_receipt_pdf(cls, payment_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = cls._create_header("PAYMENT VOUCHER RECEIPT")

        receipt_data = [
            ["Payment ID:", str(payment_data.get('id', ''))[:8].upper()],
            ["Customer Name:", payment_data.get('customer_name', '-')],
            ["Payment Date:", str(payment_data.get('payment_date', ''))],
            ["Payment Mode:", str(payment_data.get('payment_mode', 'Cash')).upper()],
            ["Receipt / Txn Ref:", payment_data.get('receipt_no', '-')],
            ["Amount Received:", f"Rs. {payment_data.get('amount_paid', 0):,.2f}"],
        ]
        t = Table(receipt_data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 5), (1, 5), colors.HexColor('#D1E7DD')),
            ('FONTNAME', (0, 5), (1, 5), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_sugarcane_catalog_pdf(cls, varieties: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = cls._create_header("SUGARCANE VARIETIES & RATE CARD")

        data = [["Sr.", "Variety Name", "Variety Code", "Default Rate (Rs./Plant)", "Status"]]
        for i, v in enumerate(varieties, 1):
            data.append([
                str(i),
                v.get("name", ""),
                v.get("code", "-"),
                f"Rs. {v.get('default_rate', 0):,.2f}",
                "Active" if v.get("is_active") else "Inactive",
            ])

        t = Table(data, colWidths=[30, 200, 100, 120, 90])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAF9')]),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
