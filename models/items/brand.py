from sqlalchemy import select, distinct

from models import ComponentAttribute
from utils.database import SessionLocal


def get_all_brands():
    session = SessionLocal()
    try:
        results = session.execute(
            select(distinct(ComponentAttribute.value))
            .where(ComponentAttribute.key == "brand")
        ).scalars().all()
        return True, results
    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get brands: {str(e)}"
    finally:
        session.close()
