
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from web3 import Web3

from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from eth_account.messages import encode_defunct

router = APIRouter(prefix="/tokens")
logger = LoggerConfig(__name__).get()


# @router.get("/")
# def retrieve():
#     token = request.args.get('token')
#     maskedToken = sha1(token)
#     user = User.query.filter_by(token=maskedToken)

@router.get("/sign")
def sign_message(
        message: str = "Reddit Year in Review",
        username: str = "u_123",  # Convert to user_id?
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    ex_msg = bytearray.fromhex(message[2:]).decode()
    message = encode_defunct(text=ex_msg)
    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/37SaPgF-UEVyGxqZXtDBMKykQt2Ya4Er"))
    signed_msg = w3.eth.account.sign_message(message, private_key=user.privateKey)
    return {'result': signed_msg.signature.hex()}
