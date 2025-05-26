from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from io import BytesIO
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

from app import crud, schemas
from app.database import get_db
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
)


@router.get(
    "/",
    response_model=List[schemas.ArticleOut],
    summary="List Published",
    description="Возвращает опубликованные статьи (опционально filter by status)"
)
def list_published(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(10, ge=1, le=100, description="Максимум записей"),
    status: Optional[int] = Query(None, description="ID статуса для фильтрации"),
    db: Session = Depends(get_db)
):
    return crud.get_articles(db, skip=skip, limit=limit, status_id=status)


@router.get(
    "/all",
    response_model=List[schemas.ArticleOut],
    summary="List All",
    description="Возвращает все статьи, вне зависимости от статуса"
)
def list_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.get_articles(db, skip=skip, limit=limit, status_id=None)


@router.get(
    "/{article_id}",
    response_model=schemas.ArticleOut,
    summary="Get One",
    description="Возвращает статью по её ID"
)
def get_one(
    article_id: int,
    db: Session = Depends(get_db)
):
    art = crud.get_article(db, article_id)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    return art


@router.post(
    "/",
    response_model=schemas.ArticleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create",
    description="Создаёт новую статью"
)
def create(
    article_in: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.create_article(db, article_in)


@router.put(
    "/{article_id}",
    response_model=schemas.ArticleOut,
    summary="Update",
    description="Обновляет существующую статью"
)
def update(
    article_id: int,
    update_data: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    art = crud.get_article(db, article_id)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    return crud.update_article(db, art, update_data)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete",
    description="Удаляет статью по ID"
)
def delete(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    art = crud.get_article(db, article_id)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    crud.delete_article(db, art)


@router.get(
    "/{article_id}/pdf",
    summary="Article Pdf",
    description="Генерирует PDF для статьи"
)
def pdf(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    art = crud.get_article(db, article_id)
    if not art:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Статья не найдена")

    buf = BytesIO()
    p = canvas.Canvas(buf)
    p.drawString(50, 800, f"Title: {art.Title}")
    p.drawString(50, 780, f"Author ID: {art.AuthorId}")
    text = p.beginText(50, 760)
    for line in art.Body.splitlines():
        text.textLine(line)
    p.drawText(text)
    p.showPage()
    p.save()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=article_{article_id}.pdf"}
    )
