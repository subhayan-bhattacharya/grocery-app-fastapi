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


class GrocerySupermarket(Base):
    """Store class for ORM."""

    __tablename__ = "grocery_supermarket"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), nullable=False, unique=True)


class GroceryBucket(Base):
    """Store class for grocery bucket."""

    __tablename__ = "grocery_bucket"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class GroceryBucketAccess(Base):
    """Class for grocery access bucket."""

    __tablename__ = "grocery_bucket_access"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    bucket_id = Column(Integer, ForeignKey("grocery_bucket.id"))


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
    bucket_id = Column(Integer, ForeignKey("grocery_bucket.id"))
    # There will be an entry into the item table with the category when
    # this table gets populated
    item_id = Column(Integer, ForeignKey("grocery_item.id"))
    category_id = Column(Integer, ForeignKey("grocery_category.id"))
    quantity = Column(Integer, default=1, nullable=False)
    description = Column(String(50))
    purchased = Column(Boolean, default=False)


if __name__ == "__main__":
    # load the environment from the file app.env in the project directory
    basedir = pathlib.Path(__file__).parent.parent
    load_dotenv(basedir / "app.env")
    engine = create_engine(os.getenv("DB_FILE"), echo=True)
    Base.metadata.create_all(engine)
