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
class ProcessV1Meta(abc.ABCMeta):
    """
    Metaclass for `ProcessV1` type.

    Explanation:
    ------------
    - Validations:
        - `RANK` must be an `int` or `None`.
        - `DOMAIN` must be EntityV1 (`pyd.BaseModel` subclasses).
        - `while_alive` method must be implemented.
        - `while_alive` method must have a `step` argument.
        - `id`, `entities`, and `status` arguments must be in `__init__`.
        - `id`, `entities`, and `status` arguments must be in the right order.
    - Initialization:
        - Calls the `ProcessV1` initialization method.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        if cls.__name__ != "ProcessV1":
            required_attrs = {
                "RANK": (
                    lambda x: isinstance(x, int) or x is None,
                    "`RANK` must be an `int` or `None`.",
                ),
                "DOMAIN": (
                    lambda x: all(issubclass(dm, EntityV1) for dm in x),
                    "`DOMAIN` must be EntityV1 subclasses.",
                ),
            }
            for attr, (validator, error_msg) in required_attrs.items():
                assert hasattr(cls, attr) and validator(
                    getattr(cls, attr)
                ), f"`{name}` {error_msg}"
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
        for param, index in (("id", 1), ("entities", 2), ("status", 3)):
            assert (
                param in init_vars
            ), f"`{name}` class must have a `{param}` argument in `__init__`."
            assert (
                init_vars.index(param) == index
            ), f"`{name}` class `{param}` argument must be in position {index}."

        ret_validator = pyd.validate_call(
            config={"validate_return": True, "arbitrary_types_allowed": True}
        )
        for m in ("while_alive", "while_dormant"):
            method = getattr(cls, m)
            method.__annotations__["return"] = tp.Dict[str, int | float]
            method.__annotations__["step"] = int
            setattr(cls, m, ret_validator(method))
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
        assert all(
            isinstance(ent, self.DOMAIN) for ent in entities.values()
        ), f"All entities must be instances of `DOMAIN` {self.DOMAIN}."
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
    def while_alive(self, step: int) -> tp.Dict[str, int | float]:
        """
        Logic while the process is `ALIVE`. Returns a dictionary of intermediate
        results as dictionary of `str` keys and `int` or `float` values.
        """
        raise NotImplementedError

    def while_dormant(self, step: int) -> tp.Dict[str, int | float]:
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
            l = self.while_alive(step)
        elif self.status == "DORMANT":
            l = self.while_dormant(step)
        else:
            pass
        info = {f"{self.id}/{self.status}/{k}/{step}": v for k, v in l.items()}
        return info
