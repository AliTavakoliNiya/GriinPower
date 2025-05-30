from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_PATH


# Database URL—for SQLite, a file named 'database.db' is used
DATABASE_URL = DATABASE_PATH

# Create the engine without auto-creating database
engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False},
    poolclass=None  # Prevents pool creation for non-existent database
)


# Create a configured "Session" class with autocommit disabled to enforce transactions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

# Define the Base class for our models.
Base = declarative_base()
