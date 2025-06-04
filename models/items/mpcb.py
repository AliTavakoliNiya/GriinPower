from sqlalchemy.orm import joinedload
import jdatetime
from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    min_current --> required
    max_current --> required
    breaking_capacity --> required
    trip_class --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""

def get_all_mpcbs():
    session = SessionLocal()

    attribute_keys = [
        "min_current", "max_current", "breaking_capacity", "trip_class",
        "brand", "order_number", "created_by_id"
    ]

    mpcbs = (
        session.query(Component)
        .filter(Component.type == "MPCB")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    mpcb_list = []
    for mpcb in mpcbs:
        attr_dict = {attr.key: attr.value for attr in mpcb.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in mpcb.suppliers:
            mpcb_data = {
                "id": mpcb.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    mpcb_data[key] = attr_dict.get(key, "")
            mpcb_list.append(mpcb_data)

    session.close()
    return mpcb_list


def get_mpcb_by_current(rated_current, brand=None, order_number=None):
    session = SessionLocal()
    try:
        current_val = float(rated_current)

        mpcbs = (
            session.query(Component)
            .filter(Component.type == "MPCB")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_mpcbs = []

        for mpcb in mpcbs:
            attr_dict = {attr.key: attr.value for attr in mpcb.attributes}

            try:
                min_c = float(attr_dict.get("min_current", -1))
                max_c = float(attr_dict.get("max_current", -1))
            except ValueError:
                continue

            if not (min_c <= current_val <= max_c):
                continue

            if brand and attr_dict.get("brand") != brand:
                continue
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_mpcbs.append({
                "component": mpcb,
                "attr_dict": attr_dict,
                "latest_supplier": max(mpcb.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_mpcbs:
            return False, "❌ MPCB not found"

        latest = max(
            matching_mpcbs,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]
        result = {
            "id": latest["component"].id,
            "min_current": attr.get("min_current"),
            "max_current": attr.get("max_current"),
            "breaking_capacity": attr.get("breaking_capacity"),
            "trip_class": attr.get("trip_class"),
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
        return False, f"get mpcb error:\n{str(e)}"
    finally:
        session.close()


def insert_mpcb_to_db(
        brand,
        order_number,
        min_current,
        max_current,
        breaking_capacity,
        trip_class,
        ):

    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "MPCB")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                attr_dict.get("brand") == brand and
                attr_dict.get("order_number") == order_number and
                attr_dict.get("min_current") == min_current and
                attr_dict.get("max_current") == max_current and
                attr_dict.get("breaking_capacity") == breaking_capacity and
                attr_dict.get("trip_class") == trip_class
            ):
                return True, component.id  # Already exists

        new_mpcb = Component(
            type="MPCB",
            attributes=[
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='min_current', value=min_current),
                ComponentAttribute(key='max_current', value=max_current),
                ComponentAttribute(key='breaking_capacity', value=breaking_capacity),
                ComponentAttribute(key='trip_class', value=trip_class),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_mpcb)
        session.flush()
        session.commit()
        return True, new_mpcb.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting MPCB: {str(e)}"
    finally:
        session.close()
