from sqlalchemy import Column, String
from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class ItemPrice(Base):
    __tablename__ = 'item_prices'

    price_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=False)
    # vendor_id = Column(Integer, ForeignKey('vendors.vendor_id', ondelete="CASCADE"), nullable=False)

    price = Column(Float, nullable=False)
    brand = Column(String, nullable=False)
    reference = Column(String, nullable=False)
    effective_date = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="prices")
    # vendor = relationship("Vendor", back_populates="item_prices")
    creator = relationship("User", back_populates="item_prices_created")

    def __repr__(self):
        return f"<ItemPrice(price={self.price}, brand='{self.brand}', effective_date='{self.effective_date}')>"


def get_price(item_id, brand, item_brand=True):
    session = SessionLocal()

    try:
        if item_brand:
            rslt = (
                    session.query(ItemPrice)
                    .filter(ItemPrice.item_id == item_id, ItemPrice.brand == brand)
                    .order_by(ItemPrice.effective_date.desc())
                    .limit(1)
                    .first()
                    or ItemPrice()
            )
        else:
            rslt = (
                    session.query(ItemPrice)
                    .filter(ItemPrice.item_id == item_id)
                    .order_by(ItemPrice.effective_date.desc())
                    .limit(1)
                    .first()
                    or ItemPrice()
            )

        return rslt

    except Exception as e:
        session.rollback()
        show_message("item_price_model\n" + str(e) + "\n")
        return ItemPrice()

    finally:
        session.close()
