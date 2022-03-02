import os
from hashlib import sha1

from fastapi import APIRouter, Depends
from web3 import Web3
from web3.types import ABI
from sqlalchemy.orm import Session

from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig

from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

router = APIRouter(prefix="/mint")
logger = LoggerConfig(__name__).get()


@router.post("/username")
def mint_with_username(
        contract_id: str,
        username: str,
        db: Session = Depends(get_db)
):
    user = User.query.filter_by(username=username).first()
    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
    if not user:
        account = w3.eth.account.create()
        user = User(
            private_key=account.privateKey,
            username=username,
            address=account.address
        )
        db.add(user)
        db.commit()
    address = user.address
    contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
    abi = contract.data
    minter = w3.eth.contract(abi=abi, address=contract.address)
    built_txn = minter.functions.mintNFT(address, "0x00").buildTransaction({
        'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
        'gas': 7000000,
        'maxFeePerGas': w3.toWei('3', 'gwei'),
        'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
    })
    signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return {"hash": tx_hash.hex()}


@router.post("/email")
def mint_with_email(
        contract_id: str,
        email: str,
        db: Session = Depends(get_db)
):
    user = User.query.filter_by(email=email).first()
    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
    if not user:
        account = w3.eth.account.create()
        user = User(
            private_key=account.privateKey,
            username=email,
            address=account.address,
            email=email,
        )
        db.add(user)
        db.commit()
    address = user.address
    contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
    abi = contract.data
    Minter = w3.eth.contract(abi=abi, address=contract.address)
    built_txn = Minter.functions.mintNFT(address, "0x00").buildTransaction({
        'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
        'gas': 7000000,
        'maxFeePerGas': w3.toWei('3', 'gwei'),
        'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
    })
    signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    token = generateRandomString()
    maskedToken = sha1(token)
    saveToken(user, maskedToken)
    message = Mail(
        from_email=('hello@zentacle.com', 'Zentacle'),
        to_emails='mayank@zentacle.com')

    message.template_id = 'd-df22c68e00c345108a3ac18ebf65bdaf'
    message.dynamic_template_data = {
        'org': 'Reddit',
        'description': 'You were granted a NFT',
        'url': 'http://localhost:8000/token?token=' + token,
    }
    if not os.environ.get('FLASK_ENV') == 'development':
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            sg.send(message)
        except Exception as e:
            print(e)
    return {"hash": tx_hash.hex()}
