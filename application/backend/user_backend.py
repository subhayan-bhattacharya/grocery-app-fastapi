"""Code related to backend interactions for user."""
from sqlalchemy import exc
from sqlalchemy.orm.session import sessionmaker

from application.backend import BackendException
from application.models import Bucket, BucketWithId, UserModel, UserModelWithId
from application.sqlalchemy_models import GroceryBucket, User


class IncorrectCredentials(Exception):
    pass


class UserBackend:
    """User backend class."""

    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    def add_a_new_user(self, user: UserModel) -> UserModelWithId:
        """Add a new user to the database."""
        with self.session_maker.begin() as session:
            try:
                user.password = user.password.get_secret_value()
                new_user = User(**user.model_dump())
                session.add(new_user)
                session.flush()  # unless we do this the exception is not caught !
                return UserModelWithId.model_validate(
                    {
                        "id": new_user.id,
                        "name": new_user.name,
                        "lastName": new_user.lastName,
                        "email": new_user.email,
                        # this is fine since pydantic with serialize it well when displaying
                        "password": new_user._password,
                    }
                )
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a user with the name : "
                    f"{new_user.name} and email : {new_user.email}"
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
                return BucketWithId.model_validate(
                    {
                        "id": new_bucket.id,
                        "name": new_bucket.name,
                    }
                )
            except exc.IntegrityError as error:
                session.rollback()
                raise BackendException(
                    f"There is already a bucket with the name : "
                    f"{bucket.name} and for the user : {user.name}"
                )

    def get_all_buckets_for_user(self, user: UserModelWithId) -> list[BucketWithId]:
        """Get all the buckets for the user."""
        buckets = []
        with self.session_maker.begin() as session:
            for db_entry in (
                session.query(GroceryBucket).filter_by(user_id=user.id).all()
            ):
                buckets.append(
                    BucketWithId.model_validate(
                        {"id": db_entry.id, "name": db_entry.name}
                    )
                )
        return buckets
