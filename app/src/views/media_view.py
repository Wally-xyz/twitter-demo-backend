from dataclasses import dataclass
from typing import Optional

from app.src.models.models import Media


@dataclass
class MediaView:
    id: str
    name: Optional[str]
    description: Optional[str]
    json_ipfs_hash: str
    url: str

    def __init__(self, media: Media):
        self.id = media.id
        self.name = media.name
        self.description = media.description
        self.json_ipfs_hash = media.json_ipfs_hash
        self.url = media.ipfs_image_url
