# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import abc
import fastapi
import uvicorn
import asyncio
import pydantic as pyd

from ..processes.base import ProcessV1

# ---ENGINEV1-------------------------------------------------------------------
class EngineV1(abc.ABC):
    """
    Base class for V1 type engines.
    """

    @pyd.validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self, 
        state: pyd.BaseModel,
        processes: tp.List[ProcessV1],
        entities: tp.List[pyd.BaseModel],
    ):
        self.state = state
        self.processes = processes
        self.entities = entities
        self.schedule = None
    
    def _update_schedule(self):
        if self.schedule is None:
            schedule = []
            



    