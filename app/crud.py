from sqlalchemy.orm import Session 
from . import models, schemas 
from typing import List       
from fastapi import HTTPException, status 
from passlib.context import CryptContext  
from .models import User, Task
from .schemas import UserCreate, TaskCreate

# -------------------------
# BOOKS SECTION

def create_book(db: Session, book: schemas.BookCreate, user_id: int):
    db_book = models.Book(
        book_name=book.book_name,
        description=book.description,
        pages=book.pages,
        author=book.author,
        publisher=book.publisher,
        user_id=user_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books(
    db: Session,
    user_id: int,
    name: str = None,
    author: str = None,
    publisher: str = None,
    sort_by: str = "id",
    sort_order: str = "asc"
) -> List[models.Book]:
    # Start with current user's books only
    query = db.query(models.Book).filter(models.Book.user_id == user_id)

    # filters
    if name:
        query = query.filter(models.Book.book_name.ilike(f"%{name}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    if publisher:
        query = query.filter(models.Book.publisher.ilike(f"%{publisher}%"))

    # sorting
    sort_column = getattr(models.Book, sort_by, models.Book.id)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    return query.order_by(sort_column).all()



def delete_book(db: Session, book_id: int, user_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id, models.Book.user_id == user_id).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": f"Book with id {book_id} deleted successfully"}


# -------------------------
# USER AUTHENTICATION SECTION

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Returns a hashed version of the password.
    """
    return pwd_context.hash(password)


def create_user(db: Session, user: UserCreate):
    """
    Adds a new user with a hashed password to the users table.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    """
    Retrieves a user by their username (used for login and validation).
    """
    return db.query(User).filter(User.username == username).first()

# -------------------------
# TASKS SECTION

def create_task(db: Session, task: TaskCreate, user_id: int):
    """
    Creates a new task for the logged-in user.
    """
    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieves paginated tasks for a specific user.
    - skip: number of records to skip (offset)
    - limit: maximum number of records to return
    """
    return (
        db.query(models.Task)
        .filter(models.Task.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_task(db: Session, task_id: int, user_id: int, task_update: schemas.TaskUpdate):
    """
    Updates a task only if it belongs to the current user.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields provided in request
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int):
    """
    Deletes a task only if it belongs to the current user.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": f"Task with id {task_id} deleted successfully"}
