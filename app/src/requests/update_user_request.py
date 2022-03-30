from typing import Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class UpdateUserRequest(BaseModel):
    twitter_handle: Optional[str] = None

    def to_data(self):
        return UpdateUserData(twitter_handle=self.twitter_handle)


@dataclass
class UpdateUserData:
    twitter_handle: Optional[str] = None

