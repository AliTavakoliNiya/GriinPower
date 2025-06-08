import jdatetime
from sqlalchemy.orm import joinedload

from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    rated_current --> required
    coil_voltage --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""


def get_all_contactors():
    session = SessionLocal()

    attribute_keys = [
        "rated_current", "coil_voltage", "brand", "order_number", "created_by_id"
    ]

    contactors = (
        session.query(Component)
        .filter(Component.type == "Contactor")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    contactor_list = []
    for contactor in contactors:
        attr_dict = {attr.key: attr.value for attr in contactor.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in contactor.suppliers:
            contactor_data = {
                "id": contactor.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":  
                    contactor_data[key] = attr_dict.get(key, "")
            contactor_list.append(contactor_data)

    session.close()
    return contactor_list


def get_contactor_by_current(rated_current, brands=[], order_number=None):
    session = SessionLocal()
    try:
        current_val = float(rated_current)
        min_val = current_val * 1.25

        contactors = (
            session.query(Component)
            .filter(Component.type == "Contactor")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_contactors = []

        for contactor in contactors:
            attr_dict = {attr.key: attr.value for attr in contactor.attributes}

            rc = float(attr_dict.get("rated_current", -1))
            brand = attr_dict.get("brand")

            if rc < min_val:
                continue

            if brands and brand not in brands:
                continue

            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_contactors.append({
                "component": contactor,
                "attr_dict": attr_dict,
                "rated_current": rc,
                "latest_supplier": max(contactor.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_contactors:
            return False, "❌ Contactor not found"

        best_match = min(
            matching_contactors,
            key=lambda item: item["rated_current"]
        )

        supplier = best_match["latest_supplier"]
        attr = best_match["attr_dict"]
        result = {
            "id": best_match["component"].id,
            "rated_current": attr.get("rated_current"),
            "coil_voltage": attr.get("coil_voltage"),
            "brand": attr.get("brand"),
            "order_number": attr.get("order_number"),
            "supplier_name": supplier.supplier.name if supplier else "",
            "price": supplier.price if supplier else "",
            "currency": supplier.currency if supplier else "",
            "date": str(supplier.date) if supplier else "",
        }
        return True, result

    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()


def insert_contactor_to_db(
        brand,
        order_number,
        rated_current,
        coil_voltage):

    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "Contactor")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                attr_dict.get("brand") == brand and
                attr_dict.get("order_number") == order_number and
                attr_dict.get("rated_current") == rated_current and
                attr_dict.get("coil_voltage") == coil_voltage
            ):
                return True, component.id  # component exists

        new_contactor = Component(
            type="Contactor",
            attributes=[
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='rated_current', value=rated_current),
                ComponentAttribute(key='coil_voltage', value=coil_voltage),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_contactor)
        session.flush()
        session.commit()
        return True, new_contactor.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting contactor: {str(e)}"
    finally:
        session.close()


