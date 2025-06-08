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
    class --> required
    trip_time --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""

def get_all_bimetals():
    session = SessionLocal()

    attribute_keys = [
        "min_current", "max_current", "class", "trip_time",
        "brand", "order_number", "created_by_id"
    ]

    bimetals = (
        session.query(Component)
        .filter(Component.type == "Bimetal")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    bimetal_list = []
    for bimetal in bimetals:
        attr_dict = {attr.key: attr.value for attr in bimetal.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in bimetal.suppliers:
            bimetal_data = {
                "id": bimetal.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    bimetal_data[key] = attr_dict.get(key, "")
            bimetal_list.append(bimetal_data)

    session.close()
    return bimetal_list


def get_bimetal_by_current(rated_current, brands=[], order_number=None):
    session = SessionLocal()
    try:
        current_val = float(rated_current)

        bimetals = (
            session.query(Component)
            .filter(Component.type == "Bimetal")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_bimetals = []

        for bimetal in bimetals:
            attr_dict = {attr.key: attr.value for attr in bimetal.attributes}

            try:
                min_c = float(attr_dict.get("min_current", -1))
                max_c = float(attr_dict.get("max_current", -1))
            except ValueError:
                continue

            # بررسی تطابق جریان با بازه
            if not (min_c <= current_val <= max_c):
                continue

            # بررسی برند
            brand = attr_dict.get("brand")
            if brands and brand not in brands:
                continue

            # بررسی شماره سفارش
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_bimetals.append({
                "component": bimetal,
                "attr_dict": attr_dict,
                "range": max_c - min_c,
                "latest_supplier": max(bimetal.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_bimetals:
            return False, "❌ Bimetal not found"

        # انتخاب بی‌متال با کمترین بازه جریان
        best_match = min(
            matching_bimetals,
            key=lambda item: item["range"]
        )

        supplier = best_match["latest_supplier"]
        attr = best_match["attr_dict"]
        result = {
            "id": best_match["component"].id,
            "min_current": attr.get("min_current"),
            "max_current": attr.get("max_current"),
            "class": attr.get("class"),
            "trip_time": attr.get("trip_time"),
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
        return False, f"❌ Failed in get_bimetal_by_current:\n{str(e)}"
    finally:
        session.close()


def insert_bimetal_to_db(
        brand,
        order_number,
        min_current,
        max_current,
        _class,
        trip_time,
        ):
    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "Bimetal")
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
                attr_dict.get("class") == _class and
                attr_dict.get("trip_time") == trip_time
            ):
                return True, component.id

        new_bimetal = Component(
            type="Bimetal",
            attributes=[
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='min_current', value=min_current),
                ComponentAttribute(key='max_current', value=max_current),
                ComponentAttribute(key='class', value=_class),
                ComponentAttribute(key='trip_time', value=trip_time),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_bimetal)
        session.flush()
        session.commit()
        return True, new_bimetal.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting Bimetal: {str(e)}"
    finally:
        session.close()

