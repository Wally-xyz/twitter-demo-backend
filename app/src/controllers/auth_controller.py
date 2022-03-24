import string
import random
from datetime import timedelta

import boto3
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from web3 import Web3

from app.src.config.parameter_store import Properties
from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.email_service import EmailService
from app.src.services.user_service import UserService
from app.src.views.user_view import UserView
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/auth")
logger = LoggerConfig(__name__).get()
kms_client = boto3.client("kms")


def render(user: User, access_token: str):
    return {"user": UserView(user), "access_token": access_token}


@router.post("/sendcode")
def create_or_resend_code(
        email: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = UserService.create_from_email(db=db, email=email)
    code = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
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
        if not user.private_key:
            w3 = Web3(Web3.HTTPProvider(Properties.alchemy_node_url))
            account = w3.eth.account.create()
            # Encoded Private Key
            response = kms_client.encrypt(
                KeyId=Properties.kms_db_key_alias,
                Plaintext=account.privateKey.hex()
            )
            # This is a bytes array. Postgres will automatically convert it to hex?
            # Should we convert it to hex first? Then potentially the decrypt will be easier
            user.private_key = response['CiphertextBlob']

            user.address = account.address
        user.verified = True
        db.commit()
        access_token = AuthJWT().create_access_token(subject=user.id, expires_time=timedelta(minutes=60))
        return render(user, access_token)
    else:
        return {"message": "Invalid Code"}
