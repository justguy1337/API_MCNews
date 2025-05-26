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
    MiddleName: Optional[str]
    BirthDate: date
    GenderId: int
    Email: EmailStr
    Login: str
    PasswordHash: str
    Photo: Optional[bytes]

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    UserId: int
    CreatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

# статьи

class ArticleBase(BaseModel):
    AuthorId: int
    Title: str
    Body: str
    StatusId: int

class ArticleCreate(ArticleBase):
    Image: Optional[bytes]
    TagIds: Optional[List[int]] = []

class ArticleUpdate(BaseModel):
    Title: Optional[str]
    Body: Optional[str]
    StatusId: Optional[int]
    Image: Optional[bytes]
    TagIds: Optional[List[int]] = []

class ArticleOut(ArticleBase):
    ArticleId: int
    Author: UserOut
    Status: StatusOut
    Tags: List[TagOut]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
