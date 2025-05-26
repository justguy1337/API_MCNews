from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["Statuses"])

@router.get("/", response_model=List[schemas.StatusOut], summary="Список статусов")
def read_statuses(db: Session = Depends(get_db)):
    return crud.get_statuses(db)
