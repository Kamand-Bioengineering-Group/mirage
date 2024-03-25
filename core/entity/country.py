# ---DEPENDENCIES---------------------------------------------------------------	
from . base import BaseEntity

# ---COUNTRY---------------------------------------------------------------------
class Country(BaseEntity):
    """
    A class to represent a country.

    Attributes
    ----------
    name : str
        the name of the country
    population : dict
        the population of the country, with the keys 'S', 'I', 'R', 'D' 
        representing the number of susceptible, infected, recovered, and 
        deceased individuals, respectively

    Methods
    -------
    S
        returns the number of susceptible individuals
    I
        returns the number of infected individuals
    R
        returns the number of recovered individuals
    D
        returns the number of deceased individuals
    """	
    def __init__(
        self,
        name: str,
        population: dict,
        resources: dict, 
    ):
        super().__init__()
        self.name = name
        self.population = population
        self.resources = resources

    @property
    def S(self):
        return self.population['S']
    
    @property
    def I(self):
        return self.population['I']
    
    @property
    def R(self):
        return self.population['R']
    
    @property
    def D(self):
        return self.population['D']


    
    