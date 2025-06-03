from sqlalchemy import cast, desc, Integer
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class PLC:

    def __init__(self, brand, model, series, digital_inputs, digital_outputs,
                 analog_inputs, analog_outputs, support_profinet, support_profibus, support_mpi,
                 support_hard_wire, component_supplier):
        self.brand = brand
        self.model = model
        self.series = series
        self.digital_inputs = digital_inputs
        self.digital_outputs = digital_outputs
        self.analog_inputs = analog_inputs
        self.analog_outputs = analog_outputs
        self.support_profinet = support_profinet
        self.support_profibus = support_profibus
        self.support_mpi = support_mpi
        self.support_hard_wire = support_hard_wire
        self.component_supplier = component_supplier

    def __repr__(self):
        return f""

def get_plc_by_io(min_digital_inputs, min_digital_outputs):
    session = SessionLocal()

    try:
        plc_type = session.query(ComponentType).filter_by(name='PLC').first()
        if not plc_type:
            return None, "ComponentType 'PLC' not found."

        attr_in = aliased(ComponentAttribute)
        attr_out = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(attr_in, Component.attributes)
            .join(attr_out, Component.attributes)
            .filter(
                Component.type_id == plc_type.id,
                attr_in.key == 'digital_inputs',
                cast(attr_in.value, Integer) >= min_digital_inputs,
                attr_out.key == 'digital_outputs',
                cast(attr_out.value, Integer) >= min_digital_outputs
            )
            .order_by(cast(attr_in.value, Integer).asc())
            .first()
        )

        if not component:
            return None, "No PLC found with sufficient digital I/O."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        plc = PLC(
            brand=component.brand,
            model=component.model,
            digital_inputs=attrs.get("digital_inputs"),
            digital_outputs=attrs.get("digital_outputs"),
            analog_inputs=attrs.get("analog_inputs"),
            analog_outputs=attrs.get("analog_outputs"),
            support_profinet=attrs.get("support_profinet"),
            support_profibus=attrs.get("support_profibus"),
            support_mpi=attrs.get("support_mpi"),
            support_hard_wire=attrs.get("support_hard_wire"),
            component_supplier=latest_supplier
        )

        return plc, f"{plc}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_plc_by_io:\n{str(e)}"

    finally:
        session.close()
