# Importing internal modules
import os
from . import models                 # ORM models for tables
from .database import engine, SessionLocal  # DB engine and session factory
from . import schemas, crud         # Pydantic schemas and CRUD functions
from sqlalchemy.orm import Session  # For dependency-injected DB session
from fastapi import FastAPI, HTTPException, status, Depends  # Core FastAPI classes
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Auth system
from .auth import create_access_token, verify_token  # JWT handling
from typing import List             # For typing response as list
from .schemas import UserCreate, UserOut, TaskCreate, TaskOut, TaskUpdate  # Explicit schema imports
from .crud import create_user, get_user_by_username, create_task  # Common CRUD functions
from passlib.context import CryptContext  # For password hashing
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


# -------------------------
# App and config setup

app = FastAPI() 


# Mount the static directory
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

# Serve index.html at the root path
@app.get("/", response_class=HTMLResponse)
def read_index():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Password encryption context

# Creates all tables if they don't exist (executed once at startup)
models.Base.metadata.create_all(bind=engine)


# -------------------------
# Health check route

@app.get("/health")
def root():
    return {"message": "ARG API Server is running!"}

# -------------------------
# Database session dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# OAuth2 setup – FastAPI's token-based security dependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -------------------------
# USER AUTH: Register & Login

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with unique username
    """
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = create_user(db, user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    user = get_user_by_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# -------------------------
# User token validation

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validates token and returns the logged-in user
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------
# BOOK ROUTES


@app.post("/books/", response_model=schemas.BookOut)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Secured route
):
    return crud.create_book(db=db, book=book, user_id=current_user.id)

@app.get("/books/", response_model=List[schemas.BookOut])
def read_books(
    name: str = None,
    author: str = None,
    publisher: str = None,
    sort_by: str = "id",               # Sorting field
    sort_order: str = "asc",           # asc or desc
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_books(
        db=db,
        user_id=current_user.id,
        name=name,
        author=author,
        publisher=publisher,
        sort_by=sort_by,
        sort_order=sort_order
    )

@app.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.delete_book(db=db, book_id=book_id, user_id=current_user.id)

# -------------------------
# TASK ROUTES (Main feature with user ownership)

@app.post("/tasks/", response_model=TaskOut)
def create_user_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return create_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[TaskOut])
def read_user_tasks(
    skip: int = 0,
    limit: int = 10,
    completed: bool = None,               # filter by completed status
    title: str = None,                    # filter by title keyword
    sort_by: str = "id",                  # sort field
    sort_order: str = "asc",              # asc or desc
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Task).filter(models.Task.user_id == current_user.id)

    # Apply filters
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if title:
        query = query.filter(models.Task.title.ilike(f"%{title}%"))

    # Apply sorting
    sort_column = getattr(models.Task, sort_by, models.Task.id)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # Pagination
    return (
        query.order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )

@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = True
    db.commit()
    return {"message": "Task marked as completed"}

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_user_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.update_task(db=db, task_id=task_id, user_id=current_user.id, task_update=task_update)

@app.delete("/tasks/{task_id}")
def delete_user_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
