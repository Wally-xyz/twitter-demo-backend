import logging.config


class LoggerConfig:
    module_name: str

    def __init__(self, module_name: str):
        self.module_name = module_name

    def get(self):
        logging.config.fileConfig("app/src/logger.ini")
        return logging.getLogger(self.module_name)
