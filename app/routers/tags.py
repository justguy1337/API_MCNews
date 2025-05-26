from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["Tags"])

@router.get("/", response_model=List[schemas.TagOut], summary="Список тегов")
def read_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)

@router.post("/", response_model=schemas.TagOut, summary="Создать тег")
def create_tag(name: str, db: Session = Depends(get_db)):
    return crud.create_tag(db, name)
