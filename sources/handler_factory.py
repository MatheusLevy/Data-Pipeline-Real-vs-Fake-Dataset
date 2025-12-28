from sources.roboflow_handler import RoboflowHandler

class HandlerFactory():
    @staticmethod
    def get_handler(handler_name: str, config: dict):
        if handler_name == 'roboflow':
            return RoboflowHandler(handler_name, config)
        raise ValueError(f"Unknown handler: {handler_name}")