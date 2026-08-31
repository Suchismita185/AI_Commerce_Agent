from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    tags = Column(String(500))
    upsell_product_id = Column(Integer, nullable=True)