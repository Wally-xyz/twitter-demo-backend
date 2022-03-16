import io
import json
import logging
import uuid
from typing import Optional

import boto3
import requests
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.src.clients.pinata_client import PIN_URL, PinFileResponse, PIN_JSON_URL
from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import Properties
from app.src.models.models import User, Media
from app.src.requests.create_media_request import CreateMediaData

logger = LoggerConfig(__name__).get()


class MediaService:

    @staticmethod
    def get(db: Session, media_id: str) -> Media:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise Exception(f"Media with id {media_id} not found")
        return media

    @staticmethod
    def update(db: Session, media_id: str, user_id: str, data: CreateMediaData):
        media_object = MediaService.get(db, media_id)
        if media_object.user_id != user_id:
            raise Exception(f"Insufficient Permissions. UserId {user_id} can not update Media {media_id}")

        if data.name:
            media_object.name = data.name
        if data.description:
            media_object.description = data.description
        db.commit()
        db.refresh(media_object)

    @staticmethod
    def upload_to_ipfs(db: Session, user: User, upload_file: UploadFile, data: CreateMediaData) -> Media:
        headers = {'Authorization': f'Bearer {Properties.pinata_jwt}'}
        filename = upload_file.filename
        contents = upload_file.file.read()
        ipfs_metadata = {"name": data.name,
                         "keyvalues": {
                             "description": data.description
                         }}

        # TODO - IPFS Metadata using name/description fields
        media_result = requests.post(url=PIN_URL,
                                     files={"file": contents},
                                     data={
                                         "pinataOptions": '{"cidVersion":0}',
                                         "pinataMetadata": json.dumps(ipfs_metadata)
                                     },
                                     headers=headers)

        ipfs_hash = media_result.json()["IpfsHash"]

        json_file = {'name': data.name,
                     'description': data.description,
                     'image': f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}'
                     }
        ipfs_metadata["name"] = "json-" + ipfs_metadata["name"]

        json_result = requests.post(url=PIN_JSON_URL,
                                    json={
                                        "pinataOptions": {"cidVersion": 0},
                                        "pinataMetadata": ipfs_metadata,
                                        "pinataContent": json_file,
                                    },
                                    headers=headers)

        logger.info(media_result.json())

        # Also put the file to S3
        s3_key = str(uuid.uuid4())
        boto3.client("s3").upload_fileobj(io.BytesIO(contents), Properties.media_bucket, s3_key)

        json_ipfs_hash = json_result.json()["IpfsHash"]

        # TODO - Better unwinding of the response object
        # response = PinFileResponse(**result.json())

        media_object = Media(ipfs_hash=json_ipfs_hash, filename=filename, key=s3_key,
                             user_id=user.id, name=data.name, description=data.description)
        db.add(media_object)
        db.commit()
        db.refresh(media_object)
        return media_object
