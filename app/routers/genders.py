from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["Genders"])

@router.get("/", response_model=List[schemas.GenderOut], summary="Список полов")
def read_genders(db: Session = Depends(get_db)):
    return crud.get_genders(db)
