from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, event, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv
import bcrypt
import os
import uuid

dotenv.load_dotenv(dotenv_path="./.env")

DATABASE_URL = os.getenv("DB_URL")


engine = create_engine("postgresql://postgres:Liukangs240@localhost:5433/apihaven_cli")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def generate_id(length = 16):
    return uuid.uuid4().hex[:length if length > 10 else 16]

class UserDatabase(Base):
    __tablename__ = "user_databases"
    name = Column(String, default="new_database")
    db_id = Column(String, primary_key=True, default=generate_id)
    last_updated = Column(DateTime, nullable=False, default=func.now())




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True, default="USER")
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    database = Column(String, ForeignKey("user_databases.db_id"), nullable=False)

    def set_password(self, raw_password: str):
        self.password = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password.encode("utf-8"))

# @event.listens_for(User, 'before_insert')
# def update_user_database(mapper, connection, target):
#     new_db = UserDatabase(db_id = generate_id(16))
#     target.database = new_db.db_id






def init_db():
    Base.metadata.create_all(bind=engine)




