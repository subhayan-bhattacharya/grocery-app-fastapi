"""Module for python fixtures."""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

import application.sqlalchemy_models as sqlalchemy_models
from application.backend import instantiate_backend


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


@pytest.fixture()
def setup_database_and_add_user(database):
    """Set up the database and add an initial user."""
    sql_statements = [
        text(
            "INSERT INTO user (email, name, lastName, password) "
            "VALUES (:email, :name, :lastName, :password)"
        ).params(
            email="user1@example.com",
            name="user1",
            lastName="lastname1",
            # Using the function generate_password_hash is important
            # before sending the password because the route uses the function
            # check_password_hash to compare the passwords
            password=generate_password_hash("password"),
        )
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)
    instantiate_backend(sqlite_db_path=database_file_path_str)
    yield database_file_path_str
