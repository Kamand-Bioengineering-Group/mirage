from texttable import Texttable
from .base import BaseEntity


# ---COUNTRY--------------------------------------------------------------------
class Country(BaseEntity):
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
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_dtype(["t", "f", "f", "f", "f", "f"])
        table.set_cols_align(["l", "r", "r", "r", "r", "r"])
        table.add_row(
            ["Name", "Beta", "Gamma", "Epsilon", "Birth Ratio", "Death Ratio"]
        )
        table.add_row(
            [
                self.name,
                self.beta,
                self.gamma,
                self.epsilon,
                self.birth_ratio,
                self.death_ratio,
            ]
        )

        loci_info = "\n".join(
            [
                f"    - {locus['name']} (Lat: {locus['lat']}, Lon: {locus['lon']}, Population: {locus['population']})"
                for locus in self.loci
            ]
        )

        return f"{table.draw()}\n\nLocis:\n{loci_info}"
