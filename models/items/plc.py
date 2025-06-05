from sqlalchemy.orm import joinedload
import jdatetime
from controllers.user_session import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    series --> required
    model --> required
    di_pins --> required
    do_pins --> required
    ai_pins --> required
    ao_pins --> required
    comminucation_type:has_profinet --> required
    comminucation_type:has_profibus --> required
    comminucation_type:has_hart --> required
    has_mpi --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""

def get_all_plcs():
    session = SessionLocal()

    attribute_keys = [
        "series", "model", "di_pins", "do_pins", "ai_pins", "ao_pins",
        "has_profinet",
        "has_profibus",
        "has_hart",
        "has_mpi",
        "brand", "order_number", "created_by_id"
    ]

    plcs = (
        session.query(Component)
        .filter(Component.type == "PLC")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    plc_list = []
    for plc in plcs:
        attr_dict = {attr.key: attr.value for attr in plc.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in plc.suppliers:
            plc_data = {
                "id": plc.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    plc_data[key] = attr_dict.get(key, "")
            plc_list.append(plc_data)

    session.close()
    return plc_list



def get_plc_by_spec(series, model, comminucation_type=None, brand="siemens", order_number=None):
    session = SessionLocal()
    try:
        plcs = (
            session.query(Component)
            .filter(Component.type == "PLC")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_plcs = []

        for plc in plcs:
            attr_dict = {attr.key: attr.value for attr in plc.attributes}

            if attr_dict.get("series") != series or attr_dict.get("model") != model:
                continue

            if brand and attr_dict.get("brand") != brand:
                continue
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            if comminucation_type:
                comm_key = f"{comminucation_type}"
                if attr_dict.get(comm_key, "false").lower() != "true":
                    continue

            matching_plcs.append({
                "component": plc,
                "attr_dict": attr_dict,
                "latest_supplier": max(plc.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_plcs:
            return False, "❌ PLC not found"

        latest = max(
            matching_plcs,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]
        result = {
            "id": latest["component"].id,
            "series": attr.get("series"),
            "model": attr.get("model"),
            "di_pins": attr.get("di_pins"),
            "do_pins": attr.get("do_pins"),
            "ai_pins": attr.get("ai_pins"),
            "ao_pins": attr.get("ao_pins"),
            "has_profinet": attr.get("has_profinet"),
            "has_profibus": attr.get("has_profibus"),
            "has_hart": attr.get("has_hart"),
            "has_mpi": attr.get("has_mpi"),
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
        print(str(e))
        return f"failed in get plc\n{str(e)}"
    finally:
        session.close()



def insert_plc_to_db(
        series,
        model,
        di_pins,
        do_pins,
        ai_pins,
        ao_pins,
        has_profinet,
        has_profibus,
        has_hart,
        has_mpi,
        brand,
        order_number
    ):
    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        existing_components = (
            session.query(Component)
            .filter(Component.type == "PLC")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                attr_dict.get("series") == series and
                attr_dict.get("model") == model and
                attr_dict.get("order_number") == order_number
            ):
                return True, component.id

        new_plc = Component(
            type="PLC",
            attributes=[
                ComponentAttribute(key="series", value=series),
                ComponentAttribute(key="model", value=model),
                ComponentAttribute(key="di_pins", value=di_pins),
                ComponentAttribute(key="do_pins", value=do_pins),
                ComponentAttribute(key="ai_pins", value=ai_pins),
                ComponentAttribute(key="ao_pins", value=ao_pins),
                ComponentAttribute(key="has_profinet", value=str(has_profinet).lower()),
                ComponentAttribute(key="has_profibus", value=str(has_profibus).lower()),
                ComponentAttribute(key="has_hart", value=str(has_hart).lower()),
                ComponentAttribute(key="has_mpi", value=str(has_mpi).lower()),
                ComponentAttribute(key="brand", value=brand),
                ComponentAttribute(key="order_number", value=order_number),
                ComponentAttribute(key="created_by_id", value=str(current_user.id)),
                ComponentAttribute(key="created_at", value=today_shamsi),
            ]
        )
        session.add(new_plc)
        session.flush()
        session.commit()
        return True, new_plc.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting PLC: {str(e)}"
    finally:
        session.close()

