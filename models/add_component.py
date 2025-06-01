from models import Component, ComponentAttribute, ComponentType, ComponentSupplier, Supplier
from utils.database import SessionLocal
from datetime import date

session = SessionLocal()


# 1. یافتن یا افزودن نوع Contactor
contactor_type = session.query(ComponentType).filter_by(name='Contactor').first()
if not contactor_type:
    contactor_type = ComponentType(name='Contactor', description='Electromagnetic contactor')
    session.add(contactor_type)
    session.commit()

# 2. یافتن یا افزودن Supplier
supplier = session.query(Supplier).filter_by(name='KalaBargh Co').first()
if not supplier:
    supplier = Supplier(name='KalaBargh Co', contact_info='021-12345678', website='https://kalabargh.example.com')
    session.add(supplier)
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

# 4. افزودن Supplier به قطعه
supplier_link = ComponentSupplier(
    supplier=supplier,
    component=contactor,
    price=2_850_000,
    currency='IRR',
    date=date.today()
)

contactor.suppliers.append(supplier_link)

# 5. ذخیره در دیتابیس
session.add(contactor)
session.commit()
session.close()
