
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


DB_USER = os.environ.get("DB_USER", "if0_38916805")         
DB_PASS = os.environ.get("DB_PASS", "")              
DB_HOST = os.environ.get("DB_HOST", "sql311.infinityfree.com")     
DB_NAME = os.environ.get("DB_NAME", "if0_38916805_project")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)