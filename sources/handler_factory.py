from models.config import Source
from sources.base_handler import BaseHandler

class HandlerFactory():
    @staticmethod
    def get_handler(handler_name: str, config: Source) -> BaseHandler:
        if handler_name == 'roboflow':
            from sources.roboflow_handler import RoboflowHandler
            return RoboflowHandler(handler_name, config)
        if handler_name == 'kaggle':
            from sources.kaggle_handler import KaggleHandler
            return KaggleHandler(handler_name, config)
        raise ValueError(f"Unknown handler: {handler_name}")