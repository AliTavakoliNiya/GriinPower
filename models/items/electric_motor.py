from sqlalchemy import cast
from sqlalchemy.orm import joinedload
from sqlalchemy.types import Float

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


def get_all_motor():
    session = SessionLocal()
    motors = []
    try:
        motor_type = session.query(ComponentType).filter(ComponentType.name == 'Motor').first()
        if not motor_type:
            return []

        components = session.query(Component)\
            .filter(Component.type_id == motor_type.id)\
            .options(joinedload(Component.attributes))\
            .all()

        for comp in components:
            attr_dict = {attr.key: attr.value for attr in comp.attributes}

            def get_attr(name):
                return attr_dict.get(name)

            def to_float(val):
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return None

            def to_int(val):
                try:
                    return int(val)
                except (TypeError, ValueError):
                    return None

            motor = ElectricMotor(
                power=to_float(get_attr('power')) or 0.0,
                rpm=to_int(get_attr('rpm')) or 0,
                voltage=to_int(get_attr('voltage')) or 0,
                brand=comp.brand or '',
                start_type=get_attr('start_type'),
                cooling_method=get_attr('cooling_method'),
                ip_rating=get_attr('ip_rating'),
                efficiency_class=get_attr('efficiency_class'),
                painting_ral=get_attr('painting_ral'),
                thermal_protection=get_attr('thermal_protection'),
                is_official=(get_attr('is_official') == 'True'),
                is_routine=(get_attr('is_routine') == 'True'),
            )
            motors.append(motor)

        return motors
    finally:
        session.close()


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

        query = session.query(Component).filter(
            Component.type_id == motor_type.id,
            cast(Component.power, Float) == float(power),
            Component.rpm == int(rpm),
            Component.voltage == int(voltage)
        )

        optional_filters = {
            "brand": brand,
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip_rating,
            "efficiency_class": efficiency_class,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "is_official": is_official,
            "is_routine": is_routine
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

        attrs = {attr.key: attr.value for attr in motor.attributes}

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
