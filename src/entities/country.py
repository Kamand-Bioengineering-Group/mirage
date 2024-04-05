# ---DEPENDENCIES---------------------------------------------------------------
from .base import EntityV1

# ---COUNTRY--------------------------------------------------------------------
class Country(EntityV1):
    def __init__(
        self,
        name: str,
        beta: float,
        gamma: float,
        epsilon: float,
        birth_ratio: float,
        death_ratio: float,
        loci: list,
    ):
        super().__init__()
        self.name = name
        self.beta = beta
        self.gamma = gamma
        self.epsilon = epsilon
        self.birth_ratio = birth_ratio
        self.death_ratio = death_ratio
        self.loci = loci

    def __str__(self):
        ...

