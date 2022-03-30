import traceback
from urllib.request import Request

import psutil
import time
from datetime import timedelta

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware

from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import Properties
from app.src.controllers import (
    contract_controller,
    mint_controller,
    media_controller,
    token_controller,
    auth_controller,
    payments_controller,
    webhooks_controller,
    user_controller,
)

logger = LoggerConfig(__name__).get()
logger.info("API Booting up....")

# https://fastapi.tiangolo.com/tutorial/metadata/
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **auth/login** logic is also here.",
    },
    {
        "name": "media",
        "description": "Manage media. So _fancy_ they have their own docs.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.include_router(contract_controller.router)
app.include_router(mint_controller.router)
app.include_router(media_controller.router)
app.include_router(token_controller.router)
app.include_router(auth_controller.router)
app.include_router(payments_controller.router)
app.include_router(webhooks_controller.router)
app.include_router(user_controller.router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "https://wallet-frontend-one.vercel.app",
    "https://wallet-frontend-stage.vercel.app",
    "https://demo-stage.wallylabs.xyz",
    "https://demo.wallylabs.xyz",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return [("authjwt_secret_key", Properties.authjwt_secret_key)]


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.middleware("http")
async def default_middleware_logging(request: Request, call_next):
    url_path = str(request.url).replace(str(request.base_url), '').lstrip()
    base_log = f"{request.method} request made to {url_path}"
    try:
        response = await call_next(request)
        # NOTE(john) - Probably don't want this long term but leave it in for now
        # Might want to make it a "DEBUG" message, and only show it on dev/stage
        if url_path:
            logger.info(f"Successful {base_log}")
        return response
    except Exception as e:
        logger.warning(f"Failed {base_log}")
        logger.error(f"uncaught exception: {traceback.format_exc()}")
        # TODO - Add some Exception handlers here
        raise e


@app.get("/", include_in_schema=False)
def get_uptime():
    uptime = time.time() - psutil.boot_time()
    return {"uptime": "{:0>8}".format(str(timedelta(seconds=uptime)))}


# if __name__ == "__main__":
#     uvicorn.run("app.src.main:app", host='0.0.0.0', port=80, reload=True, debug=True, workers=3)
