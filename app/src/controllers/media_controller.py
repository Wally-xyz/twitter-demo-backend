import logging

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.models.models import User, Media
from app.src.services.auth_service import get_current_user_id
from app.src.requests.create_media_request import CreateMediaRequest, CreateMediaData
from app.src.services.media_service import MediaService
from app.src.services.user_service import UserService
from app.src.views.media_view import MediaView

router = APIRouter(prefix="/media")
logger = LoggerConfig(__name__).get()


@router.post("/upload")
def upload_to_ipfs(
        name: str,
        description: str = 'Minted through https://www.wallylabs.xyz',
        upload_file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    media = MediaService.upload_to_ipfs(db, user, upload_file, CreateMediaData(name, description))
    return MediaView(media)


@router.get("/recent")
def get_recent_media(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    media = db.query(Media).filter(Media.user == user).order_by(Media.created_at.desc()).first()
    return MediaView(media)


@router.get("/{media_id}")
def get_media_by_id(
        media_id: str,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    media = MediaService.get(db, media_id)
    if media.user_id != user_id:
        raise Exception("Unauthorized")
    return MediaView(media)

#
# @router.put("/{media_id}")
# def update_media(
#         media_id: str,
#         req: CreateMediaRequest,
#         db: Session = Depends(get_db),
#         user_id: str = Depends(get_current_user_id)
# ):
#     media = MediaService.update(db, media_id, user_id, req.to_data())
#     return MediaView(media)
# 

# Authenticated
# @router.put("/{media_id}")
# def associate(
#         media_id: str,
#         name: Optional[str] = None,
#         description: Optional[str] = None,
#         db: Session = Depends(get_db)
# ):
#     media_object = db.query(Media).filter(Media.id == media_id).first()
#     if name:
#         media_object.name = name
#     if description:
#         media_object.description = description
#     db.commit()
#     db.refresh(media_object)
# 
#     return MediaView(media_object)
