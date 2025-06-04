from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from models import Component, ComponentSupplier
from utils.database import SessionLocal

class Calibration:
    def __init__(self, brand, model, calibration_date, calibration_due_date, calibration_lab, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.calibration_date = calibration_date              # تاریخ انجام کالیبراسیون
        self.calibration_due_date = calibration_due_date      # تاریخ انقضا یا موعد بعدی کالیبراسیون
        self.calibration_lab = calibration_lab                # آزمایشگاه یا مرکز کالیبراسیون
        self.order_number = order_number
        self.component_supplier = component_supplier              # نمونه مشابه برای ارتباط با تامین‌کننده یا نسخه قطعه

    def __repr__(self):
        return f"<Calibration(model={self.model} calibration_date={self.calibration_date})>"


def get_calibration(model=None):
    session = SessionLocal()
    try:
        calibration_type = session.query(ComponentType).filter_by(name='Calibration').first()
        query = session.query(Component).filter(Component.type_id == calibration_type.id)

        if model:
            query = query.filter(Component.model == model)

        component = query.first()
        if not component:
            return None, "❌ Calibration not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        calibration = Calibration(
            brand=component.brand,
            model=component.model,
            calibration_date=attrs.get("calibration_date"),
            calibration_due_date=attrs.get("calibration_due_date"),
            calibration_lab=attrs.get("calibration_lab"),
            component_supplier=latest_supplier
        )
        return True, calibration

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Calibration:\n{str(e)}"
    finally:
        session.close()
