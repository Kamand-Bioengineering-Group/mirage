# ---INFO-----------------------------------------------------------------------

"""
Module for base engines.
"""

__all__ = [
    "EngineV1",
]


# ---DEPENDENCIES---------------------------------------------------------------
import time
import typing as tp
import abc
import threading
import pydantic as pyd

from ..entities.base import EntityV1
from ..processes.base import ProcessV1


# ---ENGINEV1-------------------------------------------------------------------
class EngineV1Meta(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        if cls.__name__ != "EngineV1":
            assert hasattr(cls, "MAX_STEPS"), "`MAX_STEPS` must be defined"
            assert isinstance(cls.MAX_STEPS, int), "`MAX_STEPS` must be an int"
            assert cls.MAX_STEPS > 0, "`MAX_STEPS` must be greater than 0"
            assert "while_alive" in cls.__dict__ and callable(
                cls.while_alive
            ), f"`{name}` class must implement a `while_alive` method."
            assert (
                "step" in cls.__dict__["while_alive"].__code__.co_varnames
            ), "`while_alive` method must have a `step` argument."
            assert (
                "step" in cls.__dict__["while_dormant"].__code__.co_varnames
            ), "`while_dormant` method must have a `step` argument."

        init_vars = cls.__dict__["__init__"].__code__.co_varnames
        for param, index in (
            ("name", 1),
            ("state", 2),
            ("processes", 3),
            ("entities", 4),
            ("speed", 5),
            ("history_persistence", 6),
        ):
            assert (
                param in init_vars
            ), f"`{name}` class must have a `{param}` argument in `__init__`."
            assert (
                init_vars.index(param) == index
            ), f"`{name}` class `{param}` argument must be in position {index}."

        ret_validator = pyd.validate_call(
            config={"validate_return": True, "allow_arbitrary_types": True}
        )
        setattr(cls, "__init__", ret_validator(cls.__init__))

        return cls

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        oinit = cls.__init__

        def ninit(self, *args, **kwargs):
            oinit(self, *args, **kwargs)
            if ProcessV1 in cls.__bases__:
                ProcessV1.__init__(self, *args[:3])

        cls.__init__ = ninit


class EngineV1(abc.ABC, metaclass=EngineV1Meta):
    """
    Base class for V1 type engines.

    Explanation:
    ------------
    - Constants:
        - `MAX_STEPS`: The maximum number of steps the engine can run.
        - `STATUS_SET`: The set of valid statuses for the engine.
    """

    MAX_STEPS = 72000
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}

    @pyd.validate_call(config={"arbitrary_types_allowed": True})
    def __init__(
        self,
        name: str,
        state: EntityV1,
        processes: tp.List[ProcessV1],
        entities: tp.List[EntityV1],
        speed: int = 6,
        history_persistence: int = 12,
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
        self.name = name
        self.state = state
        self.processes = processes
        self.entities = entities
        self.speed = speed
        self.history_persistence = history_persistence
        self.status = "DORMANT"
        self.pr_stat_chart = {
            p.id: [[0, self.MAX_STEPS]] for p in self.processes
        }
        self.info_history = {}
        self.STEP = 0
        self.run_call_history = []
        self.state_sync_mode = "RANK"

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
    def state_sync_mode(self):
        return self._state_sync_mode

    @state_sync_mode.setter
    def state_sync_mode(self, value: str):
        assert value in {"RANK", "STEP"}, f"Invalid state sync mode: {value}"
        self._state_sync_mode = value

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

    @staticmethod
    def irange(start: int, stop: int, step: int = 1) -> range:
        """
        Inclusive variant of the `range` function.
        """
        return range(start, stop + 1, step)

    @staticmethod
    def set_to_intervals(s) -> tp.List[tp.List[int, int]]:
        """
        Convert a set of integers to a list of intervals.

        Parameters:
        -----------
        s: Set[int]
            The set of integers.

        Returns:
        --------
        List[List[int, int]]
            The list of intervals.
        """
        s = sorted(s)
        intervals = []
        start = s[0]
        for i in range(1, len(s)):
            if s[i] - s[i - 1] > 1:
                intervals.append([start, s[i - 1]])
                start = s[i]
        intervals.append([start, s[-1]])
        return intervals

    def get_pr_stat_timeline(self, process_id: str) -> tp.Set[int]:
        """
        Get the process status timeline. The timeline is a set of integers where
        each integer represents an 'ALIVE' step.

        Parameters:
        -----------
        process_id: str
            The id of the process.

        Returns:
        --------
        Set[int]
            The process status timeline.
        """
        ir = EngineV1.irange
        pr_stat_timeline = set().union(
            *(
                set(ir(*interval))
                for interval in self.pr_stat_chart[process_id]
            )
        )
        return pr_stat_timeline

    @pyd.validate_call
    def update_psc(
        self,
        process_id: str,
        intervals: (
            tp.List[tp.List[int, int]] | tp.List[int, int] | tp.Set[int]
        ),
        mode: str,
    ):
        """
        Update the process status chart.

        Parameters:
        -----------
        process_id: str
            The id of the process.
        intervals: List[List[int, int]] | List[int, int] | Set[int]
            The intervals to update.
        mode: str
            The mode of the update.
        """
        assert mode in {"ALIVE", "DORMANT"}, f"Invalid mode: {mode}"
        ir = EngineV1.irange
        pr_stat_timeline = self.get_pr_stat_timeline(process_id)
        if isinstance(intervals, list) and all(
            isinstance(interval, list) for interval in intervals
        ):
            for interval in intervals:
                if mode == "ALIVE":
                    pr_stat_timeline |= set(ir(*interval))
                elif mode == "DORMANT":
                    pr_stat_timeline -= set(ir(*interval))
        elif isinstance(intervals, list):
            if mode == "ALIVE":
                pr_stat_timeline |= set(ir(*intervals))
            elif mode == "DORMANT":
                pr_stat_timeline -= set(ir(*intervals))
        elif isinstance(intervals, set):
            if mode == "ALIVE":
                pr_stat_timeline |= intervals
            elif mode == "DORMANT":
                pr_stat_timeline -= intervals
        pr_stat_timeline_intervals = EngineV1.set_to_intervals(
            pr_stat_timeline
        )
        self.pr_stat_chart[process_id] = pr_stat_timeline_intervals

    def clear_history(self):
        """
        Clear the running history of the engine.
        """
        self.info_history.clear()
        self.run_call_history.clear()

    @pyd.validate_call
    def run(self, step: int):
        """
        Run the engine for a given step.

        Explanation:
        ------------
        - Run the processes in the schedule.
        - Set the status of the processes based on Timeline.
        - Override the status of the processes based on conditions. This is done
            by calling the `condition_status` method of the process inside it's
            `run` method. Processes do this on their own.
        - The engine prunes dead processes.
        - The engine synchronizes the entities.

        Parameters:
        -----------
        step: int
            The step to run the engine.
        """
        schedule = self.get_schedule()
        unique_ranks = set(p.RANK for p in schedule)
        current_rank = unique_ranks.pop()

        for process in schedule:
            pst = self.get_pr_stat_timeline(process.id)
            process.status = "ALIVE" if step in pst else "DORMANT"
            if process.RANK == current_rank:
                info = process.run(step)
            else:
                current_rank = unique_ranks.pop()
                for entity in self.entities:
                    entity.sync()
                self.state.sync() if self.state_sync_mode == "RANK" else None
                info = process.run(step)
            self.info_history[f"{step}"] = info
        self.state.sync() if self.state_sync_mode == "STEP" else None
        self.prune_processes()

    def fire(self):
        """
        Fire the engine.
        """
        print(f">> Starting Engine {self.__class__.__name__} {self.name}.")

        def simulation_loop():
            pT = time.time()
            while self.status != "DEAD":
                if self.status == "ALIVE":
                    nT = time.time()
                    if nT - pT >= 60 / self.speed:
                        pT = nT
                        self.run_call_history.append(pT)
                        self.run(self.STEP)
                        self.STEP += 1
                    else:
                        dT = 60 / self.speed - (nT - pT)
                        time.sleep(dT)
                        pT = nT + dT
                        self.run_call_history.append(pT)
                        self.run(self.STEP)
                        self.STEP += 1
                elif self.status == "DORMANT":
                    pass
                else:
                    pass
                if self.STEP >= self.MAX_STEPS:
                    self.status = "DEAD"
                if self.STEP % self.history_persistence == 0:
                    self.clear_history()
            print(f">> Stopping Engine {self.__class__.__name__} {self.name}.")
            self.clear_history()

        sim_loop_thread = threading.Thread(target=simulation_loop)
        sim_loop_thread.start()

        return sim_loop_thread

    def pause(self):
        """
        Pause the engine.
        """
        self.status = "DORMANT"

    def play(self):
        """
        Play the engine.
        """
        self.status = "ALIVE"

    def stop(self):
        """
        Stop the engine.
        """
        self.status = "DEAD"
