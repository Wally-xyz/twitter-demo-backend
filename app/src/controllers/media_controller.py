import os
import uuid

import boto3
import requests
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.src.clients.pinata_client import PIN_URL
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import S3BucketConfig
from app.src.models.models import Media


router = APIRouter(prefix="/media")
logger = LoggerConfig(__name__).get()


@router.post("/upload")
def mint_with_username(
        upload_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    filename = upload_file.filename
    logger.info(f"Uploading media, File object = {filename}")
    # content_type = upload_file.content_type
    pinata_auth = os.getenv('PINATA_JWT')
    headers = {'Authorization': f'Bearer {pinata_auth}'}
    contents = upload_file.file.read()

    result = requests.post(url=PIN_URL,
                           files={"file": contents},
                           data={"pinataOptions": '{"cidVersion":0}'},
                           headers=headers)

    # Also put the file to S3
    s3 = boto3.resource("s3")
    s3_key = uuid.uuid4()
    s3.upload_fileobj(contents, S3BucketConfig.media_bucket, s3_key)

    ipfsHash = result.json()['IpfsHash']
    pinSize = result.json()["PinSize"]

    media_object = Media(ipfsHash=ipfsHash, pinSize=pinSize, filename=filename, key=s3_key)
    db.add(media_object)
    db.commit()

    logger.info(f"{result.json()}")
    return result.json()
