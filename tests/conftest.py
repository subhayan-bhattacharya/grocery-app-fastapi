"""Module for python fixtures."""
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import application.sqlalchemy_models as sqlalchemy_models


@pytest.fixture()
def database(request):
    # Define the database file path
    db_file_path = os.path.join(request.config.rootdir, "test_database.db")

    # Create a SQLite database engine
    database_file_path_str = f"sqlite:///{db_file_path}"
    engine = create_engine(database_file_path_str)

    # Create the tables based on your SQLAlchemy models
    sqlalchemy_models.Base.metadata.create_all(engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    def remove_database_file():
        session.close()
        os.remove(db_file_path)

    request.addfinalizer(remove_database_file)

    def add_and_execute_sql_statements(statements):
        for statement in statements:
            session.execute(statement)
        session.commit()

    yield add_and_execute_sql_statements, database_file_path_str
