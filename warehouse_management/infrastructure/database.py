from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from warehouse_management.infrastructure.orm import Base

DATABASE_URL = "sqllite://warehouse.db"
