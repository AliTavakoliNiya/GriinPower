import jdatetime
from sqlalchemy.orm import joinedload

from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    power --> required
    rpm --> required
    voltage --> required
    start_type --> optional
    cooling_method --> optional
    ip_rating --> optional
    efficiency_class --> optional
    painting_ral --> optional
    thermal_protection --> optional
    is_official --> optional
    is_routine --> optional
    brand --> required
    order_number --> required
    created_by_id --> required
"""

def get_all_motors():
    session = SessionLocal()

    attribute_keys = [
        "power", "rpm", "voltage", "start_type", "cooling_method", "ip_rating",
        "efficiency_class", "painting_ral", "thermal_protection",
        "is_official", "is_routine", "brand", "order_number", "created_by_id"
    ]

    motors = (
        session.query(Component)
        .filter(Component.type == "Motor")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    motor_list = []
    for motor in motors:
        attr_dict = {attr.key: attr.value for attr in motor.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in motor.suppliers:
            motor_data = {
                "id": motor.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    motor_data[key] = attr_dict.get(key, "")
            motor_list.append(motor_data)

    session.close()
    return motor_list


def get_motor_by_spec(
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
    brand = brand.lower() if brand else brand
    session = SessionLocal()
    try:
        power_val = float(power)
        rpm_val = int(rpm)
        voltage_val = int(voltage)

        min_power = power_val
        max_power = power_val * 1.1  # 10% margin

        motors = (
            session.query(Component)
            .filter(Component.type == "Motor")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_motors = []

        for motor in motors:
            attr_dict = {attr.key: attr.value for attr in motor.attributes}

            try:
                motor_power = float(attr_dict.get("power", -1))
                motor_rpm = int(attr_dict.get("rpm", -1))
                motor_voltage = int(attr_dict.get("voltage", -1))
            except ValueError:
                continue  # skip invalid records

            if not (min_power <= motor_power <= max_power):
                continue
            if motor_rpm != rpm_val or motor_voltage != voltage_val:
                continue
            if attr_dict.get("brand") != brand:
                continue

            # Optional filters
            if start_type and attr_dict.get("start_type") != start_type:
                continue
            if cooling_method and attr_dict.get("cooling_method") != cooling_method:
                continue
            if ip_rating and attr_dict.get("ip_rating") != ip_rating:
                continue
            if efficiency_class and attr_dict.get("efficiency_class") != efficiency_class:
                continue
            if painting_ral and attr_dict.get("painting_ral") != painting_ral:
                continue
            if thermal_protection and attr_dict.get("thermal_protection") != thermal_protection:
                continue
            if is_official and attr_dict.get("is_official") != is_official:
                continue
            if is_routine and attr_dict.get("is_routine") != is_routine:
                continue

            latest_supplier = max(motor.suppliers, key=lambda s: s.date if s.date else "", default=None)

            matching_motors.append({
                "component": motor,
                "attr_dict": attr_dict,
                "latest_supplier": latest_supplier
            })

        if not matching_motors:
            return False, "❌ Motor not found"

        latest = max(
            matching_motors,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]

        result = {
            "id": latest["component"].id,
            "power": attr.get("power"),
            "rpm": attr.get("rpm"),
            "voltage": attr.get("voltage"),
            "brand": attr.get("brand"),
            "start_type": attr.get("start_type", ""),
            "cooling_method": attr.get("cooling_method", ""),
            "ip_rating": attr.get("ip_rating", ""),
            "efficiency_class": attr.get("efficiency_class", ""),
            "painting_ral": attr.get("painting_ral", ""),
            "thermal_protection": attr.get("thermal_protection", ""),
            "is_official": attr.get("is_official", ""),
            "is_routine": attr.get("is_routine", ""),
            "supplier_name": supplier.supplier.name if supplier else "",
            "price": supplier.price if supplier else "",
            "currency": supplier.currency if supplier else "",
            "date": str(supplier.date) if supplier else "",
        }

        return True, result

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"error {str(e)}"
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
    brand = brand.lower()
    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "Motor")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                attr_dict.get("power") == power and
                attr_dict.get("rpm") == rpm and
                attr_dict.get("voltage") == voltage and
                attr_dict.get("brand") == brand and
                attr_dict.get("start_type") == start_type and
                attr_dict.get("cooling_method") == cooling_method and
                attr_dict.get("ip_rating") == ip_rating and
                attr_dict.get("efficiency_class") == efficiency_class and
                attr_dict.get("painting_ral") == painting_ral and
                attr_dict.get("thermal_protection") == thermal_protection and
                attr_dict.get("is_official") == is_official and
                attr_dict.get("is_routine") == is_routine
            ):
                return True, component.id  # Already exists

        attributes = [
            ComponentAttribute(key="power", value=power),
            ComponentAttribute(key="rpm", value=rpm),
            ComponentAttribute(key="voltage", value=voltage),
            ComponentAttribute(key="brand", value=brand),
            ComponentAttribute(key="created_by_id", value=str(current_user.id)),
            ComponentAttribute(key="created_at", value=today_shamsi),
        ]

        optional_fields = {
            "start_type": start_type,
            "cooling_method": cooling_method,
            "ip_rating": ip_rating,
            "efficiency_class": efficiency_class,
            "painting_ral": painting_ral,
            "thermal_protection": thermal_protection,
            "is_official": is_official,
            "is_routine": is_routine
        }

        for key, value in optional_fields.items():
            if value is not None:
                attributes.append(ComponentAttribute(key=key, value=str(value)))

        new_motor = Component(
            type="Motor",
            attributes=attributes
        )

        session.add(new_motor)
        session.flush()
        session.commit()
        return True, new_motor.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting motor: {str(e)}"
    finally:
        session.close()
