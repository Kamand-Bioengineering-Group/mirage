# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import abc
import socket
import fastapi
import uvicorn
import threading
import pydantic as pyd

from ..processes.base import ProcessV1


# ---ENGINEV1-------------------------------------------------------------------
class EngineV1(abc.ABC):
    """
    Base class for V1 type engines.
    """
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}

    @pyd.validate_call(config={"arbitrary_types_allowed": True})
    def __init__(
        self,
        state: pyd.BaseModel,
        processes: tp.List[ProcessV1],
        entities: tp.List[pyd.BaseModel],
        speed: int = 6,
        port: int = 8000,
        auth: str = None,
        enable_remote_connection: bool = False,
    ):
        """
        Initialize the engine.

        Parameters:
        -----------
        state: pyd.BaseModel
            The state of the engine.
        processes: List[ProcessV1]
            The processes of the engine.
        entities: List[pyd.BaseModel]
            The entities of the engine.
        speed: int
            The speed of the engine.
        """
        self.state = state
        self.processes = processes
        self.entities = entities
        self.speed = speed
        if enable_remote_connection:
            self.port = port
            self.auth = auth
            self.app = fastapi.FastAPI()
        
        self.status = "DORMANT"

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: int):
        assert value >= 1 and isinstance(
            value, int
        ), "`speed` >= 1 and must be an integer"
        self._speed = value

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value: str):
        assert value in self.STATUS_SET, f"Invalid status: {value}"
        self._status = value

    def get_schedule(self) -> tp.List[ProcessV1]:
        """
        Get the schedule of the processes.

        Returns:
        --------
        List[ProcessV1]
            The schedule of the processes sorted by rank and class name.
        """
        schedule = sorted(
            self.processes,
            key=lambda p: (p.RANK, p.__class__.__name__),
        )
        return schedule

    def prune_processes(self):
        """
        Remove dead processes from the engine.
        """
        self.processes = [p for p in self.processes if p.status != "DEAD"]

    @pyd.validate_call
    def run(self, step: int):
        schedule = self.get_schedule()
        unique_ranks = set(p.RANK for p in schedule)
        current_rank = unique_ranks.pop()

        for process in schedule:
            if process.RANK == current_rank:
                process.run(step)
            else:
                current_rank = unique_ranks.pop()
                process.run(step)

        self.prune_processes()


    def fire(self):
        """
        Fire the engine.
        """
        def simulation_loop():
            while self.status != "DEAD":
                ...


