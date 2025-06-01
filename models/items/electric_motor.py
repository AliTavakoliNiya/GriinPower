import jdatetime
from sqlalchemy import cast
from sqlalchemy.types import Float

from models import Component, ComponentAttribute, ComponentType
from utils.database import SessionLocal


# تعریف کلاس نماینده موتور الکتریکی
class ElectricMotor:
    def __init__(
        self,
        power,
        rpm,
        voltage,
        start_type=None,
        cooling_method=None,
        ip_rating=None,
        efficiency_class=None,
        painting_ral=None,
        thermal_protection=None,
        space_heater=None,
        is_official=True,
        is_routine=True,
    ):
        self.power = power
        self.rpm = rpm
        self.voltage = voltage

        self.start_type = start_type
        self.cooling_method = cooling_method
        self.ip_rating = ip_rating
        self.efficiency_class = efficiency_class
        self.painting_ral = painting_ral
        self.thermal_protection = thermal_protection
        self.space_heater = space_heater

        self.is_official = is_official
        self.is_routine = is_routine

    def __repr__(self):
        return f"<ElectricMotor(power={self.power:.2f}kW, rpm={self.rpm}, voltage={self.voltage})>"


# تابع دریافت موتور از دیتابیس
def get_motor(
    power,
    rpm,
    voltage,
    start_type=None,
    cooling_method=None,
    ip_rating=None,
    efficiency_class=None,
    painting_ral=None,
    thermal_protection=None,
    space_heater=None
):
    session = SessionLocal()
    try:
        # یافتن نوع موتور
        motor_type = session.query(ComponentType).filter_by(name="Motor").first()
        if not motor_type:
            return False, "❌ 'Motor' type not found in ComponentType."

        # ایجاد query پایه
        query = session.query(Component).filter(
            Component.type_id == motor_type.id,
            cast(Component.power, Float) == float(power),
            Component.rpm == int(rpm),
            Component.voltage == int(voltage)
        )

        # افزودن فیلترهای اختیاری در صورت وجود مقدار
        optional_filters = {
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip_rating,
            "efficiency_class": efficiency_class,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "space_heater": space_heater
        }

        for key, value in optional_filters.items():
            if value is not None:
                query = query.join(ComponentAttribute).filter(
                    ComponentAttribute.key == key,
                    ComponentAttribute.value == str(value)
                )

        motor = query.first()
        if not motor:
            return False, "❌ No matching electric motor found."

        # خواندن ویژگی‌های ثبت‌شده
        attrs = {attr.key: attr.value for attr in motor.attributes}

        # ساختن شی‌ء ElectricMotor بر پایه داده‌ها
        motor_obj = ElectricMotor(
            power=power,
            rpm=rpm,
            voltage=voltage,
            start_type=attrs.get("start_type"),
            cooling_method=attrs.get("cooling_method"),
            ip_rating=attrs.get("ip_rating"),
            efficiency_class=attrs.get("efficiency_class"),
            painting_ral=attrs.get("painting_ral"),
            thermal_protection=attrs.get("thermal_protection"),
            space_heater=attrs.get("space_heater"),
            is_official=attrs.get("is_official", "True") == "True",
            is_routine=attrs.get("is_routine", "True") == "True"
        )

        return True, motor_obj

    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get_motor: {str(e)}"
    finally:
        session.close()


# تابع افزودن موتور جدید به دیتابیس
def insert_motor_to_db(
    power,
    rpm,
    voltage,
    start_type=None,
    cooling_method=None,
    ip_rating=None,
    efficiency_class=None,
    painting_ral=None,
    thermal_protection=None,
    space_heater=None,
    is_official=True,
    is_routine=True,
):
    session = SessionLocal()
    try:
        motor_type = session.query(ComponentType).filter_by(name="Motor").first()

        new_motor = Component(
            name=f"Electro Motor {int(power)}kW {rpm}rpm",
            type_id = motor_type.id,
            brand = '',
            model=None,
            order_number = "",
            created_by_id = 1,
            attributes = [
                ComponentAttribute(key='power', value=power),
                ComponentAttribute(key='rpm', value=rpm),
                ComponentAttribute(key='voltage', value=voltage),
            ]
        )
        session.add(new_motor)
        session.flush()  # برای گرفتن ID موتور جدید
        #
        # # افزودن ویژگی‌ها در صورت وجود مقدار
        # attributes = {
        #     "start_type": start_type,
        #     "cooling_method": cooling_method,
        #     "ip_rating": ip_rating,
        #     "efficiency_class": efficiency_class,
        #     "painting_ral": painting_ral,
        #     "thermal_protection": thermal_protection,
        #     "space_heater": space_heater,
        #     "is_official": str(is_official),
        #     "is_routine": str(is_routine),
        # }
        #
        # for key, value in attributes.items():
        #     if value is not None:
        #         session.add(ComponentAttribute(
        #             component_id=new_motor.id,
        #             key=key,
        #             value=str(value)
        #         ))

        session.commit()
        return True, f"✅ Motor inserted with ID: {new_motor.id}"

    except Exception as e:
        session.rollback()
        return False, f"❌ Error inserting motor: {str(e)}"
    finally:
        session.close()
