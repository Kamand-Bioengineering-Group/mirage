# ---INFO-----------------------------------------------------------------------
"""
Base classes for Processes. Processes change the state of the entities in a \
simulation.
"""

__all__ = ["ProcessV1"]


# ---DEPENDENCIES---------------------------------------------------------------
import abc


# ---PROCESSV1------------------------------------------------------------------
class ProcessV1(abc.ABC):
    """
    Base class for V1 type processes.

    Attributes:
        RANK (int | None): Process RANK.

    Methods:
        run(): Process logic.
    """

    RANK: int | None = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert hasattr(cls, "RANK"), "Processes must have a `RANK`."
        assert isinstance(
            cls.RANK, int | None
        ), "`RANK` must be an `int` or `None`."

    @abc.abstractmethod
    def run(self):
        """
        Process logic.
        """
        ...
        raise NotImplementedError()
