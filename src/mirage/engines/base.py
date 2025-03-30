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
from ..monitors.loggers.engine_loggers import EngineV1Logger

#Implement more detailed and informative data visualization tools.

# ---ENGINEV1-------------------------------------------------------------------
# TODO[1]: pyd. validation for __init__ method of EngineV1 and derivatives.
# Currently, the validation is done only for name, state, processes, entities,
# speed, and history_persistence arguments inside EngineV1's __init__ method.
# This is because the annotations are lost amidst various wrapping procedures
# and pydantic can't validate them.
# TODO[2]: EngineV1 and it's derivates are only accepting positional arguments.
class EngineV1Meta(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        ret_validator = pyd.validate_call(
            config={"validate_return": True, "arbitrary_types_allowed": True}
        )
        if cls.__name__ != "EngineV1":
            assert hasattr(cls, "MAX_STEPS"), "`MAX_STEPS` must be defined"
            assert isinstance(cls.MAX_STEPS, int), "`MAX_STEPS` must be an int"
            assert cls.MAX_STEPS > 0, "`MAX_STEPS` must be greater than 0"
            oinit = cls.__init__

            def ninit(self, *args, **kwargs):
                oinit(self, *args, **kwargs)
                if EngineV1 in cls.__bases__:
                    EngineV1.__init__(self, *args[:7])

            cls.__init__ = ninit

            init_method = getattr(cls, "__init__", None)
            assert callable(
                init_method
            ), f"`{name}` class must implement an `__init__` method."
            init_vars = oinit.__code__.co_varnames
            for pm, ix in (
                ("name", 1),
                ("state", 2),
                ("processes", 3),
                ("entities", 4),
                ("speed", 5),
                ("history_persistence", 6),
                ("pr_stat_chart", 7),
            ):
                assert (
                    pm in init_vars
                ), f"`{name}` class must have a `{pm}` argument in `__init__`."
                assert (
                    init_vars.index(pm) == ix
                ), f"`{name}` class `{pm}` argument must be in position {ix}."
            # NOTE: Can't validate like this because annotations are lost
            # amidst various wrapping procedures.
            # TODO: Remove Manual Validation from EngineV1's __init__.
            # setattr(cls, "__init__", ret_validator(cls.__init__))

        return cls


class EngineV1(abc.ABC, metaclass=EngineV1Meta):
    """
    Base class for V1 type engines.

    Explanation:
    ------------
    - Constants:
        - `MAX_STEPS`: The maximum number of steps the engine can run.
        - `STATUS_SET`: The set of valid statuses for the engine.
    """

    MAX_STEPS: int
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}

    def __init__(
        self,
        name: str,
        state: EntityV1,
        processes: tp.List[ProcessV1],
        entities: tp.List[EntityV1],
        speed: int,
        history_persistence: int,
        pr_stat_chart: tp.Dict[str, tp.List[tp.List[int]]] | None,
    ):
        """
        Initialize the engine.

        Parameters:
        -----------
        name: str
            The name of the engine.
        state: EntityV1
            The state of the engine. Used to store metadata from processes,
            entities, and the engine itself.
        processes: List[ProcessV1]
            The processes of the engine.
        entities: List[EntityV1]
            The entities of the engine.
        speed: int
            The speed of the engine.
        """
        ### MANUAL VALIDATION ###
        assert isinstance(name, str), "`name` must be a `str`."
        assert isinstance(state, EntityV1), "`state` must be an `EntityV1`."
        assert isinstance(processes, list), "`processes` must be a `list`."
        assert all(
            isinstance(process, ProcessV1) for process in processes
        ), "`processes` must be a list of `ProcessV1` instances."
        assert len({process.id for process in processes}) == len(
            processes
        ), "All processes must have unique ids."
        assert isinstance(entities, list), "`entities` must be a `list`."
        assert all(
            isinstance(entity, EntityV1) for entity in entities
        ), "`entities` must be a list of `EntityV1` instances."
        assert isinstance(speed, int), "`speed` must be an `int`."
        assert speed >= 1, "`speed` must be greater than or equal to 1."
        assert isinstance(
            history_persistence, int
        ), "`history_persistence` must be an `int`."
        assert history_persistence >= 1, "`history_persistence` must be >= 1."
        ### Remove this after TODO[1] ###
        self.name = name
        self.state = state
        self.processes = processes
        self.entities = entities
        self.speed = speed
        self.history_persistence = history_persistence
        self.pr_stat_chart = pr_stat_chart or {}
        if not set(self.pr_stat_chart.keys()) <= {p.id for p in self.processes}:
            raise ValueError(
                "Processes in `pr_stat_chart` must be present in `processes`."
            )
        self.pr_stat_chart = {
            p.id: self.pr_stat_chart.get(
                p.id,
                (
                    [[0, self.MAX_STEPS]]
                    if p.status == "ALIVE"
                    else [[self.MAX_STEPS + 1, self.MAX_STEPS + 1]]
                ),
            )
            for p in self.processes
        }
        self.status = "DORMANT"
        self.STEP = 0
        self.info_history = {}
        self.run_call_history = []
        self.state_sync_mode = "RANK"
        self.L = EngineV1Logger(f"V1 | {self.__class__.__name__} | {self.name}")
        self.O = []  # Observers
        self.step_callbacks = []  # Step callback functions
        self.L.info(" >> 🚀 Initialized.")  # TODO: Printe 2x due to init wrap.

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

    def list_processes(self) -> tp.List[str]:
        """
        List the processes in the engine.

        Returns:
        --------
        List[str]
            The list of processes in the engine.
        """
        return [p.id for p in self.processes]

    def filter_pr_stat_chart(
        self, process_ids: str | tp.List[str] | None
    ) -> tp.Dict[str, tp.List[tp.List[int]]]:
        """
        Show the process status chart.

        Parameters:
        -----------
        process_ids: str | List[str] | None
            The process ids to show the status chart for. If None, show for all.

        Returns:
        --------
        Dict[str, List[List[int]]]
            The process status chart.
        """
        if process_ids is None:
            return self.pr_stat_chart
        if isinstance(process_ids, str):
            process_ids = [process_ids]
        if not set(process_ids) <= set(self.pr_stat_chart.keys()):
            raise ValueError("Some process ids not found.")
        return {pid: self.pr_stat_chart[pid] for pid in process_ids}

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
    @pyd.validate_call
    def set_to_intervals(s: tp.Set) -> tp.List[tp.List[int]]:
        """
        Convert a set of integers to a list of intervals.

        Parameters:
        -----------
        s: Set[int]
            The set of integers.

        Returns:
        --------
        List[List[int]]
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

    def insert_process(
        self,
        process: ProcessV1,
        intervals: tp.List[tp.List[int]] | tp.List[int] | tp.Set[int] | None,
    ):
        """
        Insert a process to the engine.

        Parameters:
        -----------
        process: ProcessV1
            The process to insert.
        """
        if process.id in {p.id for p in self.processes}:
            raise ValueError(f"ID {process.id} already in use.")
        if intervals is None:
            self.pr_stat_chart[process.id] = (
                [[self.STEP, self.MAX_STEPS]]
                if process.status == "ALIVE"
                else [[self.MAX_STEPS + 1, self.MAX_STEPS + 1]]
            )
        if intervals is not None:
            self.pr_stat_chart[process.id] = [
                [self.MAX_STEPS + 1, self.MAX_STEPS + 1],
            ]
            self.update_psc(process.id, intervals, "ALIVE")
        self.processes.append(process)
        self.L.info(f" >> 📝 Process registered | Process: {process.id}.")

    @pyd.validate_call
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
            *(set(ir(*interval)) for interval in self.pr_stat_chart[process_id])
        )
        return pr_stat_timeline

    @pyd.validate_call
    def update_psc(
        self,
        process_id: str,
        intervals: tp.List[tp.List[int]] | tp.List[int] | tp.Set[int],
        mode: str,
    ):
        """
        Update the process status chart.

        Parameters:
        -----------
        process_id: str
            The id of the process.
        intervals: List[List[int]] | List[int] | Set[int]
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
        pr_stat_timeline_intervals = EngineV1.set_to_intervals(pr_stat_timeline)
        self.pr_stat_chart[process_id] = pr_stat_timeline_intervals
        self.L.info(
            " >> 📝 PSC updated | Process: {}, Timeline: {}.".format(
                process_id, pr_stat_timeline_intervals
            )
        )

    def kill_process(self, process_id: str):
        """
        Kill a process.

        Parameters:
        -----------
        process_id: str
            The id of the process to kill.
        """
        try:
            process = next(p for p in self.processes if p.id == process_id)
        except StopIteration:
            raise ValueError(f"Process {process_id} not found.")
        process.status = "DEAD"
        self.L.info(f" >> 💀 Process killed | Process: {process_id}.")

    def clear_history(self):
        """
        Clear the running history of the engine.
        """
        self.info_history.clear()
        self.run_call_history.clear()

    def register_step_callback(self, callback: tp.Callable[[], None]):
        """
        Register a callback function to be called after each step.
        
        Parameters:
        -----------
        callback: Callable[[], None]
            A callback function to be called after each step.
        """
        if not callable(callback):
            raise TypeError("Callback must be callable.")
        self.step_callbacks.append(callback)

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
        unique_ranks = sorted(set(p.RANK for p in schedule))
        current_rank = unique_ranks.pop(0)

        for process in schedule:
            pst = self.get_pr_stat_timeline(process.id)
            if process.status != "DEAD":
                process.status = "ALIVE" if step in pst else "DORMANT"

            if process.RANK != current_rank:
                for entity in self.entities:
                    entity.sync()
                if self.state_sync_mode == "RANK":
                    self.state.sync()
                current_rank = unique_ranks.pop(0)

            info = process.run(step)
            if info is not None:
                self.info_history[f"{process.id}/{step}"] = info

        for entity in self.entities:
            entity.sync()
        self.state.sync()
        for observer in self.O:
            observer.observe()
        self.prune_processes()
        
        # Execute step callbacks
        for callback in self.step_callbacks:
            callback()

    def fire(self, num_steps: int = None, time_limit: int = None):
        """
        Fire the engine.

        Parameters:
        -----------
        num_steps: int
            The number of steps to run the engine.
        time_limit: int
            The time limit to run the engine (in minutes).
        """
        if num_steps and not time_limit:
            if not self.MAX_STEPS >= num_steps >= 1:
                raise ValueError(f"`num_steps` not <= {self.MAX_STEPS}.")
        elif time_limit and not num_steps:
            num_steps = self.speed * time_limit
        else:
            raise ValueError("Use `num_steps` or `time_limit`.")
        num_steps = int(num_steps)

        self.L.info(f" >> 🔥 Firing...")
        self.play()

        def orchestration_loop():
            pT = time.time()
            while self.status != "DEAD" and self.STEP <= num_steps:
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
                if self.STEP % self.history_persistence == 0:
                    self.clear_history()
            self.clear_history()
            self.stop()

        orch_loop_thread = threading.Thread(target=orchestration_loop)
        orch_loop_thread.start()

        return orch_loop_thread

    def pause(self):
        """
        Pause the engine.
        """
        self.L.info(" >> ⏸️ Pausing...")
        self.status = "DORMANT"

    def play(self):
        """
        Play the engine.
        """
        self.L.info(" >> ▶️ Playing...")
        self.status = "ALIVE"

    def stop(self):
        """
        Stop the engine.
        """
        self.L.info(" >> ⏹️ Stopping...")
        self.status = "DEAD"
