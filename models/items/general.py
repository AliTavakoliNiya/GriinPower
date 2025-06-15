import jdatetime
from sqlalchemy.orm import joinedload

from controllers.user_session_controller import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    type --> required
    specification --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""


def get_all_generals():
    session = SessionLocal()

    attribute_keys = ["type", "specification", "brand", "order_number", "created_by_id"]

    generals = (
        session.query(Component)
        .filter(Component.type == "General")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    general_list = []
    for general in generals:
        attr_dict = {attr.key: attr.value for attr in general.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in general.suppliers:
            general_data = {
                "id": general.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    general_data[key] = attr_dict.get(key, "")
            general_list.append(general_data)

    session.close()
    return general_list


def get_general_by_spec(type, specification, brand=None, order_number=None):
    brand = brand.lower() if brand else None
    session = SessionLocal()
    try:
        generals = (
            session.query(Component)
            .filter(Component.type == "General")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_generals = []

        for general in generals:
            attr_dict = {attr.key: attr.value for attr in general.attributes}

            if attr_dict.get("type") != type or attr_dict.get("specification") != specification:
                continue

            if brand and attr_dict.get("brand") != brand:
                continue
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_generals.append({
                "component": general,
                "attr_dict": attr_dict,
                "latest_supplier": max(general.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_generals:
            return False, "❌ General component not found"

        latest = max(
            matching_generals,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]
        result = {
            "id": latest["component"].id,
            "type": attr.get("type"),
            "specification": attr.get("specification"),
            "brand": attr.get("brand", ""),
            "order_number": attr.get("order_number", ""),
            "supplier_name": supplier.supplier.name if supplier else "",
            "price": supplier.price if supplier else 0,
            "currency": supplier.currency if supplier else "",
            "date": str(supplier.date) if supplier else "",
        }
        return True, result

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"failed in get generals {str(e)}"
    finally:
        session.close()


def insert_general_to_db(
        brand,
        order_number,
        type,
        specification):
    brand = brand.lower()
    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "General")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                    attr_dict.get("type") == type and
                    attr_dict.get("specification") == specification and
                    attr_dict.get("brand") == brand and
                    attr_dict.get("order_number") == order_number
            ):
                return True, component.id  # Already exists

        new_general = Component(
            type="General",
            attributes=[
                ComponentAttribute(key='type', value=type),
                ComponentAttribute(key='specification', value=specification),
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_general)
        session.flush()
        session.commit()
        return True, new_general.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting General: {str(e)}"
    finally:
        session.close()



