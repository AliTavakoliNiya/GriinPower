from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from models import Component, ComponentType, ComponentVendor
from utils.database import SessionLocal

class Calibration:
    def __init__(self, name, brand, model, calibration_date, calibration_due_date, calibration_lab, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.calibration_date = calibration_date              # تاریخ انجام کالیبراسیون
        self.calibration_due_date = calibration_due_date      # تاریخ انقضا یا موعد بعدی کالیبراسیون
        self.calibration_lab = calibration_lab                # آزمایشگاه یا مرکز کالیبراسیون
        self.order_number = order_number
        self.component_vendor = component_vendor              # نمونه مشابه برای ارتباط با تامین‌کننده یا نسخه قطعه

    def __repr__(self):
        return f"<Calibration(name={self.name} model={self.model} calibration_date={self.calibration_date})>"


def get_calibration(name=None, model=None):
    session = SessionLocal()
    try:
        calibration_type = session.query(ComponentType).filter_by(name='Calibration').first()
        query = session.query(Component).filter(Component.type_id == calibration_type.id)

        if name:
            query = query.filter(Component.name == name)
        if model:
            query = query.filter(Component.model == model)

        component = query.first()
        if not component:
            return None, "❌ Calibration not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        calibration = Calibration(
            name=component.name,
            brand=component.brand,
            model=component.model,
            calibration_date=attrs.get("calibration_date"),
            calibration_due_date=attrs.get("calibration_due_date"),
            calibration_lab=attrs.get("calibration_lab"),
            component_vendor=latest_vendor
        )
        return True, calibration

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Calibration:\n{str(e)}"
    finally:
        session.close()
