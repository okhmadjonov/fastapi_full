from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.users.schemas import UserCreate, UserUpdate, UserResponse
from app.modules.users.service import UserService
from app.modules.auth.service import get_current_user, RoleChecker
from app.modules.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])

# Rol tekshirish dependency-si (faqat adminlar uchun)
admin_required = RoleChecker(["admin"])

# Yangi foydalanuvchi yaratish (Ro'yxatdan o'tish - hamma uchun ochiq)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user_in=user_in)

# Barcha foydalanuvchilarni olish (Faqat admin uchun)
@router.get("/", response_model=list[UserResponse], dependencies=[Depends(admin_required)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return UserService.get_users(db, skip=skip, limit=limit)

# Bitta foydalanuvchini olish (O'zi yoki admin)
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Sizda ushbu foydalanuvchi ma'lumotlarini ko'rish huquqi yo'q"
        )
    return UserService.get_user_by_id(db, user_id=user_id)

# Foydalanuvchini yangilash (O'zi yoki admin, rolni faqat admin o'zgartira oladi)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Sizda ushbu foydalanuvchi ma'lumotlarini o'zgartirish huquqi yo'q"
        )
    if user_in.role and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Foydalanuvchi rolini faqat admin o'zgartira oladi"
        )
    return UserService.update_user(db, user_id=user_id, user_in=user_in)

# Foydalanuvchini o'chirish (Faqat admin)
@router.delete("/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.delete_user(db, user_id=user_id)
