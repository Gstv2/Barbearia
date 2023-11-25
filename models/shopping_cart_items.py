# shopping_cart_items.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ShoppingCartItem(Base):
    __tablename__ = 'shopping_cart_items'

    id = Column(Integer, primary_key=True)
    user_email = Column(String(255), ForeignKey('user.email'), nullable=False)
    product_id = Column(Integer, ForeignKey('produtos.id'), nullable=True)
    quantity = Column(Integer, nullable=True, default=1)
    
    user = relationship('User', back_populates='shopping_cart_items')
    product = relationship('Produtos', back_populates='shopping_cart_items')