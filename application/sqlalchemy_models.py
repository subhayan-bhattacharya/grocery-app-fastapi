"""File which creates the database structure for sqlalchemy models."""
import datetime
import os
import pathlib

from dotenv import load_dotenv
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import Boolean, DateTime, Integer
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()


class User(Base):
    """User class for ORM."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(30), index=True, nullable=False, unique=True)
    name = Column(String(30), nullable=False, unique=False)
    lastName = Column(String(30), nullable=False, unique=False)
    _password = Column("password", String(256), nullable=False)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)


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
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="user_id_name_constraint"),
    )


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
    name = Column(String(20), index=True, nullable=False, unique=True)
    description = Column(String(50))


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
