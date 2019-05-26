from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    """kategorie"""

    __tablename__ = 'category'
    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    item = relationship('Item')

    def __init__(self, name):
        self.name = name


class Item(Base):
    """itemy"""

    __tablename__ = 'item'
    id = Column(Integer, Sequence('item_id_seq'), primary_key=True)
    cat_id = Column(Integer, ForeignKey('category.id'))
    description = Column(String(100), nullable=False, unique=True)
    title = Column(String(40), nullable=False, unique=True)

    def __init__(self, cat_id, description, title):
        self.cat_id = cat_id
        self.description = description
        self.title = title
