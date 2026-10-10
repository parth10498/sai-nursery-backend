from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import AdminUser, DBSession
from app.models.payment import Payment
from app.models.sale import Sale
from app.services.customer_service import CustomerService
from app.services.pdf_service import PDFGenerator
from app.services.sugarcane_service import SugarCaneService

router = APIRouter(prefix="/export", tags=["PDF Exports"])


@router.get("/customers/pdf")
async def export_customers_pdf(db: DBSession, user: AdminUser, search: Optional[str] = None):
    service = CustomerService(db)
    customers, _ = await service.list_customers(search=search, page=1, size=1000)
    data = [c.model_dump() for c in customers]
    pdf_bytes = PDFGenerator.generate_customer_list_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=customers_report.pdf"},
    )


@router.get("/customers/{customer_id}/statement/pdf")
async def export_customer_statement_pdf(customer_id: UUID, db: DBSession, user: AdminUser):
    service = CustomerService(db)
    statement = await service.get_customer_statement(customer_id)
    statement_dict = statement.model_dump()
    pdf_bytes = PDFGenerator.generate_customer_statement_pdf(statement_dict)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=statement_{customer_id}.pdf"},
    )


@router.get("/sales/{sale_id}/pdf")
async def export_sale_invoice_pdf(sale_id: UUID, db: DBSession, user: AdminUser):
    stmt = (
        select(Sale)
        .options(selectinload(Sale.customer), selectinload(Sale.sugarcane))
        .where(Sale.id == sale_id)
    )
    sale = (await db.execute(stmt)).scalar_one_or_none()
    if not sale or sale.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale invoice record not found")

    sale_dict = {
        "id": str(sale.id),
        "customer_name": sale.customer.name if sale.customer else "Valued Farmer",
        "sugarcane_name": sale.sugarcane.name if sale.sugarcane else "Sugarcane Seedlings",
        "unit_type": sale.unit_type,
        "quantity": float(sale.quantity),
        "rate": float(sale.rate),
        "total_amount": float(sale.total_amount),
        "sale_date": str(sale.sale_date),
    }
    pdf_bytes = PDFGenerator.generate_sale_invoice_pdf(sale_dict)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{sale_id}.pdf"},
    )


@router.get("/payments/{payment_id}/pdf")
async def export_payment_receipt_pdf(payment_id: UUID, db: DBSession, user: AdminUser):
    stmt = (
        select(Payment)
        .options(selectinload(Payment.customer))
        .where(Payment.id == payment_id)
    )
    payment = (await db.execute(stmt)).scalar_one_or_none()
    if not payment or payment.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment receipt record not found")

    payment_dict = {
        "id": str(payment.id),
        "customer_name": payment.customer.name if payment.customer else "-",
        "payment_date": str(payment.payment_date),
        "payment_mode": payment.payment_mode.value if hasattr(payment.payment_mode, "value") else str(payment.payment_mode),
        "receipt_no": payment.receipt_no or "-",
        "amount_paid": float(payment.amount_paid),
    }
    pdf_bytes = PDFGenerator.generate_payment_receipt_pdf(payment_dict)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{payment_id}.pdf"},
    )


@router.get("/sugarcane/pdf")
async def export_sugarcane_pdf(db: DBSession, user: AdminUser):
    service = SugarCaneService(db)
    varieties = await service.list_varieties()
    data = [v.model_dump() for v in varieties]
    pdf_bytes = PDFGenerator.generate_sugarcane_catalog_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sugarcane_catalog.pdf"},
    )
