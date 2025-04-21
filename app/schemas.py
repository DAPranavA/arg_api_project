from pydantic import BaseModel  # Used for defining data models with validation

# -------------------------
# Book Schemas (Optional / Legacy Feature)

class BookCreate(BaseModel):
    """
    Schema for creating a new book (used in POST /books/)
    """
    book_name: str
    description: str | None = None
    pages: int
    author: str
    publisher: str

class BookOut(BookCreate):
    """
    Schema for returning a book in response (adds ID)
    """
    id: int

    class Config:
        orm_mode = True  # Enables compatibility with ORM models like SQLAlchemy

# -------------------------
# User Schemas

class UserCreate(BaseModel):
    """
    Schema for user registration
    """
    username: str
    password: str

class UserOut(BaseModel):
    """
    Schema for returning user info (without password)
    """
    id: int
    username: str

    # New format in Pydantic v2 instead of orm_mode
    model_config = {
        "from_attributes": True
    }

# -------------------------
# Task Schemas

class TaskBase(BaseModel):
    """
    Base schema shared by all task-related schemas
    """
    title: str
    description: str | None = None
    completed: bool = False

class TaskCreate(TaskBase):
    """
    Schema for creating a new task
    Inherits fields from TaskBase
    """
    pass

class TaskUpdate(BaseModel):
    """
    Schema for updating a task (all fields optional)
    """
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TaskOut(TaskBase):
    """
    Schema for returning task data in responses
    """
    id: int
    user_id: int  # To show ownership of task

    model_config = {
        "from_attributes": True  # For ORM model to schema compatibility
    }
