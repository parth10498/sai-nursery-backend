from decimal import Decimal
import pytest
from app.schemas.customer import CustomerCreate
from app.schemas.sale import SaleCreate


def test_sale_total_calculation():
    qty = Decimal("1000")
    rate = Decimal("2.50")
    total = qty * rate
    assert total == Decimal("2500.00")


def test_customer_schema_validation():
    customer = CustomerCreate(
        name="Ramesh Patil",
        mobile="9822012345",
        is_active=True,
    )
    assert customer.name == "Ramesh Patil"
    assert customer.mobile == "9822012345"


def test_sale_schema_future_date_invalid():
    from datetime import date, timedelta
    future_date = date.today() + timedelta(days=2)
    with pytest.raises(ValueError):
        SaleCreate(
            user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            quantity=Decimal("500"),
            rate=Decimal("3.00"),
            sale_date=future_date,
        )


def test_sale_with_unit_type():
    from datetime import date
    sale_tons = SaleCreate(
        user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        unit_type="TONS",
        quantity=Decimal("25.50"),
        rate=Decimal("3200.00"),
        sale_date=date.today(),
    )
    assert sale_tons.unit_type == "TONS"
    assert sale_tons.quantity * sale_tons.rate == Decimal("81600.00")

    sale_qty = SaleCreate(
        user_id="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        unit_type="QTY",
        quantity=Decimal("15000"),
        rate=Decimal("2.50"),
        sale_date=date.today(),
    )
    assert sale_qty.unit_type == "QTY"
    assert sale_qty.quantity * sale_qty.rate == Decimal("37500.00")


def test_sales_analytics_response_schema():
    from app.schemas.dashboard import SalesAnalyticsResponse, MonthlyVolumeTrend, VarietySalesBreakdown

    analytics = SalesAnalyticsResponse(
        total_plants_qty=Decimal("145000"),
        total_tons_weight=Decimal("485.50"),
        total_plants_amount=Decimal("362500.00"),
        total_tons_amount=Decimal("1553600.00"),
        monthly_trends=[
            MonthlyVolumeTrend(
                month="Dec 25",
                plants_qty=Decimal("42000"),
                tons_weight=Decimal("130.0"),
                total_amount=Decimal("521000.00"),
            )
        ],
        variety_breakdown=[
            VarietySalesBreakdown(
                variety_name="Co 86032 (Nira)",
                plants_qty=Decimal("78500"),
                tons_weight=Decimal("262.2"),
                total_amount=Decimal("1035290.00"),
                percentage=54.0,
            )
        ],
    )
    assert analytics.total_plants_qty == Decimal("145000")
    assert analytics.total_tons_weight == Decimal("485.50")
    assert len(analytics.monthly_trends) == 1
    assert len(analytics.variety_breakdown) == 1

