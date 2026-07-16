from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.schemas import TokenResponse, RefreshTokenRequest, LoginRequest
from app.modules.auth.service import AuthService, get_current_user
from app.modules.users.schemas import UserResponse
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Swagger UI orqali to'g'ridan-to'g'ri "Authorize" tugmasi ishlashi uchun OAuth2PasswordRequestForm ishlatiladi
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username foydalanuvchining email manzili hisoblanadi
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return AuthService.login(db, login_data)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(db, refresh_token=request.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
