from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base

class Servicos(Base):
    __tablename__ = 'servicos'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)