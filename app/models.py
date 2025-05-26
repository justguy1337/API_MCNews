from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    ForeignKey, Table, LargeBinary, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ArticleStatus(Base):
    __tablename__ = "ArticleStatus"
    StatusId = Column(Integer, primary_key=True)
    Name     = Column(String(20), nullable=False, unique=True)
    Articles = relationship("Article", back_populates="Status")

class Gender(Base):
    __tablename__ = "Gender"
    GenderId = Column(Integer, primary_key=True)
    Name     = Column(String(16), nullable=False, unique=True)
    Users    = relationship("User", back_populates="Gender")

article_tag = Table(
    "ArticleTag", Base.metadata,
    Column("ArticleId", Integer, ForeignKey("Article.ArticleId"), primary_key=True),
    Column("TagId",    Integer, ForeignKey("Tag.TagId"),       primary_key=True),
)

class Tag(Base):
    __tablename__ = "Tag"
    TagId    = Column(Integer, primary_key=True, index=True)
    Name     = Column(String(40), nullable=False, unique=True)
    Articles = relationship("Article", secondary=article_tag, back_populates="Tags")

class User(Base):
    __tablename__ = "User"
    UserId       = Column(Integer, primary_key=True, index=True)
    FirstName    = Column(String(50), nullable=False)
    LastName     = Column(String(50), nullable=False)
    MiddleName   = Column(String(50), nullable=True)
    BirthDate    = Column(Date, nullable=False)
    GenderId     = Column(Integer, ForeignKey("Gender.GenderId"), nullable=False)
    Email        = Column(String(100), nullable=False, unique=True)
    Login        = Column(String(50),  nullable=False, unique=True)
    PasswordHash = Column(String(255), nullable=False)
    Photo        = Column(LargeBinary, nullable=True)
    CreatedAt    = Column(DateTime, default=datetime.utcnow)

    Gender   = relationship("Gender", back_populates="Users")
    Articles = relationship("Article", back_populates="Author")

class Article(Base):
    __tablename__ = "Article"
    ArticleId = Column(Integer, primary_key=True, index=True)
    AuthorId  = Column(Integer, ForeignKey("User.UserId"), nullable=False)
    Title     = Column(String(100), nullable=False)
    Body      = Column(Text, nullable=False)
    Image     = Column(LargeBinary, nullable=True)
    StatusId  = Column(Integer, ForeignKey("ArticleStatus.StatusId"), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    Author = relationship("User",          back_populates="Articles")
    Status = relationship("ArticleStatus", back_populates="Articles")
    Tags   = relationship("Tag", secondary=article_tag, back_populates="Articles")
