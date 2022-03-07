import string
import random

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.email_service import EmailService

router = APIRouter(prefix="/auth")
logger = LoggerConfig(__name__).get()


@router.post("/resendcode")
def resend_verification_code(
        email: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    code = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
    EmailService.send_verification_code(user, code)
    user.verification_code = code
    db.commit()
    return {"message": "OK"}


@router.post("/verifyemail")
def verify_email(
        email: str,
        code: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if user.verification_code == code:
        user.verified = True
        db.commit()
        return {"message": "OK"}
    else:
        return {"message": "Invalid Code"}
