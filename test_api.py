import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

# — your existing create_test_db fixture and client —
@pytest.fixture(autouse=True)
def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_and_login():
    r = client.post("/register", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"
    user_id = data["id"]

    # Login
    r = client.post("/login", data={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

# ── Auth failures ──────────────────────────────────────────

def test_register_duplicate_username():
    client.post("/register", json={"username": "bob", "password": "pwd"})
    r = client.post("/register", json={"username": "bob", "password": "pwd"})
    assert r.status_code == 400
    assert "already taken" in r.json()["detail"]

def test_login_wrong_password():
    client.post("/register", json={"username": "carol", "password": "secret"})
    r = client.post("/login", data={"username": "carol", "password": "wrong"})
    assert r.status_code == 401

# ── Create Book ────────────────────────────────────────────

def test_create_book_unauthenticated():
    r = client.post("/books/", json={
        "book_name":  "Test",
        "description":"desc",
        "pages":       10,
        "author":     "A",
        "publisher":  "P"
    })
    assert r.status_code == 401

def test_create_and_get_books_authenticated():
    # register & login
    client.post("/register", json={"username": "dave", "password": "pw"})
    login = client.post("/login", data={"username": "dave", "password": "pw"}).json()
    token = login["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create two books
    for name in ("Book1","Book2"):
        r = client.post("/books/", json={
            "book_name":  name,
            "description":"desc",
            "pages":      50,
            "author":     "Auth",
            "publisher":  "Pub"
        }, headers=headers)
        assert r.status_code == 200
        assert r.json()["book_name"] == name

    # get books list
    r = client.get("/books/", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 2

def test_get_books_with_filter():
    # seed
    client.post("/register", json={"username": "ella", "password": "pw"})
    token = client.post("/login", data={"username": "ella","password":"pw"}).json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}

    # create two different authors
    client.post("/books/", json={
        "book_name":"X", "description":"", "pages":1, "author":"Alice","publisher":"P"
    }, headers=hdr)
    client.post("/books/", json={
        "book_name":"Y", "description":"", "pages":2, "author":"Bob","publisher":"P"
    }, headers=hdr)

    # filter by author=Alice
    r = client.get("/books/?author=Alice", headers=hdr)
    xs = [b["author"] for b in r.json()]
    assert xs == ["Alice"]

# ── Delete Book ────────────────────────────────────────────

def test_delete_book_unauthenticated():
    r = client.delete("/books/1")
    assert r.status_code == 401

def test_delete_nonexistent_book():
    client.post("/register", json={"username": "fay", "password": "pw"})
    token = client.post("/login", data={"username": "fay","password":"pw"}).json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}

    r = client.delete("/books/999", headers=hdr)
    assert r.status_code == 404

def test_delete_book_success():
    # setup
    client.post("/register", json={"username": "gary", "password": "pw"})
    token = client.post("/login", data={"username": "gary","password":"pw"}).json()["access_token"]
    hdr = {"Authorization": f"Bearer {token}"}
    # create
    book = client.post("/books/", json={
        "book_name": "ToDelete", "description":"", "pages":5, "author":"A","publisher":"B"
    }, headers=hdr).json()
    bid = book["id"]

    # delete
    r = client.delete(f"/books/{bid}", headers=hdr)
    assert r.status_code in (200,204)

    # verify gone
    r2 = client.get("/books/", headers=hdr)
    assert all(b["id"] != bid for b in r2.json())
