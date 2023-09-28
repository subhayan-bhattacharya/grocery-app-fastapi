"""Test file for routes."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import application.sqlalchemy_models as sqlalchemy_models
from application import app
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


def test_get_not_purchased_entries(database):
    """Test that the route /entries works as expected."""
    # sql statements to set up the database before the test
    sql_statements = [
        text(
            "INSERT INTO user (user_email, user_name, user_last_name, password) "
            "VALUES (:user_email, :user_name, :user_last_name, :password)"
        ).params(
            user_email="user1@example.com",
            user_name="user1",
            user_last_name="lastname1",
            password="password1",
        ),
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Edeka"
        ),
        text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
            item_name="Bananas"
        ),
        text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
            item_name="Rice"
        ),
        text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
            item_name="Milk"
        ),
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Fruits",
            description="Fruits",
        ),
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Grains, Pasta and Rice",
            description="Grains, Pasta and Rice",
        ),
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Dairy",
            description="Dairy Products",
        ),
        text(
            "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
            "VALUES (:item_id, :category_id, :quantity, :purchased)"
        ).params(item_id=1, category_id=1, quantity=1, purchased=0),
        text(
            "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
            "VALUES (:item_id, :category_id, :quantity, :purchased)"
        ).params(item_id=2, category_id=2, quantity=1, purchased=0),
        text(
            "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
            "VALUES (:item_id, :category_id, :quantity, :purchased)"
        ).params(item_id=3, category_id=3, quantity=1, purchased=0),
        text(
            "UPDATE grocery_entries SET purchased = :purchased_updated WHERE id = :id"
        ).params(purchased_updated=1, id=1),
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.get("/entries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for entry in response.json():
        assert entry["item_name"] in ["Rice", "Milk"]


def test_adding_a_supermarket(database):
    """Test that a supermarket can be added to the database."""
    _, database_file_path_str = database
    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.post("/supermarkets", json={"name": "Edeka"})
    assert response.status_code == 201
    from application.backend import BACKEND

    assert BACKEND.get_the_list_of_supermarkets()[0].name == "Edeka"


def test_adding_a_supermarket_twice_fails(database):
    """Test adding a supermarket twice fails."""
    sql_statements = [
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Edeka"
        )
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.post("/supermarkets", json={"name": "Edeka"})
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "There is already a supermarket with the name : Edeka"
    )


def test_querying_list_of_supermarkets(database):
    """Test querying list of supermarkets."""
    sql_statements = [
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Edeka"
        ),
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Aldi"
        ),
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.get("/supermarkets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    supermarket_entries = [entry["name"] for entry in response.json()]
    assert sorted(supermarket_entries) == sorted(["Aldi", "Edeka"])


def test_adding_a_category(database):
    """Test that a category can be added to the database."""
    _, database_file_path_str = database
    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.post(
        "/categories", json={"name": "Test_category", "description": "Test category"}
    )
    assert response.status_code == 201


def test_adding_a_category_twice_fails(database):
    """Test adding a category twice fails."""
    sql_statements = [
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Fruits",
            description="Fruits",
        )
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)
    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.post(
        "/categories", json={"name": "Fruits", "description": "Fruits"}
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "There is already a category with the name : Fruits"
    )


def test_querying_list_of_categories(database):
    """Test querying list of categories."""
    sql_statements = [
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Fruits",
            description="Fruits",
        ),
        text(
            "INSERT INTO grocery_category (name, description) "
            "VALUES (:name, :description)"
        ).params(
            name="Spices",
            description="Spices",
        ),
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    instantiate_backend(sqlite_db_path=database_file_path_str)
    client = TestClient(app)
    response = client.get("/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    supermarket_entries = [entry["name"] for entry in response.json()]
    assert sorted(supermarket_entries) == sorted(["Spices", "Fruits"])
