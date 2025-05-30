from utils.database import SessionLocal
from models import ComponentType


session = SessionLocal()

motor_type = ComponentType(name='JB', description='Junction Box')
session.add(motor_type)
session.commit()
session.close()