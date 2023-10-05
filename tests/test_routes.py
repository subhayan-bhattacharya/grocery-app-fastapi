"""Test file for routes."""

from fastapi.testclient import TestClient
from sqlalchemy import text

from application import app


#
# def test_get_not_purchased_entries(database):
#     """Test that the route /entries works as expected."""
#     # sql statements to set up the database before the test
#     sql_statements = [
#         text(
#             "INSERT INTO user (email, name, lastName, password) "
#             "VALUES (:email, :name, :lastName, :password)"
#         ).params(
#             email="user1@example.com",
#             name="user1",
#             lastName="lastname1",
#             password="password1",
#         ),
#         text("INSERT INTO grocery_supermarket (name) " "VALUES (:name)").params(
#             name="Edeka"
#         ),
#         text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
#             item_name="Bananas"
#         ),
#         text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
#             item_name="Rice"
#         ),
#         text("INSERT INTO grocery_item (item_name) " "VALUES (:item_name)").params(
#             item_name="Milk"
#         ),
#         text(
#             "INSERT INTO grocery_category (name, description) "
#             "VALUES (:name, :description)"
#         ).params(
#             name="Fruits",
#             description="Fruits",
#         ),
#         text(
#             "INSERT INTO grocery_category (name, description) "
#             "VALUES (:name, :description)"
#         ).params(
#             name="Grains, Pasta and Rice",
#             description="Grains, Pasta and Rice",
#         ),
#         text(
#             "INSERT INTO grocery_category (name, description) "
#             "VALUES (:name, :description)"
#         ).params(
#             name="Dairy",
#             description="Dairy Products",
#         ),
#         text(
#             "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
#             "VALUES (:item_id, :category_id, :quantity, :purchased)"
#         ).params(item_id=1, category_id=1, quantity=1, purchased=0),
#         text(
#             "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
#             "VALUES (:item_id, :category_id, :quantity, :purchased)"
#         ).params(item_id=2, category_id=2, quantity=1, purchased=0),
#         text(
#             "INSERT INTO grocery_entries (item_id, category_id, quantity, purchased) "
#             "VALUES (:item_id, :category_id, :quantity, :purchased)"
#         ).params(item_id=3, category_id=3, quantity=1, purchased=0),
#         text(
#             "UPDATE grocery_entries SET purchased = :purchased_updated WHERE id = :id"
#         ).params(purchased_updated=1, id=1),
#     ]
#     add_and_execute_statements, database_file_path_str = database
#     add_and_execute_statements(sql_statements)
#
#     instantiate_backend(sqlite_db_path=database_file_path_str)
#     client = TestClient(app)
#     response = client.get("/entries")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)
#     for entry in response.json():
#         assert entry["item_name"] in ["Rice", "Milk"]



def test_adding_a_user_to_the_database(database):
    """Test that a user could be added to the database."""
    _, database_file_path_str = database
    instantiate_backend(sqlite_db_path=database_file_path_str)
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


def test_adding_a_user_twice_fails(setup_database_and_add_user):
    """Test that the same user cannot be added twice."""
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


def test_logging_a_user(setup_database_and_add_user):
    """Test that a user can be logged in."""
    client = TestClient(app)
    response = client.post(
        "/login", data={"username": "user1@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_logging_a_user_with_wrong_password_fails(setup_database_and_add_user):
    """Test logging a user in with wrong password fails."""
    client = TestClient(app)
    response = client.post(
        "/login",
        data={
            "username": "user1@example.com",
            "password": "password1",  # wrong password
        },
    )
    assert response.status_code == 401


def test_adding_a_bucket_for_a_user(setup_database_and_add_user):
    """Test adding a bucket for the user."""
    database_file_path_str = setup_database_and_add_user
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
    setup_database_and_add_user,
):
    """Adding a bucket should fail for a non authenticated user."""
    client = TestClient(app)
    response = client.post(
        "/buckets",
        json={"name": "Groceries"},
    )
    assert response.status_code == 401
