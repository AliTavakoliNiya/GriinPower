from sqlalchemy.orm import joinedload
import jdatetime
from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    rated_current --> required
    breaking_capacity --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""


def get_all_mccbs():
    session = SessionLocal()

    attribute_keys = [
        "rated_current", "breaking_capacity", "brand", "order_number", "created_by_id"
    ]

    mccbs = (
        session.query(Component)
        .filter(Component.type == "MCCB")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    mccb_list = []
    for mccb in mccbs:
        attr_dict = {attr.key: attr.value for attr in mccb.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in mccb.suppliers:
            mccb_data = {
                "id": mccb.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    mccb_data[key] = attr_dict.get(key, "")
            mccb_list.append(mccb_data)

    session.close()
    return mccb_list


def get_mccb_by_current(rated_current, brands=[], order_number=None):
    session = SessionLocal()
    try:
        current_val = float(rated_current)
        min_val = current_val * 1.25

        mccbs = (
            session.query(Component)
            .filter(Component.type == "MCCB")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_mccbs = []

        for mccb in mccbs:
            attr_dict = {attr.key: attr.value for attr in mccb.attributes}

            try:
                rc = float(attr_dict.get("rated_current", -1))
            except ValueError:
                continue

            # شرط جریان
            if rc < min_val:
                continue

            # شرط برند
            brand = attr_dict.get("brand")
            if brands and brand not in brands:
                continue

            # شرط شماره سفارش
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_mccbs.append({
                "component": mccb,
                "attr_dict": attr_dict,
                "rated_current": rc,
                "latest_supplier": max(mccb.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_mccbs:
            return False, "❌ MCCB not found"

        # انتخاب MCCB با کمترین جریان مجاز
        best_match = min(
            matching_mccbs,
            key=lambda item: item["rated_current"]
        )

        supplier = best_match["latest_supplier"]
        attr = best_match["attr_dict"]
        result = {
            "id": best_match["component"].id,
            "rated_current": attr.get("rated_current"),
            "breaking_capacity": attr.get("breaking_capacity"),
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


def insert_mccb_to_db(
        brand,
        order_number,
        rated_current,
        breaking_capacity,
        ):

    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "MCCB")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                attr_dict.get("brand") == brand and
                attr_dict.get("order_number") == order_number and
                attr_dict.get("rated_current") == rated_current and
                attr_dict.get("breaking_capacity") == breaking_capacity
            ):
                return True, component.id  # already exists

        new_mccb = Component(
            type="MCCB",
            attributes=[
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='rated_current', value=rated_current),
                ComponentAttribute(key='breaking_capacity', value=breaking_capacity),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_mccb)
        session.flush()
        session.commit()
        return True, new_mccb.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting MCCB: {str(e)}"
    finally:
        session.close()



