import traceback
from urllib.request import Request

import psutil
import time
from datetime import timedelta
from fastapi import FastAPI

from app.src.config.logger_config import LoggerConfig
from app.src.controllers import (
    contract_controller,
    mint_controller,
    media_controller,
)

logger = LoggerConfig(__name__).get()
logger.info("API Booting up....")

app = FastAPI()
app.include_router(contract_controller.router)
app.include_router(mint_controller.router)
app.include_router(media_controller.router)


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
