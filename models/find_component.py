from models.items import Component, ComponentType, ComponentAttribute, ComponentVendor, Vendor
from sqlalchemy.orm import aliased
from sqlalchemy import cast, Float, desc, and_
from datetime import date
from utils.database import SessionLocal


session = SessionLocal()


# یافتن نوع 'Contactor'
contactor_type = session.query(ComponentType).filter_by(name='Contactor').first()
if not contactor_type:
    print("نوع Contactor یافت نشد.")
    session.close()
    exit()

# ALIAS برای attribute
rated_attr = aliased(ComponentAttribute)
vendor_link = aliased(ComponentVendor)

# استعلام کنتاکتورهایی با جریان نامی بالای 8 آمپر
components = (
    session.query(Component)
    .join(rated_attr, Component.attributes)
    .filter(
        Component.type_id == contactor_type.id,
        rated_attr.key == 'rated_current',
        cast(rated_attr.value, Float) > 8
    )
    .all()
)

# چاپ اطلاعات همراه با بروزترین قیمت و فروشنده
for c in components:
    latest_vendor = (
        session.query(ComponentVendor)
        .filter(ComponentVendor.component_id == c.id)
        .order_by(desc(ComponentVendor.date))
        .first()
    )

    print(f"🔌 قطعه: {c.name}")
    print(f"  برند: {c.brand}")
    print(f"  مدل: {c.model}")
    for attr in c.attributes:
        print(f"  ویژگی: {attr.key} = {attr.value}")

    if latest_vendor:
        v = latest_vendor.vendor
        print("  📦 قیمت و تأمین‌کننده:")
        print(f"    قیمت: {latest_vendor.price} {latest_vendor.currency}")
        print(f"    تاریخ: {latest_vendor.date}")
        print(f"    فروشنده: {v.name}")
        print(f"    تماس: {v.contact_info}")
        print(f"    وب‌سایت: {v.website}")
    else:
        print("  ⚠️ قیمت یا فروشنده‌ای برای این قطعه ثبت نشده.")

    print("-" * 50)

session.close()
