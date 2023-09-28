"""Module for code which interacts with the database."""
from typing import Union

from sqlalchemy import create_engine, exc
from sqlalchemy.orm.session import sessionmaker

from application.models import Category, Entries, SuperMarket
from application.sqlalchemy_models import (
    GroceryCategory,
    GroceryEntries,
    GroceryItem,
    GrocerySupermarket,
)

BACKEND: Union["Backend", None] = None


class BackendException(Exception):
    pass


class Backend:
    """Backend class for database interaction."""

    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    def get_not_purchased_grocery_entries(self) -> list[Entries]:
        """Function to get not purchased grocery entries."""
        entries = []
        with self.session_maker.begin() as session:
            for entry in (
                session.query(
                    GroceryEntries.id,
                    GroceryItem.item_name,
                    GroceryCategory.name,
                    GroceryEntries.quantity,
                    GroceryEntries.description,
                    GroceryEntries.purchased,
                )
                .join(GroceryItem, GroceryItem.id == GroceryEntries.item_id)
                .join(GroceryCategory, GroceryCategory.id == GroceryEntries.category_id)
                .filter(GroceryEntries.purchased == 0)
            ):
                entries.append(
                    Entries.model_validate(
                        {
                            "item_name": entry[1],
                            "category_name": entry[2],
                            "quantity": entry[3],
                            "description": entry[4],
                            "purchased": entry[5],
                        }
                    )
                )
        return entries

    def add_a_supermarket(self, supermarket: SuperMarket) -> SuperMarket:
        """Add a supermarket into the database."""
        with self.session_maker.begin() as session:
            try:
                new_supermarket = GrocerySupermarket(**supermarket.model_dump())
                session.add(new_supermarket)
                session.flush()  # unless we do this the exception is not caught !
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a supermarket with the name : {supermarket.name}"
                )
        with self.session_maker.begin() as new_session:
            db_entry = (
                new_session.query(GrocerySupermarket)
                .filter_by(name=supermarket.name)
                .first()
            )
            return SuperMarket.model_validate({"name": db_entry.name})

    def get_the_list_of_supermarkets(self) -> list[SuperMarket]:
        """Get the list of supermarkets from database."""
        supermarkets = []
        with self.session_maker.begin() as session:
            for db_entry in session.query(GrocerySupermarket).all():
                supermarkets.append(SuperMarket.model_validate({"name": db_entry.name}))
        return supermarkets

    def add_a_new_category(self, category: Category) -> Category:
        """Add a new category."""
        with self.session_maker.begin() as session:
            try:
                new_category = GroceryCategory(**category.model_dump())
                session.add(new_category)
                session.flush()  # unless we do this the exception is not caught !
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a category with the name : {category.name}"
                )

        with self.session_maker.begin() as new_session:
            db_entry = (
                new_session.query(GroceryCategory).filter_by(name=category.name).first()
            )
            return Category.model_validate(
                {
                    "name": db_entry.name,
                    "description": db_entry.description,
                }
            )

    def get_all_the_categories(self) -> list[Category]:
        """Get the list of categories."""
        categories = []
        with self.session_maker.begin() as session:
            for db_entry in session.query(GroceryCategory).all():
                categories.append(
                    Category.model_validate(
                        {"name": db_entry.name, "description": db_entry.description}
                    )
                )
        return categories


def instantiate_backend(sqlite_db_path: str):
    """Instantiates the backend."""
    global BACKEND
    engine = create_engine(sqlite_db_path)
    session_maker = sessionmaker(engine)
    print("Instantiating backend....!")
    BACKEND = Backend(session_maker=session_maker)
