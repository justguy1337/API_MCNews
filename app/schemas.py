from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import date, datetime

# справочники

class StatusOut(BaseModel):
    StatusId: int
    Name: str
    model_config = ConfigDict(from_attributes=True)

class GenderOut(BaseModel):
    GenderId: int
    Name: str
    model_config = ConfigDict(from_attributes=True)

class TagOut(BaseModel):
    TagId: int
    Name: str
    model_config = ConfigDict(from_attributes=True)

# пользователи

class UserBase(BaseModel):
    FirstName: str
    LastName: str
    MiddleName: Optional[str] = None
    BirthDate: date
    GenderId: int
    Email: EmailStr
    Login: str
    Photo: Optional[bytes] = None

class UserCreate(UserBase):
    # Клиент отправляет обычный пароль, а не хеш
    Password: str

class UserOut(UserBase):
    UserId: int
    CreatedAt: datetime
    # PasswordHash не выводим в ответе из соображений безопасности
    model_config = ConfigDict(from_attributes=True)

# статьи

class ArticleBase(BaseModel):
    AuthorId: int
    Title: str
    Body: str
    StatusId: int

class ArticleCreate(ArticleBase):
    Image: Optional[bytes] = None
    TagIds: Optional[List[int]] = []

class ArticleUpdate(BaseModel):
    Title: Optional[str] = None
    Body: Optional[str] = None
    StatusId: Optional[int] = None
    Image: Optional[bytes] = None
    TagIds: Optional[List[int]] = []

class ArticleOut(ArticleBase):
    ArticleId: int
    Author: UserOut
    Status: StatusOut
    Tags: List[TagOut]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)