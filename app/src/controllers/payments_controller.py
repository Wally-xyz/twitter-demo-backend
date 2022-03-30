
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.models.models import Media
from app.src.services.payment_service import PaymentService
from app.src.services.user_service import UserService
from app.src.services.auth_service import get_current_user_id
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.views.media_view import MediaView

router = APIRouter(prefix="/payments")
logger = LoggerConfig(__name__).get()


@router.post("/checkoutsession")
def create_checkout_session(
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    user = UserService.get(db, user_id)
    media = db.query(Media).filter(Media.user == user).order_by(Media.created_at.desc()).first()
    redirect_url = PaymentService.create_payment(db=db, user_id=user_id, img_url=MediaView(media).s3_url)
    # The FE needs to redirect this url appropriately with the correct header?
    return {"checkout_session": redirect_url}


# This is hit from the redirect of the PaymentURL thing
# Ideally should be a PUT
@router.get("/{payment_id}/record")
def record_payment(
        success: bool,
        payment_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    # Write success/failure to DB
    PaymentService.update(db, user_id, payment_id, success)
    # If success, allow the user to continue?
    # Do some stuff
    return {"Redirect result": success}
