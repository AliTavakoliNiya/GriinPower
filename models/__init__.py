"""
When you have multiple model files (like user_model.py, contactor_model.py, etc.) that reference each other, circular imports can easily happen. For example:

    user_model.py references Contactor

    contactor_model.py references User

If each file tries to import the other directly, Python's import system can run into a circular dependency where neither module is fully loaded when the other needs it.
"""


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

__all__ = [
    "Base",
    "User",
    "Contactor",
    "General",
    "ElectricMotor",
    "Instrument",
    "ItemPrice",
]

from .item_price_model import ItemPrice
from models.items.electric_motor_model import ElectricMotor
from models.items.instrument_model import Instrument
from .user_model import User
from models.items.contactor_model import Contactor
from models.items.mccb_model import MCCB
from models.items.mpcb_model import MPCB
from .item_model import Item
from models.items.general_model import General


