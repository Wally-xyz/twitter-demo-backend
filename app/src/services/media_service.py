import io
import json
import mimetypes
import uuid
from typing import Optional, Dict, Any

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
    def get_most_recent(db: Session, user: User) -> Media:
        return db.query(Media).filter(Media.user == user).order_by(Media.created_at.desc()).first()

    @staticmethod
    def update(db: Session, media_id: str, user_id: str, data: CreateMediaData) -> Media:
        media_object = MediaService.get(db, media_id)
        if media_object.user_id != user_id:
            raise Exception(f"Insufficient Permissions. UserId {user_id} can not update Media {media_id}")

        if data.name:
            media_object.name = data.name
        if data.description:
            media_object.description = data.description
        db.commit()
        db.refresh(media_object)
        return media_object

    @staticmethod
    def update_from_alchemy_nft_data(db: Session, media: Media, nfts: Dict[str, Any]):
        # NOTE - We are making an assumption that the media here correlates to the most recent NFT owned by this user
        # NOTE - Should filter through the ownedNFTs and properly pick the one associated with this txnHash
        most_recent_nft = nfts["ownedNfts"][-1]
        if not media.token_id:
            media.token_id = int(most_recent_nft["id"]["tokenId"], 16)
        if not media.address:
            media.address = most_recent_nft["contract"]["address"]
        db.commit()

    # TODO - Refactor some of this to pinata client
    @staticmethod
    def upload_to_ipfs(db: Session, user: User, upload_file: UploadFile, data: CreateMediaData) -> Media:
        headers = {'Authorization': f'Bearer {Properties.pinata_jwt}'}
        filename = upload_file.filename
        contents = upload_file.file.read()
        ipfs_metadata = {"name": data.name,
                         "keyvalues": {
                             "description": data.description
                         }}

        media_result = requests.post(url=PIN_URL,
                                     files={"file": contents},
                                     data={
                                         "pinataOptions": '{"cidVersion":0}',
                                         "pinataMetadata": json.dumps(ipfs_metadata)
                                     },
                                     headers=headers)

        media_ipfs_hash = media_result.json()["IpfsHash"]
        ipfs_image_url = f'https://gateway.pinata.cloud/ipfs/{media_ipfs_hash}'

        json_file = {'name': data.name,
                     'description': data.description,
                     'image': ipfs_image_url,
                     }
        ipfs_metadata["name"] = "json-" + ipfs_metadata["name"]

        json_result = requests.post(url=PIN_JSON_URL,
                                    json={
                                        "pinataOptions": {"cidVersion": 0},
                                        "pinataMetadata": ipfs_metadata,
                                        "pinataContent": json_file,
                                    },
                                    headers=headers)
        json_ipfs_hash = json_result.json()["IpfsHash"]

        logger.info(media_result.json())

        # Also put the file to S3
        s3_key = str(uuid.uuid4())
        logger.info(f"Content Type {upload_file.content_type}")

        boto3.client("s3").upload_fileobj(io.BytesIO(contents), Properties.media_bucket, s3_key,
                                          ExtraArgs={'ACL': 'public-read',
                                                     'ContentType': upload_file.content_type}
                                          )

        media_object = Media(json_ipfs_hash=json_ipfs_hash, media_ipfs_hash=media_ipfs_hash,
                             filename=filename, s3_key=s3_key, user_id=user.id, name=data.name,
                             description=data.description, ipfs_image_url=ipfs_image_url)

        db.add(media_object)
        db.commit()
        db.refresh(media_object)
        return media_object
