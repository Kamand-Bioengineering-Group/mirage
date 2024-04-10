# ---INFO-----------------------------------------------------------------------
"""
Base classes for Processes. Processes change the state of the entities in a \
simulation.
"""

# TODO: feature: V2 type processes can modify processes and entities.
# TODO: feature: Processes of same RANK shouldn't change the state of an entity.
#       independently of each other.


__all__ = ["ProcessV1"]


# ---DEPENDENCIES---------------------------------------------------------------
import abc
import typing as tp
import pydantic as pyd


# ---PROCESSV1------------------------------------------------------------------
class ProcessV1(abc.ABC):
    """
    ProcessV1 type. Processes change the state of the entities in a simulation.

    Attributes:
    -----------
    RANK: int
        The rank of the process. Processes with higher ranks are run first.
    DOMAIN: List[pyd.BaseModel]
        The types of entities that the process can target.
    """

    RANK: int
    DOMAIN: tp.List[pyd.BaseModel]
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert hasattr(cls, "RANK"), "`ProcessV1` type must have a `RANK`."
        assert isinstance(cls.RANK, int | None), "`RANK` must be an `int`."
        assert hasattr(cls, "DOMAIN"), "`ProcessV1` must have `DOMAIN`."
        assert all(
            issubclass(tar, pyd.BaseModel) for tar in cls.DOMAIN
        ), "`DOMAIN` must be EntityV1 (`pyd.BaseModel` subclasses)."

    def __init__(
        self,
        id: str,
        entities: tp.Dict[str, pyd.BaseModel],
        status: str = "ALIVE",
    ):
        """
        Initialize the process.

        Parameters:
        -----------
        id: str
            The id of the process.
        entities: Dict[str, pyd.BaseModel]
            The entities of the process.
        """
        assert all(
            isinstance(tar, tuple(self.DOMAIN)) for tar in entities.values()
        ), "All entities must be instances of `DOMAIN`."
        self.ID = id
        self.entities = entities
        self.status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        assert (
            value in self.STATUS_SET
        ), f"Invalid assignment, `status` must be in {self.STATUS_SET}."
        self._status = value

    @abc.abstractmethod
    def run(self, step: int):
        """
        Process logic
        """
        ...
        raise NotImplementedError()
