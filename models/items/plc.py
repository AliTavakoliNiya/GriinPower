from sqlalchemy.orm import joinedload
import jdatetime
from controllers.user_session_controller import UserSession
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal
from models.users import User
from sqlalchemy.orm import aliased
from sqlalchemy import desc
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


def get_plc_by_spec(series, **optional_filters):
    """
    Retrieve a single PLC component filtered by series (required)
    and optionally by other attribute key-value pairs.

    Returns (True, plc_data) if found, else (False, message).

    :param series: required attribute 'series' string
    :param optional_filters: other optional filters as key=value pairs
    """
    session = SessionLocal()
    try:
        if not series:
            return False, "Series is required"

        query = (
            session.query(Component)
            .filter(Component.type == "PLC")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
        )

        # Join once for series filter
        alias_series = ComponentAttribute.__table__.alias("attr_series")
        query = query.join(
            alias_series,
            (alias_series.c.component_id == Component.id) &
            (alias_series.c.key == "series") &
            (alias_series.c.value == str(series))
        )

        # Join for each optional filter if provided and value not None or empty
        for i, (key, value) in enumerate(optional_filters.items()):
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue  # skip empty filters

            val_str = str(value).lower() if isinstance(value, bool) else str(value)
            alias = ComponentAttribute.__table__.alias(f"attr_opt_{i}")
            query = query.join(
                alias,
                (alias.c.component_id == Component.id) &
                (alias.c.key == key) &
                (alias.c.value == val_str)
            )

        supplier_alias = aliased(ComponentSupplier)
        query = query.join(supplier_alias, supplier_alias.component_id == Component.id)
        query = query.order_by(desc(supplier_alias.date))

        plc = query.first()
        if not plc:
            return False, "No matching PLC found"

        attr_dict = {attr.key: attr.value for attr in plc.attributes}
        created_by_id = attr_dict.get("created_by_id")

        created_by = ""
        if created_by_id:
            user = session.query(User).filter_by(id=int(created_by_id)).first()
            if user:
                created_by = f"{user.first_name} {user.last_name}"

        plc_list = []
        for supplier in plc.suppliers:
            plc_data = {
                "id": plc.id,
                "supplier_name": supplier.supplier.name,
                "price": supplier.price,
                "currency": supplier.currency,
                "date": str(supplier.date),
                "created_by": created_by,
            }
            plc_data.update(attr_dict)
            plc_list.append(plc_data)

        return True, plc_list[0] if plc_list else attr_dict

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
    brand = brand.lower()

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
