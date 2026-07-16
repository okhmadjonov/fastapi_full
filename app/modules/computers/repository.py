from sqlalchemy.orm import Session
from app.modules.computers.models import Computer
from app.modules.computers.schemas import ComputerCreate, ComputerUpdate

class ComputerRepository:
    @staticmethod
    def get_by_id(db: Session, computer_id: int):
        return db.query(Computer).filter(Computer.id == computer_id).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Computer).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Computer).filter(Computer.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, computer_in: ComputerCreate, user_id: int):
        db_computer = Computer(
            name=computer_in.name,
            brand=computer_in.brand,
            price=computer_in.price,
            user_id=user_id  # Yaratayotgan foydalanuvchining ID-si ulanadi
        )
        db.add(db_computer)
        db.commit()
        db.refresh(db_computer)
        return db_computer

    @staticmethod
    def update(db: Session, db_computer: Computer, computer_in: ComputerUpdate):
        update_data = computer_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_computer, field, value)
        db.commit()
        db.refresh(db_computer)
        return db_computer

    @staticmethod
    def delete(db: Session, db_computer: Computer):
        db.delete(db_computer)
        db.commit()
        return db_computer
