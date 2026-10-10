import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.sugar_cane import SugarCane

SUGARCANE_VARIETIES = [
    # B (Bihar)
    {
        "name": "BO 70",
        "code": "BO-70",
        "default_rate": Decimal("2.50"),
        "description": "Bihar regional series sugarcane variety",
    },
    {
        "name": "BO 91",
        "code": "BO-91",
        "default_rate": Decimal("2.60"),
        "description": "Bihar regional high yield sugarcane variety",
    },
    {
        "name": "BO 128",
        "code": "BO-128",
        "default_rate": Decimal("2.70"),
        "description": "Bihar series mid-late maturing variety",
    },
    {
        "name": "BO 130",
        "code": "BO-130",
        "default_rate": Decimal("2.80"),
        "description": "Bihar regional improved sugarcane variety",
    },

    # C (Coimbatore series and regional codes)
    {
        "name": "Co 205",
        "code": "CO-205",
        "default_rate": Decimal("2.40"),
        "description": "Historic landmark Coimbatore interspecific hybrid variety",
    },
    {
        "name": "Co 213",
        "code": "CO-213",
        "default_rate": Decimal("2.40"),
        "description": "Historic Coimbatore commercial hybrid cane",
    },
    {
        "name": "Co 312",
        "code": "CO-312",
        "default_rate": Decimal("2.50"),
        "description": "Subtropical commercial variety with excellent tillering",
    },
    {
        "name": "Co 419",
        "code": "CO-419",
        "default_rate": Decimal("2.60"),
        "description": "Historic wonder cane of Peninsular and South India",
    },
    {
        "name": "Co 527",
        "code": "CO-527",
        "default_rate": Decimal("2.50"),
        "description": "Mid-late maturing Coimbatore series commercial variety",
    },
    {
        "name": "Co 740",
        "code": "CO-740",
        "default_rate": Decimal("2.80"),
        "description": "Heavy yielding variety with exceptional ratoonability in Maharashtra",
    },
    {
        "name": "Co 997",
        "code": "CO-997",
        "default_rate": Decimal("2.70"),
        "description": "Early maturing high sucrose sugarcane variety",
    },
    {
        "name": "Co 1148",
        "code": "CO-1148",
        "default_rate": Decimal("2.60"),
        "description": "Hardy subtropical commercial cane widely grown across North India",
    },
    {
        "name": "Co 6304",
        "code": "CO-6304",
        "default_rate": Decimal("2.80"),
        "description": "High yielding tropical variety popular in Tamil Nadu",
    },
    {
        "name": "Co 7219 (Sanjivani)",
        "code": "CO-7219",
        "default_rate": Decimal("2.90"),
        "description": "Early to mid-late maturing variety with high juice quality (Sanjivani)",
    },
    {
        "name": "Co 8201",
        "code": "CO-8201",
        "default_rate": Decimal("2.70"),
        "description": "Peninsular zone commercial variety with good ratoon performance",
    },
    {
        "name": "Co 8371",
        "code": "CO-8371",
        "default_rate": Decimal("2.80"),
        "description": "Mid-late maturing variety with robust cane stalks",
    },
    {
        "name": "Co 62175",
        "code": "CO-62175",
        "default_rate": Decimal("2.70"),
        "description": "Peninsular zone high sugar cane variety",
    },
    {
        "name": "Co 85004",
        "code": "CO-85004",
        "default_rate": Decimal("2.90"),
        "description": "Early maturing high sugar commercial cultivar",
    },
    {
        "name": "Co 86032 (Nira)",
        "code": "CO-86032",
        "default_rate": Decimal("2.50"),
        "description": "Premier widely planted commercial variety in Maharashtra and South India",
    },
    {
        "name": "Co 86249",
        "code": "CO-86249",
        "default_rate": Decimal("2.70"),
        "description": "Commercial peninsular cane with good pest and disease tolerance",
    },
    {
        "name": "Co 87025",
        "code": "CO-87025",
        "default_rate": Decimal("2.80"),
        "description": "Early maturing variety with high sucrose content",
    },
    {
        "name": "Co 89003",
        "code": "CO-89003",
        "default_rate": Decimal("2.90"),
        "description": "Early maturing high brix sugarcane variety",
    },
    {
        "name": "Co 94008 (Shyama)",
        "code": "CO-94008",
        "default_rate": Decimal("2.90"),
        "description": "Peninsular zone high tonnage variety (Shyama)",
    },
    {
        "name": "Co 94012 (Phule Savitri)",
        "code": "CO-94012",
        "default_rate": Decimal("3.00"),
        "description": "Early high sugar variety recommended for Maharashtra (Phule Savitri)",
    },
    {
        "name": "Co 97009",
        "code": "CO-97009",
        "default_rate": Decimal("2.80"),
        "description": "Mid-late maturing high yielding commercial variety",
    },
    {
        "name": "Co 99004",
        "code": "CO-99004",
        "default_rate": Decimal("2.90"),
        "description": "High biomass cane with good ratooning capability",
    },
    {
        "name": "Co 0118 (Karan 2)",
        "code": "CO-0118",
        "default_rate": Decimal("3.20"),
        "description": "Early maturing high sugar subtropical variety released by ICAR-SBI",
    },
    {
        "name": "Co 0212",
        "code": "CO-0212",
        "default_rate": Decimal("2.80"),
        "description": "Subtropical commercial variety with high tillering",
    },
    {
        "name": "Co 0232",
        "code": "CO-0232",
        "default_rate": Decimal("2.90"),
        "description": "Subtropical variety tolerant to waterlogged and flooding conditions",
    },
    {
        "name": "Co 0238 (Karan 4)",
        "code": "CO-0238",
        "default_rate": Decimal("3.20"),
        "description": "High-yield high-sucrose landmark cultivar of North India",
    },
    {
        "name": "Co 0239 (Karan 6)",
        "code": "CO-0239",
        "default_rate": Decimal("3.10"),
        "description": "Subtropical early maturing variety with high juice quality",
    },
    {
        "name": "Co 0403",
        "code": "CO-0403",
        "default_rate": Decimal("2.90"),
        "description": "Mid-late maturing variety suitable for peninsular regions",
    },
    {
        "name": "Co 15023",
        "code": "CO-15023",
        "default_rate": Decimal("3.50"),
        "description": "High sugar early maturing variety with exceptional recovery rate",
    },
    {
        "name": "CoA 92081",
        "code": "COA-92081",
        "default_rate": Decimal("2.80"),
        "description": "Andhra Pradesh regional high yielding variety",
    },
    {
        "name": "CoC 671",
        "code": "COC-671",
        "default_rate": Decimal("3.00"),
        "description": "Tamil Nadu rich sweet early maturing cane variety",
    },
    {
        "name": "CoC 85061",
        "code": "COC-85061",
        "default_rate": Decimal("2.80"),
        "description": "Tamil Nadu mid-late maturing commercial variety",
    },
    {
        "name": "CoG 93076",
        "code": "COG-93076",
        "default_rate": Decimal("2.80"),
        "description": "Gujarat regional commercial sugarcane variety",
    },
    {
        "name": "CoH 56",
        "code": "COH-56",
        "default_rate": Decimal("2.70"),
        "description": "Haryana regional sugarcane variety",
    },
    {
        "name": "CoH 119",
        "code": "COH-119",
        "default_rate": Decimal("2.80"),
        "description": "Haryana mid-late commercial variety with high tillering",
    },
    {
        "name": "CoH 160",
        "code": "COH-160",
        "default_rate": Decimal("3.00"),
        "description": "Haryana early maturing high sugar variety",
    },
    {
        "name": "CoJ 64",
        "code": "COJ-64",
        "default_rate": Decimal("2.90"),
        "description": "Punjab and Haryana early maturing benchmark variety",
    },
    {
        "name": "CoJ 85",
        "code": "COJ-85",
        "default_rate": Decimal("2.80"),
        "description": "Punjab and Haryana early commercial variety",
    },
    {
        "name": "CoJ 88",
        "code": "COJ-88",
        "default_rate": Decimal("2.80"),
        "description": "Punjab and Haryana mid-late maturing variety",
    },
    {
        "name": "CoLk 8102",
        "code": "COLK-8102",
        "default_rate": Decimal("2.90"),
        "description": "IISR Lucknow Uttar Pradesh regional variety",
    },
    {
        "name": "CoLk 94184 (Birendra)",
        "code": "COLK-94184",
        "default_rate": Decimal("3.00"),
        "description": "IISR Lucknow variety tolerant to waterlogged conditions",
    },
    {
        "name": "CoM 0265",
        "code": "COM-0265",
        "default_rate": Decimal("3.00"),
        "description": "Maharashtra high biomass, drought and salinity tolerant variety",
    },
    {
        "name": "CoN 5071",
        "code": "CON-5071",
        "default_rate": Decimal("2.80"),
        "description": "Navsari Gujarat regional sugarcane variety",
    },
    {
        "name": "CoPant 84212",
        "code": "COPANT-84212",
        "default_rate": Decimal("2.80"),
        "description": "Pantnagar Uttarakhand subtropical variety",
    },
    {
        "name": "CoPb 91",
        "code": "COPB-91",
        "default_rate": Decimal("2.90"),
        "description": "Punjab regional commercial sugarcane variety",
    },
    {
        "name": "CoPK 05191",
        "code": "COPK-05191",
        "default_rate": Decimal("3.00"),
        "description": "Punjab regional improved sugarcane variety",
    },
    {
        "name": "CoS 767",
        "code": "COS-767",
        "default_rate": Decimal("2.60"),
        "description": "Shahjahanpur Uttar Pradesh mid-late hardy variety",
    },
    {
        "name": "CoS 8436",
        "code": "COS-8436",
        "default_rate": Decimal("2.80"),
        "description": "Shahjahanpur Uttar Pradesh early maturing variety",
    },
    {
        "name": "CoS 88230",
        "code": "COS-88230",
        "default_rate": Decimal("2.80"),
        "description": "Shahjahanpur Uttar Pradesh commercial sugarcane",
    },
    {
        "name": "CoS 95255",
        "code": "COS-95255",
        "default_rate": Decimal("2.90"),
        "description": "Shahjahanpur Uttar Pradesh early maturing high sugar variety",
    },
    {
        "name": "CoS 96268",
        "code": "COS-96268",
        "default_rate": Decimal("2.90"),
        "description": "Shahjahanpur Uttar Pradesh high sucrose commercial variety",
    },
    {
        "name": "CoS 97264",
        "code": "COS-97264",
        "default_rate": Decimal("2.80"),
        "description": "Shahjahanpur Uttar Pradesh commercial variety",
    },
    {
        "name": "CoSe 92423",
        "code": "COSE-92423",
        "default_rate": Decimal("2.80"),
        "description": "Shahjahanpur / Seorahi Eastern UP commercial variety",
    },
    {
        "name": "CoSe 95422",
        "code": "COSE-95422",
        "default_rate": Decimal("2.80"),
        "description": "Shahjahanpur / Seorahi Eastern UP high yield variety",
    },
    {
        "name": "CoSe 01434",
        "code": "COSE-01434",
        "default_rate": Decimal("2.90"),
        "description": "Shahjahanpur / Seorahi Eastern UP improved sugarcane variety",
    },
    {
        "name": "CoT 8201",
        "code": "COT-8201",
        "default_rate": Decimal("2.80"),
        "description": "Andhra Pradesh regional release commercial variety",
    },
    {
        "name": "CoV 92102",
        "code": "COV-92102",
        "default_rate": Decimal("2.90"),
        "description": "Maharashtra regional sugarcane variety",
    },

    # D
    {
        "name": "Dhaulu",
        "code": "DHAULU",
        "default_rate": Decimal("2.50"),
        "description": "Traditional North Indian indigenous cane (Saccharum barberi)",
    },

    # K
    {
        "name": "Kansar",
        "code": "KANSAR",
        "default_rate": Decimal("2.50"),
        "description": "Traditional indigenous Indian variety",
    },
    {
        "name": "Katha",
        "code": "KATHA",
        "default_rate": Decimal("2.50"),
        "description": "Traditional indigenous North Indian hardy cane (Saccharum barberi)",
    },

    # M
    {
        "name": "MS 68/47",
        "code": "MS-68-47",
        "default_rate": Decimal("3.00"),
        "description": "Maharashtra agricultural research station variety",
    },

    # N
    {
        "name": "Nargori",
        "code": "NARGORI",
        "default_rate": Decimal("2.50"),
        "description": "Traditional indigenous North Indian cane (Saccharum barberi)",
    },

    # P
    {
        "name": "Pansahi",
        "code": "PANSAHI",
        "default_rate": Decimal("2.60"),
        "description": "Traditional indigenous Indian cane (Saccharum sinense)",
    },
    {
        "name": "Phule 265",
        "code": "PHULE-265",
        "default_rate": Decimal("3.00"),
        "description": "Widely planted commercial cultivar in Maharashtra (same as CoM 0265)",
    },
    {
        "name": "Pundia",
        "code": "PUNDIA",
        "default_rate": Decimal("3.20"),
        "description": "Traditional indigenous thick chewing cane of Maharashtra and Karnataka",
    },

    # S
    {
        "name": "Saretha",
        "code": "SARETHA",
        "default_rate": Decimal("2.50"),
        "description": "Traditional indigenous Indian cane (Saccharum barberi)",
    },
    {
        "name": "Sunnabile",
        "code": "SUNNABILE",
        "default_rate": Decimal("2.50"),
        "description": "Traditional indigenous Indian cane (Saccharum barberi)",
    },

    # V
    {
        "name": "VSI 434",
        "code": "VSI-434",
        "default_rate": Decimal("3.20"),
        "description": "Vasantdada Sugar Institute early maturing high sugar variety (Maharashtra)",
    },
    {
        "name": "VSI 08005",
        "code": "VSI-08005",
        "default_rate": Decimal("3.30"),
        "description": "Vasantdada Sugar Institute (VSI 8005) high yielding variety (Maharashtra)",
    },
]


async def seed_sugarcane():
    async with AsyncSessionFactory() as session:
        seeded_count = 0
        updated_count = 0

        for item in SUGARCANE_VARIETIES:
            res = await session.execute(
                select(SugarCane).where(
                    (SugarCane.code == item["code"]) | (SugarCane.name == item["name"])
                )
            )
            existing = res.scalar_one_or_none()
            if not existing:
                sc = SugarCane(
                    name=item["name"],
                    code=item["code"],
                    default_rate=item["default_rate"],
                    description=item.get("description"),
                    is_active=True,
                )
                session.add(sc)
                seeded_count += 1
            else:
                existing.name = item["name"]
                existing.code = item["code"]
                existing.default_rate = item["default_rate"]
                existing.description = item.get("description")
                existing.is_active = True
                updated_count += 1

        await session.commit()
        print(f"Sugarcane varieties seeded: {seeded_count} added, {updated_count} updated. Total: {len(SUGARCANE_VARIETIES)}")


if __name__ == "__main__":
    asyncio.run(seed_sugarcane())
