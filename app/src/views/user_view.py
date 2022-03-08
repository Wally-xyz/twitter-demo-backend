from dataclasses import dataclass
from typing import Optional

from app.src.models.models import User


@dataclass
class UserView:
    id: str
    email: str
    address: Optional[str]

    def __init__(self, user: User):
        self.id = user.id
        self.email = user.email
        self.address = user.address
