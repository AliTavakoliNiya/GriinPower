from models.items import Component, ComponentAttribute, ComponentType, ComponentVendor, Vendor
from utils.database import SessionLocal
from datetime import date

session = SessionLocal()


# 1. یافتن یا افزودن نوع Contactor
contactor_type = session.query(ComponentType).filter_by(name='Contactor').first()
if not contactor_type:
    contactor_type = ComponentType(name='Contactor', description='Electromagnetic contactor')
    session.add(contactor_type)
    session.commit()

# 2. یافتن یا افزودن Vendor
vendor = session.query(Vendor).filter_by(name='KalaBargh Co').first()
if not vendor:
    vendor = Vendor(name='KalaBargh Co', contact_info='021-12345678', website='https://kalabargh.example.com')
    session.add(vendor)
    session.commit()

# 3. ساخت قطعه جدید
contactor = Component(
    name='Schneider LC1D09',
    brand='Schneider Electric',
    model='LC1D09M7',
    type=contactor_type,
    attributes=[
        ComponentAttribute(key='coil_voltage', value='220V AC'),
        ComponentAttribute(key='rated_current', value='9A'),
        ComponentAttribute(key='power_cutting_kw', value='4'),
    ]
)

# 4. افزودن Vendor به قطعه
vendor_link = ComponentVendor(
    vendor=vendor,
    component=contactor,
    price=2_850_000,
    currency='IRR',
    date=date.today()
)

contactor.vendors.append(vendor_link)

# 5. ذخیره در دیتابیس
session.add(contactor)
session.commit()
session.close()
