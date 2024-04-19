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
        self.peripheral_processes = {}

    def register_peripheral_processes(
        self,
        peripheral_processes_config: tp.Dict[
            str, tp.Tuple[str, tp.Dict[str, EntityV1], tp.Type[ProcessV1]]
        ],
    ):
        """
        Register peripheral processes.

        Parameters:
        ----------
            - peripheral_processes_config: A dictionary of peripheral processes.
                The key is the alias of the process, and the value is a tuple
                of the default process status, the entities and the process type
                involved in the process.
        """
        f = all(
            issubclass(process_type[0], ProcessV1)
            for process_type in peripheral_processes_config.values()
        )
        if not f:
            raise TypeError(
                "All peripheral processes must be instances of `ProcessV1`."
            )
        self.peripheral_processes_config = peripheral_processes_config

    def spawn_peripheral_process(
        self,
        alias: str,
        id: str,
        intervals: tp.List[tp.List[int]] | tp.List[int] | tp.Set[int] | None,
        **process_kwargs,
    ):
        """
        Spawn a peripheral process.
        """
        if alias not in self.peripheral_processes:
            raise ValueError(f"Peripheral process `{alias}` not found.")
        # check unique id
        if any(p.id == id for p in self.processes):
            raise ValueError(f"Process id {id} already exists.")
        sign = self.peripheral_processes[alias]
        process = sign[0](id, sign[1], sign[2], **process_kwargs)
        self.insert_process(process, intervals)


class FireflyV1State(EntityV1):
    baba_black_sheep: str
