"""Module for backend functions which deals with categories."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import exc

from application.models import Category, CategoryWithId
from application.sqlalchemy_models import GroceryCategory
from application.backend import BackendException, ResourceNotFound


class BackendCategory:
    """Backend category class."""
    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    def add_a_new_category(self, category: Category) -> CategoryWithId:
        """Add a new category."""
        with self.session_maker.begin() as session:
            try:
                new_category = GroceryCategory(**category.model_dump())
                session.add(new_category)
                session.flush()  # unless we do this the exception is not caught !
                return CategoryWithId.model_validate(
                    {
                        "id": new_category.id,
                        "name": new_category.name,
                        "description": new_category.description,
                    }
                )
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a category with the name : {category.name}"
                )

    def get_all_the_categories(self) -> list[CategoryWithId]:
        """Get the list of categories."""
        categories = []
        with self.session_maker.begin() as session:
            for db_entry in session.query(GroceryCategory).all():
                categories.append(
                    CategoryWithId.model_validate(
                        {
                            "id": db_entry.id,
                            "name": db_entry.name,
                            "description": db_entry.description
                        }
                    )
                )
        return categories

    def get_a_single_category(self, category_id: int) -> CategoryWithId:
        """Get a single category."""
        with self.session_maker.begin() as session:
            db_entry = session.query(GroceryCategory).filter_by(id=category_id).first()
            if db_entry is None:
                raise ResourceNotFound(f"No category found with the id {category_id}")
            return CategoryWithId.model_validate(
                {
                    "id": db_entry.id,
                    "name": db_entry.name,
                    "description": db_entry.description,
                }
            )

    def delete_a_single_category(self, category_id: int):
        """Delete a single category."""
        with self.session_maker.begin() as session:
            deleted = session.query(GroceryCategory).filter_by(id=category_id).delete()
            if deleted == 0:
                raise ResourceNotFound(f"No category found with the id {category_id}")
