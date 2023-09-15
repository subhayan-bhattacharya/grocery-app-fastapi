"""File which creates the database structure for sqlalchemy models."""
import datetime

from sqlalchemy import Column, String, create_engine
from sqlalchemy.types import DateTime, Integer
from sqlalchemy.schema import ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine('sqlite:///grocery_app.db', echo=True)


class User(Base):
    """User class for ORM."""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    user_email = Column(String(30), index=True, nullable=False, unique=True)
    user_name = Column(String(30), nullable=False, unique=False)
    user_last_name = Column(String(30), nullable=False, unique=False)


class Supermarket(Base):
    """Store class for ORM."""
    __tablename__ = 'supermarket'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), nullable=False, unique=True)


class GroceryItem(Base):
    """GroceryItem class for ORM."""
    __tablename__ = 'grocery_item'

    id = Column(Integer, primary_key=True, nullable=False)
    item_name = Column(String(20), index=True, nullable=False, unique=True)


class GroceryCategory(Base):
    """Class for grocery category."""
    __tablename__ = 'grocery_category'

    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(20), index=True, nullable=False, unique=True)
    category_description = Column(String(50))


class GroceryItemCategory(Table):
    """Class for linking item with category."""
    __tablename__ = "groceryitem_category"

    category_id = Column(Integer, ForeignKey('grocery_category.id'))
    item_id = Column(Integer, ForeignKey('grocery_item.id'))


class GroceryEntries(Base):
    """Class for grocery entries ORM."""
    __tablename__ = 'grocery_entries'

    id = Column(Integer, primary_key=True, nullable=False)
    item_id = Column(Integer, ForeignKey('grocery_item.id'))
    category_id = Column(Integer, ForeignKey('grocery_category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    supermarket_id = Column(Integer, ForeignKey('supermarket.id'))
    date_purchased = Column(DateTime, default=datetime.datetime.utcnow)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
