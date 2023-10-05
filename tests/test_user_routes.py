"""Test the routes relating to user interaction."""
from fastapi.testclient import TestClient

from application import app
from application.app_routes.user_routes import get_user_backend


def test_adding_a_user_to_the_database(database, monkeypatch, execute_queries):
    """Test that a user could be added to the database."""
    _, database_file_path_str = database
    execute_sql_and_get_results = execute_queries
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", database_file_path_str)
    client = TestClient(app)
    response = client.post(
        "/users",
        json={
            "name": "Subhayan",
            "email": "test_user@gmail.com",
            "lastName": "Bhattacharya",
            "password": "password",
        },
    )
    assert response.status_code == 201
    results = execute_sql_and_get_results(
        database_file_path=database_file_path_str.split("/")[-1],
        statement="select * from user where email = ?",
        params=("test_user@gmail.com",),
    )
    assert len(results) == 1
    assert results[0][1] == "test_user@gmail.com"


def test_adding_a_user_twice_fails(setup_database_and_add_user, monkeypatch):
    """Test that the same user cannot be added twice."""
    db_file_path = setup_database_and_add_user
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", db_file_path)
    client = TestClient(app)
    response = client.post(
        "/users",
        json={
            "name": "user1",
            "email": "user1@example.com",
            "lastName": "lastname1",
            "password": "password",
        },
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "There is already a user with the name : user1 and email : user1@example.com"
    )


def test_logging_a_user(setup_database_and_add_user, monkeypatch):
    """Test that a user can be logged in."""
    db_file_path = setup_database_and_add_user
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", db_file_path)
    client = TestClient(app)
    response = client.post(
        "/login", data={"username": "user1@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_logging_a_user_with_wrong_password_fails(
    setup_database_and_add_user, monkeypatch
):
    """Test logging a user in with wrong password fails."""
    db_file_path = setup_database_and_add_user
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", db_file_path)
    client = TestClient(app)
    response = client.post(
        "/login",
        data={
            "username": "user1@example.com",
            "password": "password1",  # wrong password
        },
    )
    assert response.status_code == 401


def test_adding_a_bucket_for_a_user(
    setup_database_and_add_user, execute_queries, monkeypatch
):
    """Test adding a bucket for the user."""
    database_file_path_str = setup_database_and_add_user
    execute_sql_and_get_results = execute_queries
    db_file_path = setup_database_and_add_user
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", db_file_path)
    client = TestClient(app)
    response = client.post(
        "/login", data={"username": "user1@example.com", "password": "password"}
    )
    access_token = response.json()["access_token"]
    new_response = client.post(
        "/buckets",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={"name": "Groceries"},
    )
    assert new_response.status_code == 201
    results = execute_sql_and_get_results(
        database_file_path=database_file_path_str.split("/")[-1],
        statement="select gb.* from grocery_bucket as gb join user as u "
        "on gb.user_id = u.id where u.email = ? and gb.name = ?",
        params=("user1@example.com", "Groceries"),
    )
    assert len(results) == 1
    assert results[0][2] == "Groceries"


def test_adding_a_bucket_for_user_fails_for_non_authenticated_user(
    setup_database_and_add_user, monkeypatch
):
    """Adding a bucket should fail for a non authenticated user."""
    db_file_path = setup_database_and_add_user
    get_user_backend.cache_clear()
    monkeypatch.setenv("DB_FILE", db_file_path)
    client = TestClient(app)
    response = client.post(
        "/buckets",
        json={"name": "Groceries"},
    )
    assert response.status_code == 401
