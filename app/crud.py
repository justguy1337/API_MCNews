from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional

def get_users(db: Session, skip: int = 0, limit: int = 100):
    # Добавляем сортировку по UserId для корректной работы с OFFSET в SQL Server
    return db.query(models.User).order_by(models.User.UserId).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.UserId == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.Email == email).first()

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.Login == login).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)  # Предполагаем, что у вас есть функция хеширования
    db_user = models.User(
        FirstName=user.first_name,
        LastName=user.last_name,
        MiddleName=user.middle_name,
        BirthDate=user.birth_date,
        GenderId=user.gender_id,
        Email=user.email,
        Login=user.login,
        PasswordHash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_id: Optional[int] = None,
    search: Optional[str] = None,
    tag_id: Optional[int] = None
):
    query = db.query(models.Article).order_by(models.Article.ArticleId)
    if status_id is not None:
        query = query.filter(models.Article.StatusId == status_id)
    if search is not None:
        query = query.filter(func.lower(models.Article.Title).like(f"%{search.lower()}%"))
    if tag_id is not None:
        query = query.join(models.article_tag).filter(models.article_tag.c.TagId == tag_id)
    return query.offset(skip).limit(limit).all()

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tag).order_by(models.Tag.TagId).offset(skip).limit(limit).all()

def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.ArticleId == article_id).first()

def create_article(db: Session, article: schemas.ArticleCreate, author_id: int):
    db_article = models.Article(
        AuthorId=author_id,
        Title=article.title,
        Body=article.body,
        StatusId=article.status_id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article(db: Session, article_id: int, article: schemas.ArticleUpdate):
    db_article = db.query(models.Article).filter(models.Article.ArticleId == article_id).first()
    if db_article:
        for key, value in article.dict(exclude_unset=True).items():
            setattr(db_article, key, value)
        db_article.UpdatedAt = db.query(models.func.sysutcdatetime()).scalar()
        db.commit()
        db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int):
    db_article = db.query(models.Article).filter(models.Article.ArticleId == article_id).first()
    if db_article:
        db.delete(db_article)
        db.commit()
    return db_article

# Вспомогательная функция для хеширования паролей
def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest().upper()