import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = os.environ.get("DB_USER") or "root"
DB_PASS = os.environ.get("DB_PASS") or ""
DB_HOST = os.environ.get("DB_HOST") or "127.0.0.1"
DB_NAME = os.environ.get("DB_NAME") or "mydb"
DB_PORT = int(os.environ.get("DB_PORT", 3306))

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4&allow_public_key_retrieval=true"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test connection
try:
    engine.connect()
    print("DB connection OK")
except Exception as e:
    print("DB connection failed:", e)
