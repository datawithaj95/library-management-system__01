from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from backend.database import Base, engine, get_db
from backend.models import Book
from backend.schemas import BookCreate, BookResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Library Management API",
    description="An API to manage library books using FastAPI and PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Library Management API!",
        "docs": "/docs"
    }


# 1. Add a new book
@app.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    if book.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=409,
                detail="A book with this ISBN already exists."
            )

    new_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        available=book.quantity > 0
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


# 2. View all books
@app.get("/books/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()


# 3. View one book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# 4. Update a book
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookCreate,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_data.isbn:
        duplicate = db.query(Book).filter(
            Book.isbn == book_data.isbn,
            Book.id != book_id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Another book already uses this ISBN."
            )

    book.title = book_data.title
    book.author = book_data.author
    book.isbn = book_data.isbn
    book.quantity = book_data.quantity
    book.available = book_data.quantity > 0

    db.commit()
    db.refresh(book)

    return book


# 5. Delete a book
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}