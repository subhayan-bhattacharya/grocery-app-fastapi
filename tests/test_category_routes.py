"""Test for the category routes."""
from fastapi.testclient import TestClient
from sqlalchemy import text

from application import app
from application.app_routes.category_routes import get_category_backend


def test_adding_a_category(database, monkeypatch, execute_queries):
    """Test that a category can be added to the database."""
    _, database_file_path_str = database
    execute_sql_and_get_results = execute_queries
    # The below two lines are essential for the tests to work
    get_category_backend.cache_clear()
    monkeypatch.setenv('DB_FILE', database_file_path_str)
    client = TestClient(app)
    response = client.post(
        "/categories", json={"name": "Test_category", "description": "Test category"}
    )
    assert response.status_code == 201
    results = execute_sql_and_get_results(
        database_file_path=database_file_path_str.split("/")[-1],
        statement="select * from grocery_category where name = ?",
        params=("Test_category",),
    )
    assert len(results) == 1
    assert results[0][1] == "Test_category"


def test_adding_a_category_twice_fails(database, monkeypatch):
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
    # The below two lines are essential for the tests to work
    get_category_backend.cache_clear()
    monkeypatch.setenv('DB_FILE', database_file_path_str)
    client = TestClient(app)
    response = client.post(
        "/categories", json={"name": "Fruits", "description": "Fruits"}
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "There is already a category with the name : Fruits"
    )


def test_querying_list_of_categories(database, monkeypatch):
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

    # The below two lines are essential for the tests to work
    get_category_backend.cache_clear()
    monkeypatch.setenv('DB_FILE', database_file_path_str)
    client = TestClient(app)
    response = client.get("/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    supermarket_entries = [entry["name"] for entry in response.json()]
    assert sorted(supermarket_entries) == sorted(["Spices", "Fruits"])
