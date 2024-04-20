# ---INFO-----------------------------------------------------------------------
"""
Base classes for Processes. Processes change the state of the entities in a \
simulation.
"""

# TODO: feature: V2 type processes can modify processes and entities.


__all__ = [
    "ProcessV1",
]


# ---DEPENDENCIES---------------------------------------------------------------
import abc
import typing as tp
import pydantic as pyd

from ..entities import EntityV1


# ---PROCESSV1------------------------------------------------------------------
# TODO[1]: pyd. validation for __init__ method of ProcessV1 and derivatives.
# Currently, the validation is done only for id, entities, and status arguments.
# inside ProcessV1's __init__ method. This is because the annotations are lost
# amidst various wrapping procedures and pydantic can't validate them.
class ProcessV1Meta(abc.ABCMeta):
    """
    Metaclass for `ProcessV1` type.

    Explanation:
    ------------
    - Validations:
        - `RANK` must be an `int` or `None`.
        - `DOMAIN` must be EntityV1 subclasses.
        - `while_alive` method must be implemented.
        - `while_alive` method must have a `step` argument.
        - `id`, `entities`, and `status` arguments must be in `__init__`.
        - `id`, `entities`, and `status` arguments must be in the right order.
    - Initialization:
        - Calls the `ProcessV1` initialization method.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        ret_validator = pyd.validate_call(
            config={"validate_return": True, "arbitrary_types_allowed": True}
        )
        if cls.__name__ != "ProcessV1":
            assert "RANK" in namespace, f"`{name}` class must have a `RANK`."
            assert (
                isinstance(namespace["RANK"], int) or namespace["RANK"] is None
            ), f"`{name}` class `RANK` must be an `int` or `None`."
            assert "DOMAIN" in namespace, f"`{name}` class must have `DOMAIN`."
            assert isinstance(namespace["DOMAIN"], tuple) and all(
                issubclass(ent, EntityV1) for ent in namespace["DOMAIN"]
            ), f"`{name}` class `DOMAIN` must be tuple of EntityV1 subclasses."
            # NOTE: This could be done in __init__ of this metaclass, but it
            # I couldn't access co_varnames of original __init__ method. This
            # implementation solves it.
            # TODO: Find a better way to do this.
            oinit = cls.__init__

            def ninit(self, *args, **kwargs):
                oinit(self, *args, **kwargs)
                if ProcessV1 in cls.__bases__:
                    ProcessV1.__init__(self, *args[:3])

            cls.__init__ = ninit
            while_alive_method = getattr(cls, "while_alive", None)
            assert callable(
                while_alive_method
            ), f"`{name}` class must implement a `while_alive` method."
            assert (
                "step" in while_alive_method.__code__.co_varnames
            ), "`while_alive` method must have a `step` argument."
            while_dormant_method = getattr(cls, "while_dormant", None)
            assert callable(
                while_dormant_method
            ), f"`{name}` class must implement a `while_dormant` method."
            assert (
                "step" in while_dormant_method.__code__.co_varnames
            ), "`while_dormant` method must have a `step` argument."

            init_method = getattr(cls, "__init__", None)
            assert callable(
                init_method
            ), f"`{name}` class must implement an `__init__` method."
            init_vars = oinit.__code__.co_varnames
            for pm, ix in (("id", 1), ("entities", 2), ("status", 3)):
                assert (
                    pm in init_vars
                ), f"`{name}` class must have a `{pm}` argument in `__init__`."
                assert (
                    init_vars.index(pm) == ix
                ), f"`{name}` class `{pm}` argument must be at pos {ix}."
            # NOTE: Can't validate like this because annotations are lost
            # amidst various wrapping procedures.
            # TODO: Remove Manual Validation from ProcessV1's __init__.
            # setattr(cls, "__init__", ret_validator(cls.__init__))
            for m_name in ("while_alive", "while_dormant"):
                m = getattr(cls, m_name)
                m.__annotations__["return"] = tp.Dict[str, int | float] | None
                m.__annotations__["step"] = int | None
                setattr(cls, m_name, ret_validator(m))

        return cls


class ProcessV1(abc.ABC, metaclass=ProcessV1Meta):
    """
    ProcessV1 type. Processes change the state of the entities in a simulation.

    Attributes:
    -----------
    RANK: int
        The rank of the process. Processes with higher ranks are run first.
    DOMAIN: Tuple[EntityV1]
        The types of entities that the process can target.
    """

    RANK: int
    DOMAIN: tp.Tuple[EntityV1]
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}

    def __init__(
        self,
        id: str,
        entities: tp.Dict[str, EntityV1],
        status: str,
    ):
        """
        Instantiate a `ProcessV1` object.

        Parameters:
        -----------
        id: str
            The id of the process.
        entities: Dict[str, EntityV1]
            The entities of the process.
        status: str
            The status of the process.
        """
        ### MANUAL VALIDATION ###
        assert isinstance(id, str), "`id` must be a `str`."
        assert isinstance(entities, dict), "`entities` must be a `dict`."
        assert all(
            isinstance(ent, self.DOMAIN) for ent in entities.values()
        ), f"All entities must be instances of `DOMAIN` {self.DOMAIN}."
        assert isinstance(status, str), "`status` must be a `str`."
        ### Remove this after TODO[1] ###
        self.id = id
        self.entities = entities
        self.status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        """
        Prevents invalid assignment to `status`.
        """
        assert (
            value in self.STATUS_SET
        ), f"Invalid assignment, `status` must be in {self.STATUS_SET}."
        self._status = value

    @abc.abstractmethod
    def while_alive(self, step: int) -> tp.Dict[str, int | float] | None:
        """
        Logic while the process is `ALIVE`. Returns a dictionary of intermediate
        results as dictionary of `str` keys and `int` or `float` values.
        """
        raise NotImplementedError

    def while_dormant(self, step: int) -> tp.Dict[str, int | float] | None:
        """
        Logic while the process is `DORMANT`. Returns a dictionary of
        intermediate results as dictionary of `str` keys and `int` or `float`
        """
        pass

    def condition_status(self) -> None:
        """
        Sets the status of the process based on the conditions. If no conditions
        are being implemented, the method returns `None`. This will override the
        status set by the `pr_stat_chart` in the engine.
        """
        ...

    def run(self, step: int):
        """
        Run the process. Returns a dictionary of intermediate results as
        dictionary of `str` keys and `int` or `float` values.
        """
        self.condition_status()
        if self.status == "ALIVE":
            status_data = self.while_alive(step)
        elif self.status == "DORMANT":
            status_data = self.while_dormant(step)
        else:
            status_data = None
        info = (
            {f"{self.status}/{k}": v for k, v in status_data.items()}
            if status_data is not None
            else None
        )
        return info
