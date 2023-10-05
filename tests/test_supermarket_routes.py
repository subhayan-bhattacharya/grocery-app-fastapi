"""Routes for the supermarket."""
from fastapi.testclient import TestClient
from sqlalchemy import text

from application import app
from application.app_routes.supermarket_routes import get_supermarket_backend


def test_adding_a_supermarket(database, monkeypatch, execute_queries):
    """Test that a supermarket can be added to the database."""
    _, database_file_path_str = database
    execute_sql_and_get_results = execute_queries

    # The below two lines are essential for the tests to work
    get_supermarket_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", database_file_path_str)
    client = TestClient(app)
    response = client.post("/supermarkets", json={"name": "Edeka"})
    assert response.status_code == 201
    results = execute_sql_and_get_results(
        database_file_path=database_file_path_str.split("/")[-1],
        statement="select * from grocery_supermarket where name = ?",
        params=("Edeka",),
    )
    assert len(results) == 1
    assert results[0][1] == "Edeka"


def test_adding_a_supermarket_twice_fails(database, monkeypatch):
    """Test adding a supermarket twice fails."""
    sql_statements = [
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Edeka"
        )
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    # The below two lines are essential for the tests to work
    get_supermarket_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", database_file_path_str)
    client = TestClient(app)
    response = client.post("/supermarkets", json={"name": "Edeka"})
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "There is already a supermarket with the name : Edeka"
    )


def test_querying_list_of_supermarkets(database, monkeypatch):
    """Test querying list of supermarkets."""
    sql_statements = [
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Konsum"
        ),
        text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
            name="Aldi"
        ),
    ]
    add_and_execute_statements, database_file_path_str = database
    add_and_execute_statements(sql_statements)

    # The below two lines are essential for the tests to work
    get_supermarket_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", database_file_path_str)
    client = TestClient(app)
    response = client.get("/supermarkets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print(response.json())
    assert len(response.json()) == 2
    supermarket_entries = [entry["name"] for entry in response.json()]
    assert sorted(supermarket_entries) == sorted(["Aldi", "Konsum"])
