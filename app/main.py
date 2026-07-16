from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base, SessionLocal
from app.api_router import api_router
from app.modules.auth.service import AuthService

# Ilova ishga tushganda bajariladigan lifespan logikasi
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Baza jadvallarini yaratish (agar yaratilmagan bo'lsa)
    Base.metadata.create_all(bind=engine)
    
    # 2. Admin foydalanuvchini qo'shish (seeding)
    db = SessionLocal()
    try:
        AuthService.seed_admin(db)
    finally:
        db.close()
        
    yield
    # Ilova to'xtaganda bajariladigan amallar (agar kerak bo'lsa) shu yerda bo'ladi

app = FastAPI(
    title="FastAPI Structured CRUD App",
    description="Role-based auth va CRUD bilan tuzilgan FastAPI loyihasi",
    version="1.0.0",
    lifespan=lifespan
)

# API routerlarni ulash
app.include_router(api_router)

# Asosiy sahifa (salomlashish sahifasi)
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "FastAPI Structured CRUD loyihasiga xush kelibsiz!",
        "docs_url": "/docs"
    }
