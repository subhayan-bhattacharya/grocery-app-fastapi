"""Module for code which interacts with the database."""
from typing import Union, Any

from sqlalchemy import create_engine, exc
from sqlalchemy.orm.session import sessionmaker

from application.models import (
    Bucket,
    BucketWithId,
    Category,
    CategoryWithId,
    Entries,
    SuperMarket,
    SuperMarketWithId,
    UserModel,
    UserModelWithId,
    BucketItemEntry,
)
from application.sqlalchemy_models import (
    GroceryBucket,
    GroceryCategory,
    GroceryEntries,
    GroceryItem,
    GrocerySupermarket,
    User,
)

BACKEND: Union["Backend", None] = None


class BackendException(Exception):
    pass


class ResourceNotFound(Exception):
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

    def add_a_new_grocery_item(self, name: str, category_id: int) -> int:
        """Add a new grocery item to the database."""
        with self.session_maker.begin() as session:
            try:
                item = GroceryItem(name=name, category_id=category_id)
                session.add(item)
                session.flush()
                return item.id
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a grocery item with the name {name}"
                )

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

    def create_a_grocery_bucket(
        self, bucket: Bucket, user: UserModelWithId
    ) -> BucketWithId:
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
            return BucketWithId.model_validate(
                {
                    "name": db_entry.name,
                }
            )

    def get_all_buckets_for_user(self, user: UserModelWithId) -> list[BucketWithId]:
        """Get all the buckets for the user."""
        buckets = []
        with self.session_maker.begin() as session:
            for db_entry in (
                session.query(GroceryBucket).filter_by(user_id=user.id).all()
            ):
                buckets.append(BucketWithId.model_validate({"name": db_entry.name}))
        return buckets

    def delete_a_user_bucket(self, user: UserModelWithId, bucket_name: str):
        """Delete a bucket for the user."""
        pass

    # def add_a_grocery_entry(self, bucket_id: int, entry: BucketItemEntry):
    #     """Add an entry to grocery bucket."""
    #     if entry.item_id is None:
    #         # Since the item id is not supplied there is nothing existing in the
    #         # database.
    #         try:
    #             if entry.category_id is None:
    #                 category = self.add_a_new_category(
    #                     Category.model_validate(
    #                         {"name": entry.category_name}
    #                     )
    #                 )
    #                 item = self.add_a_new_grocery_item(
    #                     name=entry.name,
    #                     category_id=category.
    #                 )
    #     if entry.category_id is None:
    #         try:
    #             category = self.add_a_new_category(
    #                 Category.model_validate(
    #                     {"name": entry.category_name}
    #                 )
    #             )
    #         except BackendException as error:
    #             raise error


def instantiate_backend(sqlite_db_path: str, backend_class: type) -> Any:
    """Instantiates the backend."""
    engine = create_engine(sqlite_db_path)
    session_maker = sessionmaker(engine)
    print(f"Instantiating backend...{backend_class}!")
    return backend_class(session_maker=session_maker)

