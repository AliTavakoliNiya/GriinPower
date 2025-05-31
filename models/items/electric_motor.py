from sqlalchemy import cast
from sqlalchemy.types import Float

from models import Component, ComponentType
from models import ComponentAttribute
from utils.database import SessionLocal


class ElectricMotor:
    def __init__(
        self,
        brand,
        power,
        rpm,
        voltage,
        start_type="",
        cooling_method="",
        ip_rating="",
        efficiency_class="",
        painting_ral="",
        thermal_protection="",
        space_heater="",
        is_official=True,
        is_routine=True,
    ):
        self.brand = brand
        self.power = power
        self.rpm = rpm
        self.start_type = start_type
        self.cooling_method = cooling_method
        self.ip_rating = ip_rating
        self.efficiency_class = efficiency_class
        self.voltage = voltage
        self.painting_ral = painting_ral
        self.thermal_protection = thermal_protection
        self.space_heater = space_heater
        self.is_official = is_official # not ==> by phone call
        self.is_routine = is_routine #not ==> special

    def __repr__(self):
        return f"<ElectricMotor(brand={self.brand}, power={self.power:.2f}kW, rpm={self.rpm})>"




def get_motor(
    power,
    rpm,
    voltage,
    brand,
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
        motor_type = session.query(ComponentType).filter_by(name="Electric Motor").first()
        if not motor_type:
            return False, "❌ ComponentType 'Electric Motor' not found"

        query = session.query(Component).filter(
            Component.type_id == motor_type.id,
            Component.brand == brand,
            cast(Component.power_kw, Float) == float(power),
            Component.rpm == int(rpm),
            Component.voltage == int(voltage)
        )

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
            if value:
                query = query.join(ComponentAttribute).filter(
                    ComponentAttribute.key == key,
                    ComponentAttribute.value == str(value)
                )

        motor = query.first()
        if not motor:
            return False, "❌ No matching electric motor found."

        attrs = {attr.key: attr.value for attr in motor.attributes}
        motor_obj = ElectricMotor(
            brand=motor.brand,
            power=power,
            rpm=rpm,
            voltage=voltage,
            start_type=attrs.get("start_type", ""),
            cooling_method=attrs.get("cooling_method", ""),
            ip_rating=attrs.get("ip_rating", ""),
            efficiency_class=attrs.get("efficiency_class", ""),
            painting_ral=attrs.get("painting_ral", ""),
            thermal_protection=attrs.get("thermal_protection", ""),
            space_heater=attrs.get("space_heater", "")
        )

        return True, motor_obj

    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get_motor: {str(e)}"
    finally:
        session.close()


def insert_motor_to_db(motor: ElectricMotor):
    session = SessionLocal()
    try:
        motor_type = session.query(ComponentType).filter_by(name="Motor").first()

        new_motor = Component(
            type_id=motor_type.id,
            brand=motor.brand,
            power_kw=motor.power,
            rpm=motor.rpm,
            voltage=motor.voltage,
            is_official=motor.is_official,
            is_routine=motor.is_routine
        )
        session.add(new_motor)
        session.flush()

        optional_attrs = {
            "start_type": motor.start_type,
            "cooling_method": motor.cooling_method,
            "ip_rating": motor.ip_rating,
            "efficiency_class": motor.efficiency_class,
            "painting_ral": motor.painting_ral,
            "thermal_protection": motor.thermal_protection,
            "space_heater": motor.space_heater
        }

        for key, value in optional_attrs.items():
            if value:
                attr = ComponentAttribute(
                    component_id=new_motor.id,
                    key=key,
                    value=value
                )
                session.add(attr)

        session.commit()
        return True, f"✅ Electric motor inserted with ID: {new_motor.id}"

    except Exception as e:
        session.rollback()
        return False, f"❌ Error inserting motor: {str(e)}"

    finally:
        session.close()


