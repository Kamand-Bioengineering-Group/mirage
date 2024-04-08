# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import abc
import socket
import asyncio
import fastapi
import uvicorn
import pydantic as pyd

from ..processes.base import ProcessV1


# ---ENGINEV1-------------------------------------------------------------------
class EngineV1(abc.ABC):
    """
    Base class for V1 type engines.
    """

    @pyd.validate_call(config={"arbitrary_types_allowed": True})
    def __init__(
        self,
        state: pyd.BaseModel,
        processes: tp.List[ProcessV1],
        entities: tp.List[pyd.BaseModel],
    ):
        self.state = state
        self.processes = processes
        self.entities = entities
        self.CLIENT = {
            "HOST": socket.gethostbyname(socket.gethostname()),
            "AUTH": "njdcijdvjdncjd ",
        }

    @pyd.validate_call(
        config={"arbitrary_types_allowed": True},
        validate_return=True,
    )
    def get_schedule(self) -> tp.List[ProcessV1]:
        schedule = sorted(
            self.processes,
            key=lambda p: (p.RANK, p.__class__.__name__),
        )
        return schedule

    @pyd.validate_call
    def step(self, delta: int):
        schedule = self.get_schedule()
        for process in schedule:
            process.run()

    def commit(self): ...

