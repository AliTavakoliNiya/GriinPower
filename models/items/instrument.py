from sqlalchemy.orm import joinedload
import jdatetime
from controllers.user_session_controller import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.user_model import User

"""
attribute_keys:
    type --> required
    hart_comminucation --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""


def get_all_instruments():
    session = SessionLocal()

    attribute_keys = [
        "type", "hart_comminucation",
        "brand", "order_number", "created_by_id"
    ]

    instruments = (
        session.query(Component)
        .filter(Component.type == "Instrument")
        .options(
            joinedload(Component.attributes),
            joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
        )
        .all()
    )

    instrument_list = []
    for instrument in instruments:
        attr_dict = {attr.key: attr.value for attr in instrument.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        for supplier in instrument.suppliers:
            instrument_data = {
                "id": instrument.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by
            }
            for key in attribute_keys:
                if key != "created_by_id":
                    instrument_data[key] = attr_dict.get(key, "")
            instrument_list.append(instrument_data)

    session.close()
    return instrument_list


def get_instrument_by_spec(type, hart_comminucation=None, brand=None, order_number=None):
    brand = brand.lower() if brand else brand
    session = SessionLocal()
    try:
        instruments = (
            session.query(Component)
            .filter(Component.type == "Instrument")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
            .all()
        )

        matching_instruments = []

        for instrument in instruments:
            attr_dict = {attr.key: attr.value for attr in instrument.attributes}

            if attr_dict.get("type") != type:
                continue

            if hart_comminucation is not None:
                if attr_dict.get("hart_comminucation", "").lower() != str(hart_comminucation).lower():
                    continue

            if brand and attr_dict.get("brand") != brand:
                continue
            if order_number and attr_dict.get("order_number") != order_number:
                continue

            matching_instruments.append({
                "component": instrument,
                "attr_dict": attr_dict,
                "latest_supplier": max(instrument.suppliers, key=lambda s: s.date if s.date else "", default=None)
            })

        if not matching_instruments:
            return False, "❌ Instrument not found"

        latest = max(
            matching_instruments,
            key=lambda item: item["latest_supplier"].date if item["latest_supplier"] else ""
        )

        supplier = latest["latest_supplier"]
        attr = latest["attr_dict"]
        result = {
            "id": latest["component"].id,
            "type": attr.get("type"),
            "hart_comminucation": attr.get("hart_comminucation"),
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
        return f"failed in get instrument\n{str(e)}"
    finally:
        session.close()


def insert_instrument_to_db(
        type,
        hart_comminucation,
        brand,
        order_number):
    brand = brand.lower()

    today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")
    current_user = UserSession()
    session = SessionLocal()
    try:
        hart_value = "true" if hart_comminucation is True else "false"

        existing_components = (
            session.query(Component)
            .filter(Component.type == "Instrument")
            .options(joinedload(Component.attributes))
            .all()
        )

        for component in existing_components:
            attr_dict = {attr.key: attr.value for attr in component.attributes}
            if (
                    attr_dict.get("type") == type and
                    attr_dict.get("hart_comminucation") == hart_value and
                    attr_dict.get("brand") == brand and
                    attr_dict.get("order_number") == order_number
            ):
                return True, component.id  # Already exists

        new_instrument = Component(
            type="Instrument",
            attributes=[
                ComponentAttribute(key='type', value=type),
                ComponentAttribute(key='hart_comminucation', value=hart_value),
                ComponentAttribute(key='brand', value=brand),
                ComponentAttribute(key='order_number', value=order_number),
                ComponentAttribute(key='created_by_id', value=str(current_user.id)),
                ComponentAttribute(key='created_at', value=today_shamsi),
            ]
        )
        session.add(new_instrument)
        session.flush()
        session.commit()
        return True, new_instrument.id

    except Exception as e:
        session.rollback()
        print(str(e))
        return False, f"❌ Error inserting Instrument: {str(e)}"
    finally:
        session.close()
