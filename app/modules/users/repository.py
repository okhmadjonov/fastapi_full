from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_in: UserCreate, hashed_password: str):
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            role=user_in.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate, hashed_password: str = None):
        update_data = user_in.model_dump(exclude_unset=True)
        if hashed_password:
            update_data["hashed_password"] = hashed_password
            if "password" in update_data:
                del update_data["password"]
        elif "password" in update_data:
            del update_data["password"]
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, db_user: User):
        db.delete(db_user)
        db.commit()
        return db_user
