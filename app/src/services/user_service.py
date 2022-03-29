from sqlalchemy import func
from sqlalchemy.orm import Session

from app.src.models.models import User


class UserService:

    @staticmethod
    def create_from_email(db: Session, email: str) -> User:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get(db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception(f"User with id {user_id} not found")
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(func.lower(User.email) == email.lower()).first()
