from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router

# Asosiy API yo'naltiruvchisi (version 1)
api_router = APIRouter(prefix="/api/v1")

# Modullarning routerlarini ulash
api_router.include_router(auth_router)
api_router.include_router(users_router)
