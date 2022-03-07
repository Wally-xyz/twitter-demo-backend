from dataclasses import dataclass
from typing import Optional

from app.src.models.models import Media


@dataclass
class MediaView:
    id: str
    name: Optional[str]
    description: Optional[str]
    ipfs_hash: str
    pin_size: int

    def __init__(self, media: Media):
        self.id = media.id
        self.name = media.name
        self.description = media.description
        self.ipfs_hash = media.ipfs_hash
        self.pin_size = media.pin_size
