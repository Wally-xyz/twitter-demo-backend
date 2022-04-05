import string
import random
from datetime import timedelta
from typing import Optional

import boto3
from fastapi import APIRouter, Depends
from pydantic import EmailStr

from sqlalchemy.orm import Session
from web3 import Web3
from web3.middleware import geth_poa_middleware

from app.src.config.parameter_store import Properties
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.models.typedefs.EthereumNetwork import EthereumNetwork
from app.src.requests.user_login_response import UserLoginResponse
from app.src.services.auth_service import get_current_user_id
from app.src.services.email_service import EmailService
from app.src.services.user_service import UserService
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/auth", tags=["users"])
logger = LoggerConfig(__name__).get()
kms_client = boto3.client("kms")


@router.post("/refresh", response_model=UserLoginResponse)
def create_or_resend_code(
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
        access_token: Optional[str] = None,
):
    user = UserService.get(db, user_id)
    access_token = AuthJWT().create_access_token(subject=user.id, expires_time=timedelta(minutes=60))
    refresh_token = AuthJWT().create_refresh_token(subject=user.id, expires_time=timedelta(days=60))
    return UserLoginResponse(user=user, access_token=access_token, refresh_token=refresh_token)


@router.post("/sendcode")
def create_or_resend_code(
        email: EmailStr,
        db: Session = Depends(get_db),
):
    user = UserService.get_by_email(db, email)
    if not user:
        user = UserService.create_from_email(db=db, email=email)
    code = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
    EmailService.send_verification_code(user, code)
    user.verification_code = code
    db.commit()
    return {"message": "OK"}


@router.post("/verifyemail", response_model=UserLoginResponse)
def verify_email(
        email: str,
        code: str,
        db: Session = Depends(get_db),
):
    user = UserService.get_by_email(db, email)
    if user.verification_code == code:
        if not user.private_key:
            w3 = Web3(Web3.HTTPProvider(Properties.alchemy_node_url))
            if Properties.network == EthereumNetwork.RINKEBY:
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            account = w3.eth.account.create()
            # Encoded Private Key
            response = kms_client.encrypt(
                KeyId=Properties.kms_db_key_alias,
                Plaintext=account.privateKey.hex()
            )
            # This is a bytes array. Postgres will automatically convert it to hex
            # Should we convert it to hex first? Then potentially the decrypt will be easier
            user.private_key = response['CiphertextBlob']

            user.address = account.address
        user.verified = True
        db.commit()
        access_token = AuthJWT().create_access_token(subject=user.id, expires_time=timedelta(minutes=60))
        refresh_token = AuthJWT().create_refresh_token(subject=user.id, expires_time=timedelta(days=60))
        return UserLoginResponse(user, access_token, refresh_token)
    else:
        return {"message": "Invalid Code"}
