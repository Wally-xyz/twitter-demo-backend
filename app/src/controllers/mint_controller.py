import os
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.config.parameter_store import Properties
from app.src.models.models import User, Media
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.models.typedefs.EthereumNetwork import EthereumNetwork
from app.src.services.auth_service import get_current_user_id
from app.src.services.media_service import MediaService
from app.src.services.payment_service import PaymentService
from app.src.services.user_service import UserService

router = APIRouter(prefix="/mint", tags=["media"])
logger = LoggerConfig(__name__).get()


@router.get("/media")
def get_media(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    media = MediaService.get_most_recent(db, user)
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
        media = MediaService.get_most_recent(db, user)
    else:
        media = MediaService.get(db, media_id)
    logger.info(f"Minting media: {media.id}")
    payment = PaymentService.open_payment(db, user)
    if not payment and not user.admin:
        raise Exception("No record of payment. If you believe this is in error, contact us at: ...")

    # Hit Wallet Backend and call mint endpoint
    # Determine what we want to store from their response

    db.commit()
    if payment:
        PaymentService.associate_media_with_payment(db, payment, media.id)
    # TODO - Return Media View here instead of hash
    return {"hash": media.txn_hash}
