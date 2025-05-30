from sqlalchemy import cast, desc, Integer
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class PLC:

    def __init__(self, name, brand, model, cpu_type, digital_inputs, digital_outputs,
                 analog_inputs, analog_outputs, communication_ports, memory_size_kb, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.cpu_type = cpu_type
        self.digital_inputs = digital_inputs
        self.digital_outputs = digital_outputs
        self.analog_inputs = analog_inputs
        self.analog_outputs = analog_outputs
        self.communication_ports = communication_ports
        self.memory_size_kb = memory_size_kb
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<PLC(name={self.name}, cpu_type={self.cpu_type}, di={self.digital_inputs}, do={self.digital_outputs})>"

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

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        plc = PLC(
            name=component.name,
            brand=component.brand,
            model=component.model,
            cpu_type=attrs.get("cpu_type"),
            digital_inputs=attrs.get("digital_inputs"),
            digital_outputs=attrs.get("digital_outputs"),
            analog_inputs=attrs.get("analog_inputs"),
            analog_outputs=attrs.get("analog_outputs"),
            communication_ports=attrs.get("communication_ports"),
            memory_size_kb=attrs.get("memory_size_kb"),
            component_vendor=latest_vendor
        )

        return plc, f"{plc}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_plc_by_io:\n{str(e)}"

    finally:
        session.close()
