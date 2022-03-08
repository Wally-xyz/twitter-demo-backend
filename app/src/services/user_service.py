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
