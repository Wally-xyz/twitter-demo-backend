from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.requests.update_user_request import UpdateUserRequest
from app.src.services.auth_service import get_current_user_id
from app.src.services.user_service import UserService
from app.src.views.user_view import UserView

router = APIRouter(prefix="/user", tags=["users"])
logger = LoggerConfig(__name__).get()


@router.get("/", response_model=UserView)
def get_user(
        db: Session = Depends(get_db),
        logged_in_user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, logged_in_user_id)
    return UserView(user)


@router.patch("/", response_model=UserView)
def patch_user(
        request: UpdateUserRequest,
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    user = UserService.get(db, user_id)
    user = UserService.update(db, user, request.to_data())
    return UserView(user)


@router.get("/{user_id}", response_model=UserView)
def get_user_by_id(
        user_id: str,
        db: Session = Depends(get_db),
        logged_in_user_id: str = Depends(get_current_user_id)
):
    requested_user = UserService.get(db, user_id)
    logged_in_user = UserService.get(db, logged_in_user_id)
    if logged_in_user.admin or logged_in_user.id == requested_user.id:
        return UserView(requested_user)
    else:
        raise Exception("Not Authorized")

