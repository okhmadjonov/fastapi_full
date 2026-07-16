from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.computers.repository import ComputerRepository
from app.modules.computers.schemas import ComputerCreate, ComputerUpdate
from app.modules.users.models import User

class ComputerService:
    @staticmethod
    def get_computer_by_id(db: Session, computer_id: int):
        db_computer = ComputerRepository.get_by_id(db, computer_id)
        if not db_computer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kompyuter topilmadi"
            )
        return db_computer

    @staticmethod
    def get_computers(db: Session, skip: int = 0, limit: int = 100):
        return ComputerRepository.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    def get_user_computers(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return ComputerRepository.get_by_user(db, user_id=user_id, skip=skip, limit=limit)

    @staticmethod
    def create_computer(db: Session, computer_in: ComputerCreate, current_user: User):
        # Kompyuterni joriy kirgan user ID-si bilan yaratish
        return ComputerRepository.create(db, computer_in=computer_in, user_id=current_user.id)

    @staticmethod
    def update_computer(db: Session, computer_id: int, computer_in: ComputerUpdate, current_user: User):
        db_computer = ComputerService.get_computer_by_id(db, computer_id)
        
        # Faqat egasi yoki admin o'zgartirishi mumkin
        if db_computer.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sizda ushbu kompyuter ma'lumotlarini o'zgartirish huquqi yo'q"
            )
        return ComputerRepository.update(db, db_computer=db_computer, computer_in=computer_in)

    @staticmethod
    def delete_computer(db: Session, computer_id: int, current_user: User):
        db_computer = ComputerService.get_computer_by_id(db, computer_id)
        
        # Faqat egasi yoki admin o'chira oladi
        if db_computer.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sizda ushbu kompyuterni o'chirish huquqi yo'q"
            )
        return ComputerRepository.delete(db, db_computer=db_computer)
