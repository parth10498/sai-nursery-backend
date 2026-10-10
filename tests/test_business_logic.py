from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.schemas.auth import LoginRequest
from app.schemas.customer import CustomerCreate, CustomerSettleRequest, CustomerStatementResponse
from app.schemas.payment import PaymentCreate, PaymentModeEnum
from app.schemas.sale import SaleCreate
from app.schemas.sugar_cane import SugarCaneCreate


# ------------------ Customer Validations ------------------

def test_customer_valid_creation():
    customer = CustomerCreate(
        name="  Ramesh Patil  ",
        mobile="+91 98220 12345",
        pincode="416416",
        is_active=True,
    )
    assert customer.name == "Ramesh Patil"
    assert customer.mobile == "9822012345"
    assert customer.pincode == "416416"


def test_customer_name_too_short():
    with pytest.raises(ValueError, match="at least 2 characters"):
        CustomerCreate(name="A", mobile="9822012345")


def test_customer_invalid_mobile():
    # Less than 10 digits
    with pytest.raises(ValueError, match="valid 10-digit Indian phone number"):
        CustomerCreate(name="Ramesh Patil", mobile="98220123")

    # Invalid starting digit (e.g., starts with 1)
    with pytest.raises(ValueError, match="valid 10-digit Indian phone number"):
        CustomerCreate(name="Ramesh Patil", mobile="1234567890")


def test_customer_invalid_pincode():
    with pytest.raises(ValueError, match="exactly 6 digits"):
        CustomerCreate(name="Ramesh Patil", pincode="4164")


# ------------------ Sale Validations ------------------

def test_sale_total_calculation():
    qty = Decimal("1000")
    rate = Decimal("2.50")
    total = qty * rate
    assert total == Decimal("2500.00")


def test_sale_schema_future_date_invalid():
    future_date = date.today() + timedelta(days=2)
    with pytest.raises(ValueError, match="future"):
        SaleCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            quantity=Decimal("500"),
            rate=Decimal("3.00"),
            sale_date=future_date,
        )


def test_sale_schema_too_old_date_invalid():
    old_date = date(1999, 12, 31)
    with pytest.raises(ValueError, match="earlier than 01-Jan-2000"):
        SaleCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            quantity=Decimal("500"),
            rate=Decimal("3.00"),
            sale_date=old_date,
        )


def test_sale_with_unit_type():
    sale_tons = SaleCreate(
        user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        unit_type="tons",
        quantity=Decimal("25.50"),
        rate=Decimal("3200.00"),
        sale_date=date.today(),
    )
    assert sale_tons.unit_type == "TONS"
    assert sale_tons.quantity * sale_tons.rate == Decimal("81600.00")

    sale_qty = SaleCreate(
        user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        unit_type="qty",
        quantity=Decimal("15000"),
        rate=Decimal("2.50"),
        sale_date=date.today(),
    )
    assert sale_qty.unit_type == "QTY"
    assert sale_qty.quantity * sale_qty.rate == Decimal("37500.00")


def test_sale_invalid_unit_type():
    with pytest.raises(ValueError, match="either 'QTY' .* or 'TONS'"):
        SaleCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            unit_type="KILOS",
            quantity=Decimal("100"),
            rate=Decimal("2.50"),
            sale_date=date.today(),
        )


def test_sale_decimal_precision():
    with pytest.raises(ValueError, match="cannot have more than 2 decimal places"):
        SaleCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            quantity=Decimal("100.123"),
            rate=Decimal("2.50"),
            sale_date=date.today(),
        )


# ------------------ Payment Validations ------------------

def test_payment_valid_creation():
    payment = PaymentCreate(
        user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        amount_paid=Decimal("5000.50"),
        payment_date=date.today(),
        payment_mode="upi",
        receipt_no="  REC-101  ",
    )
    assert payment.amount_paid == Decimal("5000.50")
    assert payment.payment_mode == PaymentModeEnum.ONLINE
    assert payment.receipt_no == "REC-101"


def test_payment_future_date_invalid():
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(ValueError, match="future"):
        PaymentCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            amount_paid=Decimal("1000.00"),
            payment_date=future_date,
        )


def test_payment_negative_amount_invalid():
    with pytest.raises(ValueError):
        PaymentCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            amount_paid=Decimal("-100.00"),
            payment_date=date.today(),
        )


# ------------------ Sugarcane Validations ------------------

def test_sugarcane_valid_creation():
    sc = SugarCaneCreate(
        name="  Co 86032 (Nira)  ",
        code="co-86032",
        default_rate=Decimal("2.50"),
    )
    assert sc.name == "Co 86032 (Nira)"
    assert sc.code == "CO-86032"


def test_sugarcane_negative_rate_invalid():
    with pytest.raises(ValueError):
        SugarCaneCreate(
            name="Co 86032",
            default_rate=Decimal("-1.00"),
        )


def test_sugarcane_detail_response_schema():
    from datetime import datetime
    import uuid
    from app.schemas.sugar_cane import SugarCaneDetailResponse

    detail = SugarCaneDetailResponse(
        id=uuid.uuid4(),
        name="Co 86032 (Nira)",
        code="CO-86032",
        default_rate=Decimal("2.50"),
        is_active=True,
        created_at=datetime.now(),
        total_orders=15,
        total_revenue=Decimal("125000.00"),
        total_plants_qty=Decimal("50000"),
        total_tons_weight=Decimal("0.00"),
        unique_customers_count=8,
    )
    assert detail.total_orders == 15
    assert detail.total_revenue == Decimal("125000.00")
    assert detail.unique_customers_count == 8


# ------------------ Auth Validations ------------------

def test_login_request_validation():
    req = LoginRequest(username="  nurserysai@yopmail.com  ", password="Password123")
    assert req.username == "nurserysai@yopmail.com"

    with pytest.raises(ValueError):
        LoginRequest(username="ab", password="Password123")

    with pytest.raises(ValueError):
        LoginRequest(username="admin", password="12")


# ------------------ Settlement Validations ------------------

def test_customer_settle_full_request():
    req = CustomerSettleRequest(settle_full=True, payment_mode=PaymentModeEnum.ONLINE, notes="Cleared on harvest")
    assert req.settle_full is True
    assert req.amount is None
    assert req.payment_mode == PaymentModeEnum.ONLINE


def test_customer_settle_partial_amount_request():
    req = CustomerSettleRequest(amount=Decimal("15000.00"), payment_mode=PaymentModeEnum.CASH)
    assert req.amount == Decimal("15000.00")
    assert req.settle_full is False


def test_customer_settle_future_date_invalid():
    future = date.today() + timedelta(days=2)
    with pytest.raises(ValueError, match="future"):
        CustomerSettleRequest(amount=Decimal("5000.00"), payment_date=future)

