import string
import random
from datetime import timedelta
from typing import Optional
import requests

import boto3
from fastapi import APIRouter, Depends
from pydantic import EmailStr

from sqlalchemy.orm import Session

from app.src.config.parameter_store import Properties
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.requests.user_login_response import UserLoginResponse
from app.src.services.auth_service import get_current_user_id
from app.src.services.email_service import EmailService
from app.src.services.user_service import UserService
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/auth", tags=["users"])
logger = LoggerConfig(__name__).get()
kms_client = boto3.client("kms")


@router.post("/refresh", response_model=UserLoginResponse)
def refresh_token(
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
        user.verified = True
        db.commit()
        # TODO V2 - Hit Wallet Backend to create user on their end
        headers = {
            'Authorization': f'Bearer {Properties.wally_api_key}'
        }
        r = requests.post(
            f'{Properties.wally_api_url}/wallets/create',
            data={
                'email': email,
                'id': user.id,
            },
            headers=headers,
        )
        address = r.json().get('address')
        if not address:
            r = requests.get(
                f'{Properties.wally_api_url}/wallet/{user.id}',
                headers=headers,
            )
            address = r.json().get('address')
        access_token = AuthJWT().create_access_token(subject=user.id, expires_time=timedelta(minutes=60))
        refresh_token = AuthJWT().create_refresh_token(subject=user.id, expires_time=timedelta(days=60))
        return UserLoginResponse(user, access_token, refresh_token, address)
    else:
        return {"message": "Invalid Code"}
