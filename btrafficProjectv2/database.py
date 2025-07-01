#database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ?? Replace these with your real MySQL credentials
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mariaDBT!m_008@localhost/traffic_dbP"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
