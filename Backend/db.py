import os
import hashlib
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_URL = os.getenv("DATABASE_URL", "postgresql://stylr:stylr@localhost/stylr")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(LargeBinary(16), nullable=False)

def init_db():
    Base.metadata.create_all(engine)

def hash_password(password, salt):
    h = hashlib.sha512()
    h.update(password.encode("utf-8") + salt)
    return h.hexdigest()

def create_user(username, password):
    session = Session()
    try:
        salt = os.urandom(16)
        password_hash = hash_password(password, salt)
        user = User(username=username, password_hash=password_hash, salt=salt)
        session.add(user)
        session.commit()
        user_id = user.id
        return user_id
    finally:
        session.close()

def verify_user(username, password):
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return None
        if hash_password(password, user.salt) != user.password_hash:
            return None
        return user.id
    finally:
        session.close()
