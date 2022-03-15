from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from web3 import Web3

from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.auth_service import get_current_user_id
from eth_account.messages import encode_defunct
from pydantic import BaseModel

router = APIRouter(prefix="/tokens")
logger = LoggerConfig(__name__).get()


class Message(BaseModel):
    message: str  # should come in as hex encoded


# @router.get("/")
# def retrieve():
#     token = request.args.get('token')
#     maskedToken = sha1(token)
#     user = User.query.filter_by(token=maskedToken)

@router.get("/wallet")
def get_wallet(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    return {'data': user.address}


@router.post("/sign")
def sign_message(
        messageData: Message,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id),
):
    user = db.query(User).filter(User.id == user_id).first()
    ex_msg = bytearray.fromhex(messageData.message[2:]).decode()
    message = encode_defunct(text=ex_msg)
    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/37SaPgF-UEVyGxqZXtDBMKykQt2Ya4Er"))
    signed_msg = w3.eth.account.sign_message(message, private_key=user.private_key)
    return {'result': signed_msg.signature.hex()}
