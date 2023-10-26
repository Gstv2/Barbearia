from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'user'

    email = Column(String(100), primary_key=True)
    telefone = Column(Integer, nullable=False)
    nome = Column(String(50), nullable=False)
    senha = Column(String(20), nullable=False)
