from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv  # 🔹 NEW
import os

load_dotenv()  # 🔹 NEW: Load .env variables

# Get database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/arg_books"
)

# Create SQLAlchemy engine instance with proper settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  
    pool_size=5,         
    max_overflow=10      
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for declarative models
Base = declarative_base()
