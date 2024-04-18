# ---INFO-----------------------------------------------------------------------
"""
Module for logging engine activity.
"""

__all__ = [
    "EngineV1Logger",
]

# ---DEPENDENCIES---------------------------------------------------------------
import logging


# ---EngineV1Logger-------------------------------------------------------------
class EngineV1Logger(logging.Logger):
    """
    Logger for EngineV1 type.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name)
        self.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.addHandler(handler)
        self.propagate = False
