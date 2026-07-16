from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.modules.users.repository import UserRepository
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from app.core.database import get_db
from app.modules.auth.schemas import LoginRequest, TokenResponse

# FastAPI login endpointini aniqlaymiz (Token beruvchi endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> User:
        user = UserRepository.get_by_email(db, email=login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Foydalanuvchi faol emas"
            )
        return user

    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> TokenResponse:
        user = AuthService.authenticate_user(db, login_data)
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        token_data = decode_token(refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Yaroqsiz refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = token_data.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Foydalanuvchi aniqlanmadi",
            )
        user = UserRepository.get_by_id(db, user_id=int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Foydalanuvchi topilmadi yoki faol emas"
            )
        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)

    @staticmethod
    def seed_admin(db: Session):
        admin_email = "admin@example.com"
        admin = UserRepository.get_by_email(db, email=admin_email)
        if not admin:
            admin_in = UserCreate(
                email=admin_email,
                password="adminpassword123",  
                role="admin"
            )
            hashed_password = get_password_hash(admin_in.password)
            UserRepository.create(db, user_in=admin_in, hashed_password=hashed_password)
            print("INFO: Tizimga birinchi admin qo'shildi: admin@example.com / adminpassword123")


# Token orqali joriy foydalanuvchini olish (Dependency)
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    token_data = decode_token(token)
    if not token_data or token_data.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yaroqsiz yoki muddati tugagan token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token xato ma'lumotga ega",
        )
    user = UserRepository.get_by_id(db, user_id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi faol emas"
        )
    return user

# Rolni tekshirish uchun klass (Dependency)
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sizda ushbu amalni bajarish uchun ruxsat mavjud emas"
            )
        return current_user
