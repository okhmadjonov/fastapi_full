from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        db_user = UserRepository.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foydalanuvchi topilmadi"
            )
        return db_user

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return UserRepository.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    def create_user(db: Session, user_in: UserCreate):
        # Email oldindan ro'yxatdan o'tganligini tekshirish
        existing_user = UserRepository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ushbu email bilan foydalanuvchi allaqachon ro'yxatdan o'tgan"
            )
        
        # Parolni hashing qilish
        hashed_password = get_password_hash(user_in.password)
        return UserRepository.create(db, user_in=user_in, hashed_password=hashed_password)

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate):
        db_user = UserService.get_user_by_id(db, user_id)
        
        # Agar email o'zgartirilayotgan bo'lsa, u band emasligini tekshirish
        if user_in.email and user_in.email != db_user.email:
            existing_user = UserRepository.get_by_email(db, email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ushbu email allaqachon band"
                )
        
        # Parol o'zgartirilayotgan bo'lsa, uni hashlash
        hashed_password = None
        if user_in.password:
            hashed_password = get_password_hash(user_in.password)
            
        return UserRepository.update(db, db_user=db_user, user_in=user_in, hashed_password=hashed_password)

    @staticmethod
    def delete_user(db: Session, user_id: int):
        db_user = UserService.get_user_by_id(db, user_id)
        return UserRepository.delete(db, db_user=db_user)
