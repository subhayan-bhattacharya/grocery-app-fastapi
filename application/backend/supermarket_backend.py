"""Module for supermarket backend."""
from sqlalchemy import exc
from sqlalchemy.orm.session import sessionmaker

from application.backend import BackendException, ResourceNotFound
from application.models import SuperMarket, SuperMarketWithId
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

    def delete_a_supermarket(self, supermarket_id: int):
        """Delete a supermarket by its id."""
        with self.session_maker.begin() as session:
            deleted = (
                session.query(GrocerySupermarket).filter_by(id=supermarket_id).delete()
            )
            if deleted == 0:
                raise ResourceNotFound(
                    f"No Supermarket found with the id {supermarket_id}"
                )

    def get_a_single_supermarket(self, supermarket_id: int) -> SuperMarketWithId:
        """Get the details about a single supermarket."""
        with self.session_maker.begin() as session:
            db_entry = (
                session.query(GrocerySupermarket).filter_by(id=supermarket_id).first()
            )
            if db_entry is None:
                raise ResourceNotFound(
                    f"No supermarket found with the id {supermarket_id}"
                )
            return SuperMarketWithId.model_validate(
                {
                    "id": db_entry.id,
                    "name": db_entry.name,
                }
            )
