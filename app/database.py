from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = "root"
DB_PASS = "GSsgSqFqtSsQUtmSKDhfEXKrOvpsmtkp"
DB_HOST = "switchyard.proxy.rlwy.net"
DB_NAME = "railway"
DB_PORT = 47635

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # checks dead connections
    pool_recycle=300,       #  refresh before timeout (VERY IMPORTANT)
    pool_size=5,            #  connection pool size
    max_overflow=10,        #  extra connections if needed
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test connection
try:
    with engine.connect() as conn:
        print("DB connection OK")
except Exception as e:
    print("DB connection failed:", e)
