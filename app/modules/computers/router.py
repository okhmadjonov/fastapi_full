from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.computers.schemas import ComputerCreate, ComputerUpdate, ComputerResponse
from app.modules.computers.service import ComputerService
from app.modules.auth.service import get_current_user, RoleChecker
from app.modules.users.models import User

# Faqat adminlarga ruxsat berish dependency-si
admin_required = RoleChecker(["admin"])

# Router darajasida dependency qo'shish orqali barcha yo'llarni adminlar uchun cheklaymiz
router = APIRouter(
    prefix="/computers", 
    tags=["Computers"], 
    dependencies=[Depends(admin_required)]
)

# 1. Yangi kompyuter yaratish (Faqat admin)
@router.post("/", response_model=ComputerResponse, status_code=status.HTTP_201_CREATED)
def create_computer(
    computer_in: ComputerCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return ComputerService.create_computer(db, computer_in=computer_in, current_user=current_user)

# 2. Barcha kompyuterlarni olish (Faqat admin)
@router.get("/", response_model=list[ComputerResponse])
def read_computers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ComputerService.get_computers(db, skip=skip, limit=limit)

# 3. Admin o'zi yaratgan kompyuterlarni olish (Faqat admin)
@router.get("/my", response_model=list[ComputerResponse])
def read_my_computers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return ComputerService.get_user_computers(db, user_id=current_user.id, skip=skip, limit=limit)

# 4. Bitta kompyuterni olish (Faqat admin)
@router.get("/{computer_id}", response_model=ComputerResponse)
def read_computer(
    computer_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ComputerService.get_computer_by_id(db, computer_id=computer_id)

# 5. Kompyuter ma'lumotlarini o'zgartirish (Faqat admin)
@router.put("/{computer_id}", response_model=ComputerResponse)
def update_computer(
    computer_id: int, 
    computer_in: ComputerUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return ComputerService.update_computer(
        db, computer_id=computer_id, computer_in=computer_in, current_user=current_user
    )

# 6. Kompyuterni o'chirish (Faqat admin)
@router.delete("/{computer_id}", response_model=ComputerResponse)
def delete_computer(
    computer_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return ComputerService.delete_computer(db, computer_id=computer_id, current_user=current_user)

