import hmac
import hashlib
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.clients.alchemy_client import AlchemyClient
from app.src.config.parameter_store import Properties
from app.src.models.models import Media
from app.src.requests.alchemy_mined_transaction_request import AlchemyMinedTransaction
from app.src.services.email_service import EmailService
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.services.media_service import MediaService

router = APIRouter(prefix="/webhooks")
logger = LoggerConfig(__name__).get()


@router.post("/alchemy/mined")
def alchemy_mined_webhook(
        req: AlchemyMinedTransaction,
        db: Session = Depends(get_db),
):
    # TODO - Header validation things
    logger.info(f"Alchemy Webhook: {req}")
    media = db.query(Media).filter(Media.txn_hash == req.fullTransaction.hash).first()
    if not media:
        logger.error(f"Webhook: {req} did not find Media with hash {req.fullTransaction.hash}")
        raise Exception("Not Found")
    media.is_confirmed = True
    media.nonce = req.fullTransaction.nonce
    try:
        nfts = AlchemyClient.get_nfts(media.user.address)
        MediaService.update_from_alchemy_nft_data(db, media, nfts)
    except Exception:
        logger.warn("Unable to get nfts transactionID data")
    db.commit()
    EmailService.send_mined_email(media)
    return {"msg": "OK"}


# TODO - Some email on drop
@router.post("/alchemy/dropped")
def alchemy_dropped_webhook(
        req: AlchemyMinedTransaction,
        db: Session = Depends(get_db),
):
    # Write success/failure to DB
    # If success, allow the user to continue?
    # Do some stuff
    return {"Redirect result": "N/A"}


# TODO - Implement
# https://docs.alchemy.com/alchemy/guides/using-notify#2.-validate-the-signature-received
def is_valid_signature(request):
    token = Properties.alchemy_auth_token
    headers = request['headers']
    signature = headers['x-alchemy-signature']
    body = request['body']
    string_body = json.dumps(body, separators=(',', ':'))

    digest = hmac.new(
        bytes(token, 'utf-8'),
        msg=bytes(string_body, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature == digest
