from pydantic.dataclasses import dataclass

from app.src.models.models import User
from app.src.views.user_view import UserView


@dataclass
class UserLoginResponse:
    user_view: UserView
    access_token: str
    refresh_token: str

    def __init__(self, user: User, access_token, refresh_token):
        self.user_view = UserView(user)
        self.access_token = access_token
        self.refresh_token = refresh_token
