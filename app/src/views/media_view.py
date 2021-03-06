from typing import Optional

from pydantic.dataclasses import dataclass

from app.src.config.parameter_store import Properties
from app.src.models.models import Media

opensea_collection_url = f"{Properties.opensea_url}/assets"


@dataclass
class MediaView:
    id: str
    name: Optional[str]
    description: Optional[str]
    json_ipfs_hash: str
    url: str
    s3_url: str
    etherscan_url: Optional[str]
    opensea_url: Optional[str]
    nonce: Optional[str]

    def __init__(self, media: Media):
        self.id = media.id
        self.name = media.name
        self.description = media.description
        self.json_ipfs_hash = media.json_ipfs_hash
        self.url = media.ipfs_image_url
        self.s3_url = media.s3_url()
        self.etherscan_url = f"{Properties.etherscan_url}/tx/{media.txn_hash}" if media.txn_hash else None
        self.opensea_url = f"{opensea_collection_url}/{media.address}/{media.token_id}" if media.token_id else None
        self.nonce = media.nonce
