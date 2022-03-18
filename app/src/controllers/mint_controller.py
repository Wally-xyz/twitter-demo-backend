import os
from typing import Optional

from fastapi import APIRouter, Depends
from web3 import Web3
from sqlalchemy.orm import Session

from app.src.config.parameter_store import Properties
from app.src.models.models import ABI, User, Media
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.auth_service import get_current_user_id
from app.src.services.email_service import EmailService
from app.src.services.media_service import MediaService
from app.src.services.payment_service import PaymentService
from app.src.services.user_service import UserService

router = APIRouter(prefix="/mint")
logger = LoggerConfig(__name__).get()


@router.get("/media")
def get_media(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    media = db.query(Media).filter(Media.user == user).order_by(Media.created_at.desc()).first()
    # TODO - Return media view
    return {'data': media.media_ipfs_hash}


@router.post("/mint")
def mint(
        media_id: Optional[str] = None,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    if not media_id:
        media = db.query(Media).filter(Media.user == user).first()
    else:
        media = MediaService.get(db, media_id)
    logger.info(f"Minting media: {media.id}")
    payment = PaymentService.open_payment(db, user)
    if not payment:
        raise Exception("No record of payment. If you believe this is in error, contact us at: ...")

    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/37SaPgF-UEVyGxqZXtDBMKykQt2Ya4Er"))
    # Needs to be set to estimate gas for transaction
    w3.eth.defaultAccount = Properties.vault_public_key
    address = user.address
    contract = db.query(ABI).order_by(ABI.created_at.desc()).first()
    abi = contract.data
    minter = w3.eth.contract(abi=abi, address=contract.address)
    max_priority_fee = w3.eth.max_priority_fee
    ipfs_hash = media.json_ipfs_hash
    nonce = w3.eth.getTransactionCount(w3.eth.account.from_key(Properties.vault_private_key).address)
    built_txn = minter.functions.mintNFT(address, ipfs_hash).buildTransaction({
        'nonce': nonce,
        # 'maxFeePerGas': max_priority_fee + w3.eth.gas_price,
        # this doesn't seem to be outputting the correct value, not sure why yet
        # 'maxPriorityFeePerGas': max_priority_fee,
    })

    signed_txn = w3.eth.account.signTransaction(built_txn, private_key=Properties.vault_private_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    EmailService.send_minted_email(user, txn_hash.hex())
    media.txn_hash = txn_hash
    db.commit()
    PaymentService.associate_media_with_payment(db, payment, media.id)
    return {"hash": txn_hash.hex()}


# TODO - Remove username and contract_id from this endpoint
# Make it behind the authentication so it pulls the user from the logged-in session JWT token
# Get the contract_id from the database (we'll only ahave one right?
# @router.post("/username")
# def mint_with_username(
#         contract_id: str,
#         username: str,
#         db: Session = Depends(get_db)
# ):
#     user = User.query.filter_by(username=username).first()
#     w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/37SaPgF-UEVyGxqZXtDBMKykQt2Ya4Er"))
#     if not user:
#         account = w3.eth.account.create()
#         user = User(
#             private_key=account.privateKey,
#             username=username,
#             address=account.address
#         )
#         db.session.add(user)
#         db.session.commit()
#     address = user.address
#     contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
#     abi = contract.data
#     w3.eth.defaultAccount = os.environ.get("PUBLIC_KEY")
#     minter = w3.eth.contract(abi=abi, address=contract.address)
#     max_priority_fee = w3.eth.max_priority_fee
#     media = Media.query.filter_by(User=user)
#     ipfs_hash = media.ipfs_hash
#     built_txn = minter.functions.mintNFT(address, ipfs_hash).buildTransaction({
#         'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
#         'maxFeePerGas': max_priority_fee + w3.eth.gas_price,
#         # this doesn't seem to be outputting the correct value, not sure why yet
#         'maxPriorityFeePerGas': max_priority_fee,
#     })
#     signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
#     tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     return {"hash": tx_hash.hex()}

#
# @router.post("/email")
# def mint_with_email(
#         contract_id: str,
#         email: str,
#         db: Session = Depends(get_db)
# ):
#     user = User.query.filter_by(email=email).first()
#     w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
#     if not user:
#         account = w3.eth.account.create()
#         user = User(
#             private_key=account.privateKey,
#             username=email,
#             address=account.address,
#             email=email,
#         )
#         db.session.add(user)
#         db.session.commit()
#     address = user.address
#     contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
#     abi = contract.data
#     Minter = w3.eth.contract(abi=abi, address=contract.address)
#     maxPriorityFee = w3.eth.max_priority_fee
#     built_txn = Minter.functions.mintNFT(address, "0x00").buildTransaction({
#         'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
#         'maxFeePerGas': maxPriorityFee + w3.eth.gas_price,
#         'maxPriorityFeePerGas': maxPriorityFee,
#     })
#     signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
#     tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     token = generateRandomString()
#     maskedToken = sha1(token)
#     saveToken(user, maskedToken)
#     message = Mail(
#         from_email=('hello@zentacle.com', 'Zentacle'),
#         to_emails='mayank@zentacle.com')
#
#     message.template_id = 'd-df22c68e00c345108a3ac18ebf65bdaf'
#     message.dynamic_template_data = {
#         'org': 'Reddit',
#         'description': 'You were granted a NFT',
#         'url': 'http://localhost:8000/token?token=' + token,
#     }
#     if not os.environ.get('FLASK_ENV') == 'development':
#         try:
#             sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#             sg.send(message)
#         except Exception as e:
#             print(e.body)
#     return jsonify(tx_hash.hex())
