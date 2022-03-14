import os

from fastapi import APIRouter, Depends
import stripe
from web3 import Web3
from web3.types import ABI
from sqlalchemy.orm import Session

from app.src.config.parameter_store import Properties
from app.src.services.auth_service import get_current_user_id
from app.src.models.models import User
from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig

router = APIRouter(prefix="/payments")
logger = LoggerConfig(__name__).get()

stripe.api_key = Properties.stripe_api_key


@router.post("/checkoutsession")
def create_checkout_session(
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1KdEBBBRQJlh59702ERTzDWh',  # TODO - Calculate on demand? Pull from parameter store?
                    'quantity': 1,
                },
            ],
            mode='payment',
            # It seems like this should redirect to a FE url?
            # Which then pings our backend with additional information...?
            success_url=Properties.base_domain + '/payments/record?success=True',
            cancel_url=Properties.base_domain + '/payments/record?success=False',
        )
    except Exception as e:
        return str(e)

    return {"checkout_session": checkout_session.url}


# This is hit from the redirect of the PaymentURL thing
@router.get("/record")
def create_checkout_session(
        success: bool,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    # Write success/failure to DB
    # If success, allow the user to continue?
    # Do some stuff
    return {"Redirect result": success}
