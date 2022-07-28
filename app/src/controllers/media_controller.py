from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import true
from sqlalchemy.orm import Session

from app.src.clients.alchemy_client import AlchemyClient
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.models.models import Media
from app.src.services.auth_service import get_current_user_id
from app.src.requests.create_media_request import CreateMediaRequest, CreateMediaData
from app.src.services.media_service import MediaService
from app.src.services.user_service import UserService
from app.src.views.media_view import MediaView

router = APIRouter(prefix="/media", tags=["media"])
logger = LoggerConfig(__name__).get()


@router.post("/upload", response_model=MediaView)
def upload_to_ipfs(
        name: str,
        description: str = 'Minted through https://www.wally.xyz',
        upload_file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    # TODO V2 - Determine how much of this call should hit the Wallet API
    media = MediaService.upload_to_ipfs(db, user, upload_file, CreateMediaData(name, description))
    return MediaView(media)


@router.get("/alchemy_client_recent", response_model=MediaView)
def alchemy_client_recent(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    nfts = AlchemyClient.get_nfts(user.address)
    logger.info(f"Alchemy NFT Response: {nfts}")
    media = db.query(Media)\
        .filter(Media.user == user and Media.is_confirmed == true()).order_by(Media.created_at.desc()).first()
    MediaService.update_from_alchemy_nft_data(db, media, nfts)
    db.commit()
    return MediaView(media)


@router.get("/recent", response_model=MediaView)
def get_recent_media(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    media = MediaService.get_most_recent(db, user)
    return MediaView(media)


@router.get("/{media_id}", response_model=MediaView)
def get_media_by_id(
        media_id: str,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    media = MediaService.get(db, media_id)
    if media.user_id != user_id:
        raise Exception("Unauthorized")
    return MediaView(media)
