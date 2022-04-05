import boto3
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.auth_service import get_current_user_id
from pydantic import BaseModel

from app.src.services.user_service import UserService

router = APIRouter(prefix="/tokens")
logger = LoggerConfig(__name__).get()
kms_client = boto3.client("kms")


class Message(BaseModel):
    message: str  # should come in as hex encoded


@router.get("/wallet")
def get_wallet(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    return {'data': user.address}


@router.post("/sign")
def sign_message(
        message_data: Message,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id),
):
    user = UserService.get(db, user_id)

    # TODO V2 - Hit wallet backend to get signed message
    signed_msg = "signed message from Wallet" # Should return it in the format I want

    return {'result': signed_msg}
