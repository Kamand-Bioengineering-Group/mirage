# ---INFO-----------------------------------------------------------------------
"""
Firefly engine.
"""

__all__ = [
    "FireflyV1",
    "FireflyV1State",
]


# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
from .base import EngineV1
from ..entities.base import EntityV1
from ..processes.base import ProcessV1


# ---FIREFLY--------------------------------------------------------------------
class FireflyV1(EngineV1):
    """
    Firefly engine.
    """

    MAX_STEPS = 365 * 20

    def __init__(
        self,
        name: str,
        state: EntityV1,
        processes: tp.List[ProcessV1],
        entities: tp.List[EntityV1],
        speed: int,
        history_persistence: int,
        pr_stat_chart: tp.Dict[str, tp.List[tp.List[int]]] | None,
        baba_black_sheep: str,
    ):
        self.baba_black_sheep = baba_black_sheep


class FireflyV1State(EntityV1):
    baba_black_sheep: str
