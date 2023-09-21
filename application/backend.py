"""Module for code which interacts with the database."""
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from application.models import Entries
from application.sqlalchemy_models import (GroceryCategory, GroceryEntries,
                                           GroceryItem)

BACKEND: Union["Backend", None] = None


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
                    GroceryCategory.category_name,
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


def instantiate_backend(sqlite_db_path: str):
    """Instantiates the backend."""
    global BACKEND
    engine = create_engine(sqlite_db_path, echo=True)
    session_maker = sessionmaker(engine)
    print("Instantiating backend....!")
    BACKEND = Backend(session_maker=session_maker)
