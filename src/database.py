from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.utils.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Every request opens a db session, uses it and closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()