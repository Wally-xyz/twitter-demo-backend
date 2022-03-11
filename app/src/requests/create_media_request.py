from typing import Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


# Optional or required?
class CreateMediaRequest(BaseModel):
    name: Optional[str] = "MyName"
    description: Optional[str] = "MyDescription"

    def to_data(self):
        return CreateMediaData(name=self.name, description=self.description)


@dataclass
class CreateMediaData:
    name: Optional[str]
    description: Optional[str]
