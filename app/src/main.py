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


@app.get("/", include_in_schema=False)
def get_uptime():
    uptime = time.time() - psutil.boot_time()
    return {"uptime": "{:0>8}".format(str(timedelta(seconds=uptime)))}
