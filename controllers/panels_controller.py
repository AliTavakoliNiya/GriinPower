from models.contactor_model import get_contactor_by_motor_power
from models.general_model import get_general_by_name
from models.motor_model import Motor
from models.mpcb_model import get_mpcb_by_motor_power
from models.cable_rating_model import get_cable_by_dimension_current
from math import sqrt
from collections import defaultdict


def transport_controller(project_details):
    # ----------------------- transport_panel -----------------------
    transport_panel = {"type": [],
                       "brand": [],
                       "reference_number": [],
                       "specifications": [],
                       "quantity": [],
                       "price": [],
                       "total_price": [],
                       "last_price_update": [],
                       "note": []}

    # ----------------------- creating_motor -----------------------
    rotary = Motor(project_details["transport"]["motors"]["rotary"]["power"], usage="Rotary")
    rotary_qty = project_details["transport"]["motors"]["rotary"]["qty"]

    telescopic_chute = Motor(project_details["transport"]["motors"]["telescopic_chute"]["power"],
                             usage="Telescopic Chute")
    telescopic_chute_qty = project_details["transport"]["motors"]["telescopic_chute"]["qty"]

    slide_gate = Motor(project_details["transport"]["motors"]["slide_gate"]["power"], usage="Slide Gate")
    slide_gate_qty = project_details["transport"]["motors"]["slide_gate"]["qty"]

    screw1 = Motor(project_details["transport"]["motors"]["screw1"]["power"], usage="Screw1")
    screw1_qty = project_details["transport"]["motors"]["screw1"]["qty"]

    screw2 = Motor(project_details["transport"]["motors"]["screw2"]["power"], usage="Screw2")
    screw2_qty = project_details["transport"]["motors"]["screw2"]["qty"]

    transport_motor_qty = [(rotary, rotary_qty), (telescopic_chute, telescopic_chute_qty), (slide_gate, slide_gate_qty),
                           (screw1, screw1_qty), (screw2, screw2_qty)]

    # ----------------------- choose_mpcb -----------------------
    for motor, qty in transport_motor_qty:
        choose_mpcb(transport_panel, motor, qty)

    # ----------------------- choose_contactor -----------------------
    for motor, qty in transport_motor_qty:
        choose_contactor(transport_panel, motor, qty)

    # ----------------------- choose_general -----------------------
    transport_generals = ["lcb", "terminal_4", "terminal_6",
                          "relay_1no_1nc", "relay_2no_2nc",
                          "button", "selector_switch", "signal_lamp_24v",
                          "duct_cover", "miniatory_rail", "panel_wire"]
    for item in transport_generals:
        choose_general(transport_panel, transport_motor_qty, item)

    # ----------------------- choose_power_and_signal_cable -----------------------
    length = project_details["cable_dimension"]
    volt = project_details["volt"]
    if length != 0:
        choose_signal_cable(transport_panel, transport_motor_qty, length)
        choose_power_cable(transport_panel, transport_motor_qty, length, volt)

    # ----------------------- choose_electrical_panel -----------------------
    choose_electrical_panel(transport_panel, transport_motor_qty)

    return transport_panel


def choose_electrical_panel(transport_panel, transport_motor_qty):
    panel_qty = 1

    total_motors = sum(qty for _, qty in transport_motor_qty)
    if total_motors == 0:
        return
    elif total_motors < 3:
        electrical_panel_name = "electrical_panel_0p8x1"
        transport_panel["type"].append("ELECTRICAL PANEL 0.8x1")
    elif total_motors < 4:
        electrical_panel_name = "electrical_panel_0p8x1p6"
        transport_panel["type"].append("ELECTRICAL PANEL 0.8x1.6")
    elif total_motors < 8:
        electrical_panel_name = "electrical_panel_1p2x2p2"
        transport_panel["type"].append("ELECTRICAL PANEL 1.2x2.2")
    else:
        electrical_panel_name = "electrical_panel_1p2x2"
        transport_panel["type"].append("ELECTRICAL PANEL 1.2x2")
        panel_qty = 2

    electrical_panel = get_general_by_name(electrical_panel_name)
    transport_panel["brand"].append(electrical_panel.brand)
    transport_panel["specifications"].append("-")
    transport_panel["reference_number"].append("-")
    transport_panel["quantity"].append(panel_qty)
    transport_panel["price"].append(1_000_000)
    transport_panel["total_price"].append(panel_qty * 1_000_000)
    transport_panel["last_price_update"].append("")
    transport_panel["note"].append(f"for {total_motors} motors")


