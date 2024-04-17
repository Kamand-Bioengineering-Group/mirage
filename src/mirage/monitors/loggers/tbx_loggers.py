# ---INFO-----------------------------------------------------------------------
"""
Module for logging engine activity.
"""

__all__ = []

# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import threading
import tensorboardX as tbx
from ...engines import EngineV1


# ---EngineV1Logger-------------------------------------------------------------
class TbxTimeseriesLoggerV1(tbx.SummaryWriter):
    """
    Logger for EngineV1 type.
    """

    def __init__(self, engine: EngineV1, log_dir: str):
        super().__init__(log_dir)
        self.engine = engine
        self.regobj = None

    def register_objects(
        self, object_attrs: tp.Dict[str, tp.Tuple[tp.Any, tp.Tuple[str]]]
    ):
        """
        Register objects for logging.

        Parameters
        ----------
        object_attrs : Dict[str, Tuple[Any, Tuple[str]]]
            Dictionary with name of plots, object in context and its attributes
            to log.
        """
        self.regobj = object_attrs

    def fire(self):
        """
        Start logging.
        """
        if self.regobj is not None:
            for name, (obj, attrs) in self.regobj.items():
                for attr in attrs:
                    self.add_scalar(
                        f"{name}/{attr}",
                        getattr(obj, attr),
                        self.engine.STEP,
                    )
        # engine.run_call_history is a list of timestamps when engine.run was
        # called plot the average time intervals for last 5 calls
        if len(self.engine.run_call_history) > 5:
            avg_time = (
                sum(
                    [
                        self.engine.run_call_history[i]
                        - self.engine.run_call_history[i + 1]
                        for i in range(-5, -1)
                    ]
                )
                / 5
            )
            self.add_scalar("RunTime", avg_time, self.engine.STEP)
