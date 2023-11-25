# produtos.py
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from .base import Base

class Produtos(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)    
    description = Column(Text, nullable=True)
    shopping_cart_items = relationship('ShoppingCartItem', back_populates='product')