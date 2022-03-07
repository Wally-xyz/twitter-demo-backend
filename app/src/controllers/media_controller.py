import io
import uuid
from typing import Optional

import boto3
import requests
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.src.clients.pinata_client import PIN_URL
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import S3BucketConfig, Properties
from app.src.models.models import Media
from app.src.views.media_view import MediaView

router = APIRouter(prefix="/media")
logger = LoggerConfig(__name__).get()


@router.post("/upload")
def upload_to_ipfs(
        upload_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    filename = upload_file.filename
    logger.info(f"Uploading media, File object = {filename}")
    headers = {'Authorization': f'Bearer {Properties.pinata_jwt}'}
    contents = upload_file.file.read()

    result = requests.post(url=PIN_URL,
                           files={"file": contents},
                           data={"pinataOptions": '{"cidVersion":0}'},
                           headers=headers)

    # Also put the file to S3
    s3 = boto3.client("s3")
    s3_key = str(uuid.uuid4())
    s3.upload_fileobj(io.BytesIO(contents), S3BucketConfig.media_bucket, s3_key)

    logger.info(result.json())

    ipfs_hash = result.json()['IpfsHash']
    pin_size = result.json()["PinSize"]

    media_object = Media(ipfs_hash=ipfs_hash, pin_size=pin_size, filename=filename, key=s3_key)
    db.add(media_object)
    db.commit()
    db.refresh(media_object)

    logger.info(f"{result.json()}")
    return MediaView(media_object)


@router.put("/{media_id}")
def update_media(
        media_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        db: Session = Depends(get_db)
):
    media_object = db.query(Media).filter(Media.id == media_id).first()
    if name:
        media_object.name = name
    if description:
        media_object.description = description
    db.commit()
    db.refresh(media_object)

    return MediaView(media_object)
