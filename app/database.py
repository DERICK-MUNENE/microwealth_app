from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = "root"
DB_PASS = "GSsgSqFqtSsQUtmSKDhfEXKrOvpsmtkp"
DB_HOST = "switchyard.proxy.rlwy.net"
DB_NAME = "railway"
DB_PORT = 47635

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test connection
try:
    engine.connect()
    print("DB connection OK")
except Exception as e:
    print("DB connection failed:", e)
