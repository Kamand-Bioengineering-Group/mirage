# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import pydantic as pyd

# ---COUNTRY--------------------------------------------------------------------
class Locus(pyd.BaseModel):
    name: str
    latitude: float
    longitude: float
    population: int
    airports: tp.Dict[str, int]
    ports: tp.Dict[str, int]
    hospitals: tp.Dict[str, int]
    loc_resources: tp.Dict[str, tp.Dict[str, float | int]]

class Country(pyd.BaseModel):
    name: str
    beta: float
    gamma: float
    epsilon: float
    birth_rate: float
    death_rate: float
    gdp: int
    cen_resources: tp.Dict[str, tp.Dict[str, float | int]]
    loci: tp.Dict[str, Locus]

