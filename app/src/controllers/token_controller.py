import boto3
import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.config.database_config import get_db
from app.src.config.parameter_store import Properties
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
    headers = {
        'Authorization': f'Bearer {Properties.wally_api_key}'
    }
    r = requests.get(
        f'{Properties.wally_api_url}/wallet/{user_id}',
        headers=headers,
    )
    address = r.json().get('address')
    # TODO V2 - Get user's wallet address
    return {'data': address}


@router.post("/sign")
def sign_message(
        message_data: Message,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id),
):
    user = UserService.get(db, user_id)

    headers = {
        'Authorization': f'Bearer {Properties.wally_api_key}'
    }
    r = requests.post(
        f'{Properties.wally_api_url}/wallet/{user_id}/sign-message',
        data={
            'message': message_data,
        },
        headers=headers,
    )
    # TODO V2 - Hit wallet backend to get signed message
    signed_msg = r.json().get('signature') # Should return it in the format I want

    return {'result': signed_msg}

@router.post("/decrypt")
def decrypt_wallet(
    private_key_data: Message,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    user = UserService.get(db, user_id)
    if not user.admin:
        return "Not an admin"
    decrypt_user = UserService.get(db, private_key_data.message)
    decrypted_private_key = kms_client.decrypt(
        CiphertextBlob=bytes.fromhex(decrypt_user.private_key[2:]),
        KeyId=Properties.kms_db_key_alias
    )['Plaintext'].decode('utf-8')
    return { 'private_key': decrypted_private_key }