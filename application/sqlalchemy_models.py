"""File which creates the database structure for sqlalchemy models."""
import datetime
import os
import pathlib

from dotenv import load_dotenv
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, DateTime, Integer

Base = declarative_base()


class User(Base):
    """User class for ORM."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    user_email = Column(String(30), index=True, nullable=False, unique=True)
    user_name = Column(String(30), nullable=False, unique=False)
    user_last_name = Column(String(30), nullable=False, unique=False)
    password = Column(String(30), nullable=False)


class Supermarket(Base):
    """Store class for ORM."""

    __tablename__ = "supermarket"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), nullable=False, unique=True)


class GroceryItem(Base):
    """GroceryItem class for ORM."""

    __tablename__ = "grocery_item"

    id = Column(Integer, primary_key=True, nullable=False)
    item_name = Column(String(20), index=True, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("grocery_category.id"))


class GroceryCategory(Base):
    """Class for grocery category."""

    __tablename__ = "grocery_category"

    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(20), index=True, nullable=False, unique=True)
    category_description = Column(String(50))


class GroceryEntries(Base):
    """Class for grocery entries ORM."""

    __tablename__ = "grocery_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    # There will be an entry into the item table with the category when
    # this table gets populated
    item_id = Column(Integer, ForeignKey("grocery_item.id"))
    category_id = Column(Integer, ForeignKey("grocery_category.id"))
    quantity = Column(Integer, default=1, nullable=False)
    description = Column(String(50))
    purchased = Column(Boolean)


class GroceryPurchaseHistory(Base):
    """Class for grocery purchase history ORM."""

    __tablename__ = "grocery_purchase_history"

    id = Column(Integer, primary_key=True, nullable=False)
    grocery_entry_id = Column(Integer, ForeignKey("grocery_entries.id"))
    date_purchased = Column(DateTime, default=datetime.datetime.utcnow)
    supermarket_id = Column(Integer, ForeignKey("supermarket.id"))
    user_id = Column(Integer, ForeignKey("user.id"))


if __name__ == "__main__":
    # load the environment from the file app.env in the project directory
    basedir = pathlib.Path(__file__).parent.parent
    load_dotenv(basedir / "app.env")
    engine = create_engine(os.getenv("DB_FILE"), echo=True)
    Base.metadata.create_all(engine)
