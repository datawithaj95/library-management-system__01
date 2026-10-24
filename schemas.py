from pydantic import BaseModel, Field, ConfigDict


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str | None = Field(default=None, max_length=20)
    quantity: int = Field(default=1, ge=0)


class BookResponse(BookCreate):
    id: int
    available: bool

    model_config = ConfigDict(from_attributes=True)