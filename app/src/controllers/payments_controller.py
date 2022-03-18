
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.src.services.payment_service import PaymentService
from app.src.services.auth_service import get_current_user_id
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig

router = APIRouter(prefix="/payments")
logger = LoggerConfig(__name__).get()


@router.post("/checkoutsession")
def create_checkout_session(
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    redirect_url = PaymentService.create_payment(db=db, user_id=user_id)
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
