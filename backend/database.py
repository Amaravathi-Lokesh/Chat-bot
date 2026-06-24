from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from config.settings import Settings
DATABASE_URL = Settings.db_key
print("DATABASE_URL =", DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    # connect_args={"check_same_thread": False}
)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()