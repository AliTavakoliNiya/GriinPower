

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentVendor, ComponentType
from utils.database import SessionLocal


class ElectricMotor:
    def __init__(
        self,
        name,
        brand,
        model,
        power,
        rpm,
        start_type,
        cooling_method,
        ip_rating,
        efficiency_class,
        voltage,
        painting_ral,
        thermal_protection,
        space_heater,
        component_vendor,
        order_number="",
    ):
        self.name = name
        self.brand = brand
        self.model = model
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
        self.component_vendor = component_vendor
        self.order_number = order_number

    def __repr__(self):
        return f"<ElectricMotor(name={self.name}, power={self.power}kW, rpm={self.rpm})>"


def get_motor_by_power(power, rpm, start_type, cooling_method, ip,
                       efficiency_class, voltage, painting_ral,
                       thermal_protection, space_heater):
    session = SessionLocal()
    try:
        motor_type = session.query(ComponentType).filter_by(name='Electric Motor').first()
        if not motor_type:
            return False, "❌ Electric Motor type not found."

        query = session.query(Component).filter(Component.type_id == motor_type.id)

        # Join all attributes
        attributes = {
            "power": power,
            "rpm": rpm,
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip,
            "efficiency_class": efficiency_class,
            "voltage": voltage,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "space_heater": space_heater
        }

        for key, val in attributes.items():
            query = query.join(Component.attributes).filter(
                Component.attributes.any(key=key, value=str(val))
            )

        component = query.first()
        if not component:
            return False, "❌ Matching Electric Motor not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attr_dict = {attr.key: attr.value for attr in component.attributes}

        motor = ElectricMotor(
            name=component.name,
            brand=component.brand,
            model=component.model,
            power=attr_dict.get("power"),
            rpm=attr_dict.get("rpm"),
            start_type=attr_dict.get("start_type"),
            cooling_method=attr_dict.get("cooling_method"),
            ip_rating=attr_dict.get("ip_rating"),
            efficiency_class=attr_dict.get("efficiency_class"),
            voltage=attr_dict.get("voltage"),
            painting_ral=attr_dict.get("painting_ral"),
            thermal_protection=attr_dict.get("thermal_protection"),
            space_heater=attr_dict.get("space_heater"),
            component_vendor=latest_vendor
        )

        return True, motor

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_motor_by_power:\n{str(e)}"
    finally:
        session.close()
