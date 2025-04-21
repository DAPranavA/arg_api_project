from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from .database import Base
from sqlalchemy.orm import relationship

# -------------------------
# Book Model
# Table: books

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    pages = Column(Integer, nullable=False)
    author = Column(String, nullable=False)
    publisher = Column(String, nullable=False)

    #New: Link book to user
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

# -------------------------
# User Model
# Table: users

class User(Base):
    __tablename__ = "users"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)         # Hashed password (using bcrypt)

    tasks = relationship("Task", back_populates="owner")

# -------------------------
# Task Model
# Table: tasks

class Task(Base):
    __tablename__ = "tasks"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)        
    title = Column(String, nullable=False)                    
    description = Column(String, nullable=True)               
    completed = Column(Boolean, default=False)                

    user_id = Column(Integer, ForeignKey("users.id"))         
    owner = relationship("User", back_populates="tasks")      
