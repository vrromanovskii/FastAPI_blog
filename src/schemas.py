from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class PublicationCreate(BaseModel):
    title: str
    text: str
    category: str
    image_url: str

class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class PublicationOut(BaseModel):
    publication_id: UUID
    title: str
    text: str
    category: str
    image_url: str
    created_at: datetime
    updated_at: datetime
    author_id: int

    class Config:
        from_attributes = True # позволяет работать с SQLAlchemy моделями



class DeletedPublicationOut(BaseModel):
    publication_id: UUID
    title: str
    text: str
    category: str
    image_url: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    author_id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



from typing import TypeVar, Generic, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int