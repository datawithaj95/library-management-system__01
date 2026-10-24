from sqlalchemy import Column, Integer, String, Boolean
from backend.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    quantity = Column(Integer, default=1)
    available = Column(Boolean, default=True)