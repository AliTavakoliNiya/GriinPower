import jdatetime
from sqlalchemy.orm import joinedload

from controllers.user_session_controller import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    type --> required
    width --> required
    height --> required
    depth --> required
    ip_rating --> optional
    brand --> required
    order_number --> required
    created_by_id --> required
"""


def get_all_electrical_panel():
    session = SessionLocal()

    attribute_keys = ["type", "width", "height", "depth", "ip_rating", "brand", "order_number", "created_by_id"]

    generals = (
        session.query(Component)
        .filter(Component.type.in_(["Electrical Panel", "Local Box", "Junction Box"]))
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


def get_electrical_panel_by_spec(type, width=None, height=None, depth=None, ip_rating=None, brand=None, order_number=""):

    session = SessionLocal()
    try:
        panels = (
            session.query(Component)
            .filter(Component.type == type)
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_panels = []

        for panel in panels:
            attr_dict = {attr.key: attr.value for attr in panel.attributes}

            if attr_dict.get("type") != type:
                continue
            if width and attr_dict.get("width") != width:
                continue
            if height and attr_dict.get("height") != height:
                continue
            if depth and attr_dict.get("depth") != depth:
                continue
            if ip_rating and attr_dict.get("ip_rating") != ip_rating:
                continue
            if brand and attr_dict.get("brand") != brand:
                continue
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_panels.append({
                "component": panel,
                "attr_dict": attr_dict,
                "latest_supplier": max(panel.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_panels:
            return False, "❌ Component not found"

        latest = max(
            matching_panels,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]
        result = {
            "id": latest["component"].id,
            "type": attr.get("type"),
            "width": attr.get("width"),
            "height": attr.get("height"),
            "depth": attr.get("depth"),
            "ip_rating": attr.get("ip_rating", ""),
            "brand": attr.get("brand"),
            "order_number": attr.get("order_number"),
            "supplier_name": supplier.supplier.name if supplier else "",
            "price": supplier.price if supplier else 0,
            "currency": supplier.currency if supplier else "",
            "date": str(supplier.date) if supplier else "",
        }
        return True, result

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error get panel: {str(e)}"
    finally:
        session.close()



def insert_electrical_panel_to_db(
        type,
        width,
        height,
        depth,
        brand,
        order_number,
        ip_rating=None):

    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == type)
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                    attr_dict.get("type") == type and
                    attr_dict.get("width") == width and
                    attr_dict.get("height") == height and
                    attr_dict.get("depth") == depth and
                    attr_dict.get("brand") == brand and
                    attr_dict.get("order_number") == order_number and
                    (not ip_rating or attr_dict.get("ip_rating") == ip_rating)
            ):
                return True, component.id

        attributes = [
            ComponentAttribute(key="type", value=type),
            ComponentAttribute(key="width", value=width),
            ComponentAttribute(key="height", value=height),
            ComponentAttribute(key="depth", value=depth),
            ComponentAttribute(key="brand", value=brand),
            ComponentAttribute(key="order_number", value=order_number),
            ComponentAttribute(key="created_by_id", value=str(current_user.id)),
            ComponentAttribute(key="created_at", value=today_shamsi),
        ]
        if ip_rating:
            attributes.append(ComponentAttribute(key="ip_rating", value=ip_rating))

        new_panel = Component(
            type=type,
            attributes=attributes
        )
        session.add(new_panel)
        session.flush()
        session.commit()
        return True, new_panel.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting panel: {str(e)}"
    finally:
        session.close()




