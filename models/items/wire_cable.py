import jdatetime
from sqlalchemy.orm import joinedload

from controllers.user_session_controller import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.users import User

"""
attribute_keys:
    type --> required
    l_number --> required
    l_size --> required
    note --> optional
    brand --> required
    order_number --> fixed = ""
    created_by_id --> required
"""


def get_all_wire_cable():
    session = SessionLocal()
    attribute_keys = ["type", "l_number", "l_size", "note", "brand", "order_number", "created_by_id"]

    components = (
        session.query(Component)
        .filter(Component.type == "WireCable")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    result_list = []
    for component in components:
        attr_dict = {attr.key: attr.value for attr in component.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in component.suppliers:
            item = {
                "id": component.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key == "l_number":
                    try:
                        item[key] = int(attr_dict.get(key, 0))
                    except (ValueError, TypeError):
                        item[key] = 0
                elif key == "l_size":
                    try:
                        item[key] = float(attr_dict.get(key, 0))
                    except (ValueError, TypeError):
                        item[key] = 0.0
                elif key != "created_by_id":
                    item[key] = attr_dict.get(key, "")
            result_list.append(item)

    session.close()
    return result_list


def get_wire_cable_by_spec(type, l_number, l_size=None, brand=None, note=None):
    session = SessionLocal()
    try:
        components = (
            session.query(Component)
            .filter(Component.type == "WireCable")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matches = []
        for comp in components:
            attr_dict = {attr.key: attr.value for attr in comp.attributes}

            if attr_dict.get("type") != type:
                continue

            try:
                l_number_db = int(attr_dict.get("l_number", 0))
                l_size_db = float(attr_dict.get("l_size", 0))
            except (ValueError, TypeError):
                continue

            if l_number_db != int(l_number):
                continue
            if l_size and l_size_db != float(l_size):
                continue
            if brand and attr_dict.get("brand") != brand:
                continue
            if note and attr_dict.get("note") != note:
                continue

            latest_supplier = max(comp.suppliers, key=lambda s: s.date if s.date else "", default=None)
            matches.append({
                "component": comp,
                "attr_dict": attr_dict,
                "latest_supplier": latest_supplier
            })

        if not matches:
            return False, "❌ Component not found"

        latest = max(matches, key=lambda x: x["latest_supplier"].date if x["latest_supplier"] else "")
        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]

        result = {
            "id": latest["component"].id,
            "type": attr.get("type"),
            "l_number": int(attr.get("l_number", 0)),
            "l_size": float(attr.get("l_size", 0)),
            "brand": attr.get("brand"),
            "note": attr.get("note", ""),
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
        return False, f"❌ Error get wire/cable: {str(e)}"
    finally:
        session.close()


def insert_wire_cable_to_db(type, l_number, l_size, brand, note=None, created_by_id=None):
    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing = (
            session.query(Component)
            .filter(Component.type == "WireCable")
            .options(joinedload(Component.attributes))
            .all()
        )

        for comp in existing:
            attr_dict = {attr.key: attr.value for attr in comp.attributes}
            if (
                    attr_dict.get("type") == type and
                    attr_dict.get("l_number") == l_number and
                    attr_dict.get("l_size") == l_size and
                    attr_dict.get("brand") == brand and
                    attr_dict.get("order_number") == ""
            ):
                if note and attr_dict.get("note") != note:
                    continue
                return True, comp.id

        created_by_id = created_by_id if created_by_id else str(current_user.id)
        attributes = [
            ComponentAttribute(key="type", value=type),
            ComponentAttribute(key="l_number", value=l_number),
            ComponentAttribute(key="l_size", value=l_size),
            ComponentAttribute(key="brand", value=brand),
            ComponentAttribute(key="order_number", value=""),
            ComponentAttribute(key="created_by_id", value=str(created_by_id)),
            ComponentAttribute(key="created_at", value=today_shamsi),
        ]
        if note:
            attributes.append(ComponentAttribute(key="note", value=note))

        new_component = Component(
            type="WireCable",
            attributes=attributes
        )
        session.add(new_component)
        session.flush()
        session.commit()
        return True, new_component.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting wire/cable: {str(e)}"
    finally:
        session.close()
