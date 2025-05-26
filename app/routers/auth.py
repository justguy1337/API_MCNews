from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter(tags=["Auth"])

@router.post("/register", response_model=schemas.UserOut, summary="Регистрация")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_login(db, user.Login):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Login already exists")
    user.PasswordHash = get_password_hash(user.PasswordHash)
    return crud.create_user(db, user)

@router.post("/login", summary="Авторизация")
def login(data: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, data.Login)
    if not db_user or not verify_password(data.PasswordHash, db_user.PasswordHash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": db_user.Login})
    return {"access_token": token, "token_type": "bearer"}