def choose_mpcb(transport_panel, motor, qty):
    if qty == 0:
        return

    if motor.power_kw == 0:
        return

    mpcb = get_mpcb_by_motor_power(motor.power_kw)
    transport_panel["type"].append(f"MPCB FOR {motor.usage.upper()}")
    transport_panel["brand"].append(mpcb.brand)
    transport_panel["specifications"].append(f"Motor Power: {mpcb.p_kw} KW\nIe: {mpcb.ie_a} A")
    transport_panel["reference_number"].append(mpcb.mpcb_reference)
    transport_panel["quantity"].append(qty)
    transport_panel["price"].append(12_000_000)
    transport_panel["total_price"].append(qty * 12_000_000)
    transport_panel["last_price_update"].append("")
    transport_panel["note"].append(f"{qty} x Motor Power: {motor.power_kw} KW")


def choose_contactor(transport_panel, motor, qty):
    if qty == 0:
        return

    if motor.power_kw == 0:
        return

    contactor = get_contactor_by_motor_power(motor.power_kw)
    transport_panel["type"].append(f"CONTACTOR FOR {motor.usage}")
    transport_panel["brand"].append(contactor.brand)
    transport_panel["specifications"].append(f"Motor Power: {contactor.p_kw} KW")
    transport_panel["reference_number"].append(contactor.contactor_reference)
    transport_panel["quantity"].append(qty)
    transport_panel["price"].append(50_000_000)
    transport_panel["total_price"].append(qty * 50_000_000)
    transport_panel["last_price_update"].append("")
    transport_panel["note"].append(f"{qty} x Motor Power: {motor.power_kw} KW")


def choose_general(transport_panel, transport_motor_qty, item_name):
    item_qty = 0
    notes = []
    for motor, qty in transport_motor_qty:
        if qty != 0:
            item_qty += qty * getattr(motor, item_name + '_qty')
            notes.append(f"{qty}x{getattr(motor, item_name + '_qty')} for {motor.usage}")

    item_note = "\n".join(notes)

    if item_qty == 0:
        return

    general_item = get_general_by_name(item_name)

    item_name = item_name.upper()
    item_name = item_name.replace("_", " ")
    transport_panel["type"].append(item_name)
    transport_panel["brand"].append(general_item.brand)
    transport_panel["specifications"].append("-")
    transport_panel["reference_number"].append("-")
    item_qty = round(item_qty, 1)
    transport_panel["quantity"].append(item_qty)
    transport_panel["price"].append(1_000_000)
    transport_panel["total_price"].append(item_qty * 1_000_000)
    transport_panel["last_price_update"].append("")
    transport_panel["note"].append(item_note)


def choose_signal_cable(transport_panel, transport_motor_qty, length):
    cable_length = 0
    notes = []
    for motor, qty in transport_motor_qty:
        if qty == 0:
            continue
        cable_length += length * motor.signal_cable_7x1p5_l_cofactor * qty
        notes.append(f"{length * motor.signal_cable_7x1p5_l_cofactor * qty} for {motor.usage}")

    cable_note = "\n".join(notes)

    if cable_length == 0:
        return

    cable = get_general_by_name("signal_cable_7x1p5")

    transport_panel["type"].append(f"SIGNAL CABLE 7x1.5")
    transport_panel["brand"].append(cable.brand)
    transport_panel["specifications"].append("-")
    transport_panel["reference_number"].append("-")
    cable_length = round(cable_length, 1)
    transport_panel["quantity"].append(cable_length)
    transport_panel["price"].append(400_000)
    transport_panel["total_price"].append(cable_length * 400_000)
    transport_panel["last_price_update"].append("")
    transport_panel["note"].append(cable_note)


def choose_power_cable(transport_panel, transport_motor_qty, length, volt):
    cable_grouping = defaultdict(lambda: {"total_length": 0, "notes": []})
    correction_factor = 1.6 / (sqrt(3) * volt * 0.85 * 0.93)

    for motor, qty in transport_motor_qty:
        if qty == 0 or motor.power_kw == 0:
            continue

        # Calculate corrected current
        current = motor.power_kw * 1000 * correction_factor

        # Find cable based on motor's current
        cable = get_cable_by_dimension_current(length=length, current=current)

        motor_length = length * motor.power_cable_cofactor * qty

        # Group by cable size
        key = cable.cable_size_mm
        cable_grouping[key]["total_length"] += motor_length
        cable_grouping[key]["notes"].append(f"{motor_length} for {motor.usage}")

    for cable_size_mm, data in cable_grouping.items():
        if data["total_length"] == 0:
            continue

        rounded_length = round(data["total_length"], 1)
        total_price = rounded_length * 850_000

        transport_panel["type"].append(f"POWER CABLE SIZE {cable_size_mm}mm")
        transport_panel["brand"].append("-")
        transport_panel["specifications"].append("-")
        transport_panel["reference_number"].append("-")
        transport_panel["quantity"].append(rounded_length)
        transport_panel["price"].append(850_000)
        transport_panel["total_price"].append(total_price)
        transport_panel["last_price_update"].append("")
        transport_panel["note"].append("\n".join(data["notes"]))
