
"""
CRUD helpers for MicrocontrollersNews API.

Key points:
*   Always sort `get_articles()` to satisfy MSSQL OFFSET/FETCH requirements.
*   Use `Session.get()` where possible (SQLAlchemy 1.4+).
*   Avoid passing unknown kwargs to model constructors (`**user.dict()` kept, but validated).
*   Handle optional image/tag assignments safely.
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app import models, schemas


# ────────────────────── Users ───────────────────────────────────────────────────


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Return user by primary key or *None*."""
    return db.get(models.User, user_id)


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Return list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_login(db: Session, login: str) -> Optional[models.User]:
    """Case‑insensitive lookup by login."""
    return (
        db.query(models.User)
        .filter(models.User.Login.ilike(login))
        .first()
    )



def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Insert new user and return fresh instance."""
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ──────────────────── Reference data ────────────────────────────────────────────


def get_statuses(db: Session) -> Sequence[models.ArticleStatus]:
    return db.query(models.ArticleStatus).order_by(models.ArticleStatus.StatusId).all()



def get_genders(db: Session) -> Sequence[models.Gender]:
    return db.query(models.Gender).order_by(models.Gender.GenderId).all()



def get_tags(db: Session) -> Sequence[models.Tag]:
    return db.query(models.Tag).order_by(models.Tag.Name).all()



def create_tag(db: Session, name: str) -> models.Tag:
    tag = models.Tag(Name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# ───────────────────── Articles ────────────────────────────────────────────────

DEFAULT_ARTICLE_ORDER = models.Article.CreatedAt.desc()



def get_articles(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    status_id: Optional[int] = None,
    order_by = DEFAULT_ARTICLE_ORDER,
) -> Sequence[models.Article]:
    """
    Fetch a slice of articles with stable ordering (required for MSSQL OFFSET/FETCH).

    `.offset(skip).limit(limit)` is always accompanied by `.order_by(...)`.
    """
    q = db.query(models.Article)

    if status_id is not None:
        q = q.filter(models.Article.StatusId == status_id)

    q = q.order_by(order_by)

    if skip:
        q = q.offset(skip)
    if limit:
        q = q.limit(limit)

    return q.all()



def get_article(db: Session, article_id: int) -> Optional[models.Article]:
    return db.get(models.Article, article_id)



def create_article(db: Session, art: schemas.ArticleCreate) -> models.Article:
    db_art = models.Article(
        AuthorId=art.AuthorId,
        Title=art.Title,
        Body=art.Body,
        StatusId=art.StatusId,
        CreatedAt=datetime.utcnow(),
        UpdatedAt=datetime.utcnow(),
    )

    if art.Image is not None:
        db_art.Image = art.Image

    if art.TagIds:
        db_art.Tags = (
            db.query(models.Tag)
            .filter(models.Tag.TagId.in_(art.TagIds))
            .all()
        )

    db.add(db_art)
    db.commit()
    db.refresh(db_art)
    return db_art



def update_article(
    db: Session,
    db_art: models.Article,
    upd: schemas.ArticleUpdate,
) -> models.Article:
    """Apply partial update according to Pydantic model `ArticleUpdate`."""
    for field, val in upd.dict(exclude_unset=True).items():
        if field == "TagIds":
            db_art.Tags = (
                db.query(models.Tag)
                .filter(models.Tag.TagId.in_(val))
                .all()
            )
        else:
            setattr(db_art, field, val)

    db_art.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(db_art)
    return db_art



def delete_article(db: Session, db_art: models.Article) -> None:
    db.delete(db_art)
    db.commit()
