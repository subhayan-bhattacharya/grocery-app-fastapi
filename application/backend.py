"""Module for code which interacts with the database."""
from typing import Union

from sqlalchemy import create_engine, exc
from sqlalchemy.orm.session import sessionmaker

from application.models import (Bucket, Category, Entries, SuperMarket,
                                UserModel, UserModelWithId)
from application.sqlalchemy_models import (GroceryBucket, GroceryCategory,
                                           GroceryEntries, GroceryItem,
                                           GrocerySupermarket, User)

BACKEND: Union["Backend", None] = None


class BackendException(Exception):
    pass


class IncorrectCredentials(Exception):
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

    def add_a_new_user(self, user: UserModel):
        """Add a new user to the database."""
        with self.session_maker.begin() as session:
            try:
                user.password = user.password.get_secret_value()
                new_user = User(**user.model_dump())
                session.add(new_user)
                session.flush()  # unless we do this the exception is not caught !
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a user with the name : "
                    f"{new_user.name} and email : {new_user.email}"
                )
        with self.session_maker.begin() as new_session:
            db_entry = new_session.query(User).filter_by(email=user.email).first()
            return UserModel.model_validate(
                {
                    "name": db_entry.name,
                    "lastName": db_entry.lastName,
                    "email": db_entry.email,
                    # this is fine since pydantic with serialize it well when displaying
                    "password": db_entry._password,
                }
            )

    def get_a_user(self, email: str) -> UserModelWithId:
        """Get a user from the database using the email."""
        with self.session_maker.begin() as new_session:
            user_in_db = new_session.query(User).filter_by(email=email).first()
            if user_in_db is not None:
                return UserModelWithId.model_validate(
                    {
                        "id": user_in_db.id,
                        "name": user_in_db.name,
                        "lastName": user_in_db.lastName,
                        "email": user_in_db.email,
                        # this is fine since pydantic with serialize it well when displaying
                        "password": user_in_db._password,
                    }
                )
            raise IncorrectCredentials("Wrong user name or password!.")

    def check_password_of_user(self, user: UserModel, password: str) -> None:
        """Check the password of the user is correct."""
        with self.session_maker.begin() as session:
            user_in_db = session.query(User).filter_by(email=user.email).first()
            if not user_in_db.verify_password(password=password):
                raise IncorrectCredentials("Wrong user name or password!.")

    def create_a_grocery_bucket(self, bucket: Bucket, user: UserModelWithId) -> Bucket:
        """Create a bucket in the database."""
        with self.session_maker.begin() as session:
            try:
                new_bucket = GroceryBucket(**bucket.model_dump() | {"user_id": user.id})
                session.add(new_bucket)
                session.flush()  # unless we do this the exception is not caught !
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a bucket with the name : "
                    f"{bucket.name} and for the user : {user.name}"
                )
        with self.session_maker.begin() as new_session:
            db_entry = (
                new_session.query(GroceryBucket)
                .filter_by(user_id=user.id, name=bucket.name)
                .first()
            )
            return Bucket.model_validate(
                {
                    "name": db_entry.name,
                }
            )

    def get_all_buckets_for_user(self, user: UserModelWithId) -> list[Bucket]:
        """Get all the buckets for the user."""
        buckets = []
        with self.session_maker.begin() as session:
            for db_entry in (
                session.query(GroceryBucket).filter_by(user_id=user.id).all()
            ):
                buckets.append(Bucket.model_validate({"name": db_entry.name}))
        return buckets


def instantiate_backend(sqlite_db_path: str):
    """Instantiates the backend."""
    global BACKEND
    engine = create_engine(sqlite_db_path)
    session_maker = sessionmaker(engine)
    print("Instantiating backend....!")
    BACKEND = Backend(session_maker=session_maker)
