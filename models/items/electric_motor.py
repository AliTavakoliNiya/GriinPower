from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentType
from utils.database import SessionLocal


class ElectricMotor:
    def __init__(
            self,
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
            is_official=None,
            is_routine=None,
    ):
        self.power = power
        self.rpm = rpm
        self.voltage = voltage
        self.brand = brand

        self.start_type = start_type
        self.cooling_method = cooling_method
        self.ip_rating = ip_rating
        self.efficiency_class = efficiency_class
        self.painting_ral = painting_ral
        self.thermal_protection = thermal_protection

        self.is_official = is_official
        self.is_routine = is_routine

    def __repr__(self):
        return f"<ElectricMotor(Brand={self.brand}, power={self.power:.2f}kW, rpm={self.rpm}, voltage={self.voltage})>"


def get_all_motors():
    session = SessionLocal()

    attribute_keys = [
        "power", "rpm", "voltage", "brand",
        "start_type", "cooling_method", "ip_rating", "efficiency_class",
        "painting_ral", "thermal_protection", "is_official", "is_routine"
    ]

    motors = (
        session.query(Component)
        .join(ComponentType)
        .filter(ComponentType.name == "Motor")
        .options(joinedload(Component.attributes), joinedload(Component.suppliers))
        .all()
    )

    motor_list = []
    for motor in motors:
        attr_dict = {attr.key: attr.value for attr in motor.attributes}
        for supplier in motor.suppliers:
            motor_data = {
                "id": motor.id,
                "name": motor.name,
                "brand": motor.brand,
                "model": motor.model,
                "order_number": motor.order_number,
                "created_at": str(motor.created_at),
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
            }
            for key in attribute_keys:
                motor_data[key] = attr_dict.get(key, "")
            motor_list.append(motor_data)
    return motor_list, attribute_keys


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
        is_official=None,
        is_routine=None,
):
    session = SessionLocal()
    try:
        motor_type = session.query(ComponentType).filter_by(name="Motor").first()

        query = session.query(Component).filter(Component.type_id == motor_type.id)

        query = query.filter(Component.brand == brand)

        # Apply required attributes using aliases
        required_filters = {
            "power": power,
            "rpm": rpm,
            "voltage": voltage,
        }

        for i, (key, value) in enumerate(required_filters.items()):
            attr_alias = aliased(ComponentAttribute, name=f"required_attr_{i}")
            query = query.join(attr_alias, Component.id == attr_alias.component_id)
            query = query.filter(attr_alias.key == key, attr_alias.value == str(value))

        # Fetch all candidates that match required attributes
        candidates = query.options(
            joinedload(Component.attributes)
        ).all()

        if not candidates:
            return False, "❌ No motor found matching required attributes."

        # Define optional filters
        optional_filters = {
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip_rating,
            "efficiency_class": efficiency_class,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "is_official": str(is_official) if is_official is not None else None,
            "is_routine": str(is_routine) if is_routine is not None else None
        }

        # Rank candidates by number of matching optional attributes
        def count_optional_matches(component):
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            return sum(
                1 for key, val in optional_filters.items()
                if val is not None and attr_dict.get(key) == val
            )

        best_match = max(candidates, key=count_optional_matches)
        attrs = {attr.key: attr.value for attr in best_match.attributes}

        motor_obj = ElectricMotor(
            power=power,
            rpm=rpm,
            voltage=voltage,
            brand=brand,
            start_type=attrs.get("start_type"),
            cooling_method=attrs.get("cooling_method"),
            ip_rating=attrs.get("ip_rating"),
            efficiency_class=attrs.get("efficiency_class"),
            painting_ral=attrs.get("painting_ral"),
            thermal_protection=attrs.get("thermal_protection"),
            is_official=attrs.get("is_official", "True") == "True",
            is_routine=attrs.get("is_routine", "True") == "True"
        )

        return True, motor_obj

    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get_motor: {str(e)}"
    finally:
        session.close()


def insert_motor_to_db(
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
        is_official=None,
        is_routine=None,
):
    current_user = UserSession()
    session = SessionLocal()
    try:
        motor_type = session.query(ComponentType).filter_by(name="Motor").first()

        new_motor = Component(
            name=f"Electro Motor {int(power)}kW {rpm}rpm",
            type_id=motor_type.id,
            brand=brand,
            created_by_id=current_user.id,
            attributes=[
                ComponentAttribute(key='power', value=power),
                ComponentAttribute(key='rpm', value=rpm),
                ComponentAttribute(key='voltage', value=voltage),
            ]
        )
        session.add(new_motor)
        session.flush()  # to achive new motor id

        # add optional attributes
        attributes = {
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip_rating,
            "efficiency_class": efficiency_class,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "is_official": is_official,
            "is_routine": is_routine,
        }

        for key, value in attributes.items():
            if value is not None:
                session.add(ComponentAttribute(
                    component_id=new_motor.id,
                    key=key,
                    value=str(value)
                ))

        session.commit()
        return True, new_motor.id

    except Exception as e:
        session.rollback()
        return False, f"❌ Error inserting motor: {str(e)}"
    finally:
        session.close()
