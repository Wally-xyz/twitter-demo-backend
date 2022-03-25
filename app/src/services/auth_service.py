from typing import Optional
from fastapi import HTTPException
from fastapi_jwt_auth.exceptions import InvalidHeaderError
from starlette.status import HTTP_403_FORBIDDEN
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends


async def get_current_user_id(
        access_token: Optional[str] = None,
        authorize: AuthJWT = Depends(),
):
    try:
        # This is a bit of a hack to allow the access_token to come into the request
        if access_token:
            authorize._token = access_token
        authorize.jwt_required(token=access_token)
        return authorize.get_jwt_subject()
    except KeyError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")
    # NOTE(john) - I thought this might catch {"detail": "Signature has expired"} errors
    # But I think it happens one level sooner, in the AuthJWT = Depends() on line 11?
    # except InvalidHeaderError:
    #     raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Authorization Expired")
