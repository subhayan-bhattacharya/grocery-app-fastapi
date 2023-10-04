"""Module for supermarket backend."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import exc

from application.backend import BackendException
from application.models import SuperMarketWithId, SuperMarket
from application.sqlalchemy_models import GrocerySupermarket


class SupermarketBackend:
    """Supermarket backend class."""

    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    def add_a_supermarket(self, supermarket: SuperMarket) -> SuperMarketWithId:
        """Add a supermarket into the database."""
        with self.session_maker.begin() as session:
            try:
                new_supermarket = GrocerySupermarket(**supermarket.model_dump())
                session.add(new_supermarket)
                session.flush()  # unless we do this the exception is not caught !
                return SuperMarketWithId.model_validate(
                    {"id": new_supermarket.id, "name": new_supermarket.name}
                )
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a supermarket with the name : {supermarket.name}"
                )

    def get_the_list_of_supermarkets(self) -> list[SuperMarketWithId]:
        """Get the list of supermarkets from database."""
        supermarkets = []
        with self.session_maker.begin() as session:
            for db_entry in session.query(GrocerySupermarket).all():
                supermarkets.append(
                    SuperMarketWithId.model_validate(
                        {"id": db_entry.id, "name": db_entry.name}
                    )
                )
        return supermarkets
