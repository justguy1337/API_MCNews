# app/main.py

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, users, articles, tags, statuses, genders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microcontrollers News API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(auth.router,     prefix="/auth")
app.include_router(users.router,    prefix="/users")
app.include_router(articles.router)
app.include_router(tags.router,     prefix="/tags")
app.include_router(statuses.router, prefix="/statuses")
app.include_router(genders.router,  prefix="/genders")


from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, models
from datetime import date

@app.on_event("startup")
def seed_initial_data():
    db: Session = SessionLocal()
    try:
        # Seed genders
        if db.query(models.Gender).count() == 0:
            db.add_all([
                models.Gender(GenderId=1, Name="Male"),
                models.Gender(GenderId=2, Name="Female"),
            ])
            db.commit()
        # Seed statuses
        if db.query(models.ArticleStatus).count() == 0:
            db.add_all([
                models.ArticleStatus(StatusId=1, Name="Draft"),
                models.ArticleStatus(StatusId=2, Name="Published")
            ])
            db.commit()
        # Seed tags
        if db.query(models.Tag).count() == 0:
            db.add_all([
                models.Tag(TagId=1, Name="ESP32"),
                models.Tag(TagId=2, Name="STM32"),
                models.Tag(TagId=3, Name="Raspberry Pi")
            ])
            db.commit()
        # Seed demo user
        if db.query(models.User).count() == 0:
            demo = models.User(
                UserId=1,
                FirstName="Иван",
                LastName="Иванов",
                MiddleName=None,
                BirthDate=date(1990,1,1),
                GenderId=1,
                Email="ivan@example.com",
                Login="ivan",
                PasswordHash="hash",
                Photo=None
            )
            db.add(demo); db.commit()
    finally:
        db.close()