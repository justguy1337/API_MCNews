from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from io import BytesIO
from app import crud, schemas, models
from app.database import get_db
from app.utils.security import get_current_user, verify_password, get_password_hash

from typing import List

router = APIRouter(tags=["Users"])


@router.get("/", response_model=List[schemas.UserOut], summary="Список пользователей")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=schemas.UserOut, summary="Профиль")
def read_users_me(current: models.User = Depends(get_current_user)):
    return current


@router.put("/me", response_model=schemas.UserOut, summary="Обновить профиль")
def update_profile(update: schemas.UserCreate, db: Session = Depends(get_db),
                   current: models.User = Depends(get_current_user)):
    # Исключаем пароль из обновления профиля
    update_data = update.dict(exclude={'Password'}, exclude_unset=True)
    for field, val in update_data.items():
        setattr(current, field, val)
    db.commit()
    db.refresh(current)
    return current


@router.put("/me/password", summary="Сменить пароль")
def change_password(old: str, new: str, db: Session = Depends(get_db),
                    current: models.User = Depends(get_current_user)):
    if not verify_password(old, current.PasswordHash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Old password incorrect")
    current.PasswordHash = get_password_hash(new)
    db.commit()
    return {"msg": "Password updated"}


@router.get("/me/pdf", summary="Профиль PDF")
def profile_pdf(current: models.User = Depends(get_current_user)):
    buf = BytesIO()
    p = canvas.Canvas(buf)
    p.drawString(50, 800, f"{current.FirstName} {current.LastName}")
    p.drawString(50, 780, f"Email: {current.Email}")
    p.showPage()
    p.save()
    buf.seek(0)
    return Response(buf.read(), media_type="application/pdf")


@router.post("/", response_model=schemas.UserOut, summary="Создать пользователя")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя"""
    # Проверяем уникальность логина
    existing_user = crud.get_user_by_login(db, user.Login)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )

    # Проверяем уникальность email
    existing_email = db.query(models.User).filter(models.User.Email == user.Email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    return crud.create_user(db=db, user=user)