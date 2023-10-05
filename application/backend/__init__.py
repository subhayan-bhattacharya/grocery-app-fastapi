"""Module for code which interacts with the database."""
from typing import Any, Union

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

BACKEND: Union["Backend", None] = None


class BackendException(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


def instantiate_backend(sqlite_db_path: str, backend_class: type) -> Any:
    """Instantiates the backend."""
    print(
        f"Instantiating backend...{backend_class} and database file path : {sqlite_db_path}!"
    )
    engine = create_engine(sqlite_db_path)
    session_maker = sessionmaker(engine)
    return backend_class(session_maker=session_maker)
