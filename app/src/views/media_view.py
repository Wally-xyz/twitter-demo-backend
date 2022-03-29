from dataclasses import dataclass
from typing import Optional

from app.src.config.parameter_store import Properties
from app.src.models.models import Media


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
        self.s3_url = f"https://{Properties.media_bucket}.s3.amazonaws.com/{media.s3_key}"
        self.etherscan_url = f"{Properties.etherscan_url}/tx/{media.txn_hash}" if media.txn_hash else None
        self.opensea_url = f"{Properties.opensea_collection_url}/{media.token_id}" if media.token_id else None
        self.nonce = media.nonce
