import numpy as np
from scipy.special import expit
from . import geo_political_entities
from .constants import *
from ...processes.base import ProcessV1


def truncated_sigmoid(x, min_val, max_val):
    sigmoid_x = expit(x)
    scaled_sigmoid_x = min_val + (sigmoid_x * (max_val - min_val))
    return scaled_sigmoid_x


############################################################################################################
class BirthProcess(ProcessV1):
    """_summary_
    Birth process that models the birth rate of a country based on the economic prosperity of the country
    and the population of the country.

    _user_input_
    NONE

    _internal_
        - alpha: float
        The weight of the susceptible population in the birth rate calculation.
    - beta: float
        The weight of the recovered population in the birth rate calculation.
    - gamma: float
        The weight of the infected population in the birth rate calculation.
    - max_birth_rate: float
        The maximum birth rate that can be achieved in a country.
    - economic_prosperity_THRESH: float
        The economic prosperity threshold that determines the birth rate of a country.

    _process_
    - Updates value of locus.A birth rate for all the locus
    """

    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        alpha=0.5,
        beta=0.3,
        gamma=0.2,
        max_birth_rate=0.15,
        economic_prosperity_THRESH=0.5,
    ):
        # super().__init__(id, entities, status)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_birth_rate = max_birth_rate
        self.economic_prosperity_THRESH = economic_prosperity_THRESH

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        birth_rates = {}
        for country in self.entities:

            economic_prosperity = self.entities[country].human_welfare_resource

            for i, locus in enumerate(self.entities[country].loci):

                living_population_contribution = (
                    self.alpha * (locus.susceptible)
                    + self.beta * (locus.recovered)
                    + self.gamma * (locus.infected)
                ) / max_living_population

                if (economic_prosperity < self.economic_prosperity_THRESH) and (
                    economic_prosperity > base_birth_rate
                ):
                    birth_rate = (
                        (
                            self.alpha * (locus.susceptible)
                            + self.beta * (locus.recovered)
                            + self.gamma * (locus.infected)
                        )
                        * economic_prosperity
                        / max_living_population
                    )
                    if locus.A + birth_rate <= self.max_birth_rate:
                        locus.A += birth_rate
                    else:
                        locus.A = self.max_birth_rate

                elif economic_prosperity >= self.economic_prosperity_THRESH:
                    economic_prosperity_use = living_population_contribution * (
                        1 - (min_human_welfare_resource / economic_prosperity)
                    )
                    birth_rate = (
                        (2 / (1 + np.exp(-economic_prosperity_use))) - 1
                    ) * self.max_birth_rate

                    if locus.A + birth_rate <= self.max_birth_rate:
                        self.entities[country].loci[i].A += birth_rate
                    else:
                        locus.A = self.max_birth_rate
                elif economic_prosperity <= base_birth_rate:
                    birth_rate = base_birth_rate
                    if locus.A + birth_rate <= max_birth_rate:
                        locus.A += birth_rate
                    else:
                        locus.A = max_birth_rate

        ####### Keep if want to debug #######
        # return {
        #     "MaskImplementationProcess"
        #     + "_"
        #     + str(locus.name)
        #     + "_"
        #     + str(country): locus.A
        #     for locus in self.entities[country].loci
        # }


############################################################################################################


class MaskImplementationProcess(ProcessV1):

    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        effect: list,
        health_resource_cost=5,
        sanitation_equipment_cost=5,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):
        # super().__init__(id, entities, status)
        self.health_resource_cost = health_resource_cost
        self.sanitation_equipment_cost = sanitation_equipment_cost
        self.state = state
        self.effect = effect
        self.country = country
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        # print("STEP: ", step)
        for i, country in enumerate(self.country):
            # print("COUNTRY: ", country, i)
            health_resource = self.entities[country].health_resource_stockpile
            sanitation_equipment = self.entities[country].sanitation_equipment_stockpile

            for locus in self.entities[country].loci:
                if locus.name == self.state[i]:
                    # print("Yes", locus.name, self.state, self.effect[i])
                    if (
                        health_resource >= self.health_resource_cost * self.effect[i]
                        and sanitation_equipment
                        >= self.sanitation_equipment_cost * self.effect[i]
                    ):
                        # print("ENOUNG RESOURCES", health_resource, sanitation_equipment, self.health_resource_cost * self.effect[i], self.sanitation_equipment_cost * self.effect[i])
                        if (
                            self.entities[country].health_resource_stockpile
                            - self.health_resource_cost * self.effect[i]
                            <= 0
                        ):
                            self.entities[country].health_resource_stockpile = 0
                        else:
                            self.entities[country].health_resource_stockpile -= (
                                self.health_resource_cost * self.effect[i]
                            )
                        if (
                            self.entities[country].sanitation_equipment_stockpile
                            - self.sanitation_equipment_cost * self.effect[i]
                            <= 0
                        ):
                            self.entities[country].sanitation_equipment_stockpile = 0
                        else:
                            self.entities[country].sanitation_equipment_stockpile -= (
                                self.sanitation_equipment_cost * self.effect[i]
                            )

                        # print(locus.B, "LOCUS B")
                        if (
                            locus.B
                            - truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                            >= 1e-7
                        ):
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) / max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                        else:
                            # print("Sigmoid missed")
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= 0.02 * locus.B * self.effect[i]
                    else:
                        # print("Insuff RES")
                        locus.B -= 0.000002 * locus.B
                else:
                    pass

        # return {
        #     "MaskImplementation"
        #     + "_"
        #     + str(locus.name)
        #     + "_"
        #     + str(country): locus.B
        #     for locus in self.entities[country].loci
        # }


# Make AidKitImplementationProcess class similar to the above processes structure
class AidKitImplementationProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        effect: list,
        health_resource_cost=100,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):

        # super().__init__(id, entities, status)
        self.state = state
        self.health_resource_cost = health_resource_cost
        self.country = country
        self.state = state
        self.effect = effect
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        # print("STEP: ", step)
        for i, country in enumerate(self.country):
            # print("COUNTRY: ", country, i)
            health_resource = self.entities[country].health_resource_stockpile

            for locus in self.entities[country].loci:
                if locus.name == self.state[i]:
                    # print("Yes", locus.name, self.state, self.effect[i])
                    if health_resource >= self.health_resource_cost * self.effect[i]:
                        # print("ENOUNG RESOURCES", health_resource, sanitation_equipment, self.healt)
                        if (
                            self.entities[country].health_resource_stockpile
                            - self.health_resource_cost * self.effect[i]
                            <= 0
                        ):
                            self.entities[country].health_resource_stockpile = 0
                        else:
                            self.entities[country].health_resource_stockpile -= (
                                self.health_resource_cost * self.effect[i]
                            )

                        # print(locus.B, "LOCUS B")
                        if (
                            locus.B
                            - truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                            >= 1e-7
                        ):
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) / max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                        else:
                            # print("Sigmoid missed")
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= 0

                        # print(locus.name, locus.B, "LOCUS B")
                        # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")

                    else:
                        # print("Insuff RES")
                        locus.B -= 0
                else:
                    pass
        # return {
        #     "AidKitImplementationProcess"
        #     + "_"
        #     + str(locus.name)
        #     + "_"
        #     + str(country): locus.B
        #     for locus in self.entities[country].loci
        # }


class General_Sanitation_Implementation(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        effect: list,
        sanitation_resource_cost=200,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):

        # super().__init__(id, entities, status)
        self.state = state
        self.sanitation_resource_cost = sanitation_resource_cost
        self.country = country
        self.state = state
        self.effect = effect
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        # print("STEP: ", step)
        for i, country in enumerate(self.country):
            # print("COUNTRY: ", country, i)
            health_resource = self.entities[country].sanitation_equipment_stockpile

            for locus in self.entities[country].loci:
                if locus.name == self.state[i]:
                    # print("Yes", locus.name, self.state, self.effect[i])
                    if health_resource >= self.sanitation_resource_cost * self.effect[
                        i
                    ] * (locus.susceptible + locus.infected + locus.recovered) / (
                        locus.area * max_living_population
                    ):
                        # print("ENOUNG RESOURCES", health_resource, sanitation_equipment, self.healt)
                        if (
                            self.entities[country].health_resource_stockpile
                            - self.sanitation_resource_cost
                            * self.effect[i]
                            * (locus.susceptible + locus.infected + locus.recovered)
                            / (locus.area * max_living_population)
                            <= 0
                        ):
                            self.entities[country].health_resource_stockpile = 0
                        else:
                            self.entities[country].health_resource_stockpile -= (
                                self.sanitation_resource_cost
                                * self.effect[i]
                                * (locus.susceptible + locus.infected + locus.recovered)
                                / (locus.area * max_living_population)
                            )

                        # print(locus.B, "LOCUS B")
                        if (
                            locus.B
                            - truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible + locus.recovered)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                            >= 1e-7
                        ):
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) / max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= truncated_sigmoid(
                                locus.B
                                * self.effect[i]
                                * (locus.infected + locus.susceptible + locus.recovered)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                        else:
                            # print("Sigmoid missed")
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")
                            locus.B -= 0

                        # print(locus.name, locus.B, "LOCUS B")
                        # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value), "TRUNCATED SIGMOID")

                    else:
                        # print("Insuff RES")
                        locus.B -= 0
                else:
                    pass
        # return {
        #     "GeneralSanitationImplementation"
        #     + "_"
        #     + str(locus.name)
        #     + "_"
        #     + str(country): locus.B
        #     for locus in self.entities[country].loci
        # }


class QuarantineFacilitiesQProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        num_centers: list,
        gdp_cost_per_center=500,
        health_resource_cost=50,
        sanitation_equipment_cost=100,
        trunk_min_value=1e-6,
        trunk_max_value=5e-5,
    ):

        # super().__init__(id, entities, status)
        self.gdp_cost_per_center = gdp_cost_per_center
        self.health_resource_cost = health_resource_cost
        self.sanitation_equipment_cost = sanitation_equipment_cost
        self.num_centers = num_centers
        self.state = state
        self.country = country
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        # print("STEP: ", step)
        for i, country in enumerate(self.country):
            # print("COUNTRY: ", country, i)
            health_resource = self.entities[country].health_resource_stockpile
            sanitation_equipment = self.entities[country].sanitation_equipment_stockpile
            gdp = self.entities[country].gdp

            for locus in self.entities[country].loci:
                if locus.name == self.state[i]:
                    # print("Yes", locus.name, self.state, self.effect[i])
                    if (
                        health_resource
                        >= self.health_resource_cost * self.num_centers[i]
                        and sanitation_equipment
                        >= self.sanitation_equipment_cost * self.num_centers[i]
                        and gdp >= self.gdp_cost_per_center * self.num_centers[i]
                    ):
                        # print("ENOUNG RESOURCES", health_resource, sanitation_equipment, self.healt)
                        if (
                            self.entities[country].health_resource_stockpile
                            - self.health_resource_cost * self.num_centers[i]
                            <= 0
                        ):
                            self.entities[country].health_resource_stockpile = 0
                        else:
                            self.entities[country].health_resource_stockpile -= (
                                self.health_resource_cost * self.num_centers[i]
                            )

                        if (
                            self.entities[country].sanitation_equipment_stockpile
                            - self.sanitation_equipment_cost * self.num_centers[i]
                            <= 0
                        ):
                            self.entities[country].sanitation_equipment_stockpile = 0
                        else:
                            self.entities[country].sanitation_equipment_stockpile -= (
                                self.sanitation_equipment_cost * self.num_centers[i]
                            )

                        if (
                            self.entities[country].gdp
                            - self.gdp_cost_per_center * self.num_centers[i]
                            <= 0
                        ):
                            self.entities[country].gdp = 0
                        else:
                            self.entities[country].gdp -= (
                                self.gdp_cost_per_center * self.num_centers[i]
                            )

                        # print(locus.B, "LOCUS B")
                        locus.quarantine_facilities += self.num_centers[i]
                        if (
                            locus.B
                            - truncated_sigmoid(
                                locus.B
                                * locus.quarantine_facilities
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                            >= 1e-7
                        ):
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) / max_l
                            locus.B -= truncated_sigmoid(
                                locus.B
                                * locus.quarantine_facilities
                                * (locus.infected + locus.susceptible)
                                / max_living_population,
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                        else:
                            # print("Sigmoid missed")
                            # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value)
                            locus.B -= 0

                        # print(locus.name, locus.B, "LOCUS B")
                        # print(truncated_sigmoid(locus.B * self.effect[i] * (locus.infected + locus.susceptible) /max_living_population, self.trunk_min_value, self.trunk_max_value)

                    else:
                        # print("Insuff RES")
                        locus.B -= 0

                else:
                    pass

        # return {
        #     "QuarantineFacilitiesQProcess"
        #     + "_"
        #     + str(locus.name)
        #     + "_"
        #     + str(country): locus.B
        #     for locus in self.entities[country].loci
        # }


##########################################################################
##########################################################################
##########################################################################


class EconomicZoneEffectChangeProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country=[],
        economic_zone_names=[],
        effect=[],
    ):
        # super().__init__(id, entities, status)
        self.country = country
        self.economic_zone_names = economic_zone_names
        self.effect = effect

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        if len(self.country) > 0 and len(self.country) == len(self.economic_zone_names):
            for i, country in enumerate(self.country):
                for locus in self.entities[country].loci:
                    for economicZone in locus.economic_zones:
                        if economicZone["name"] == self.economic_zone_names[i]:
                            economicZone["effect"] = self.effect[i]
        self.status = "DEAD"


class EcoSpotContinous(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        max_tier=4,
        gdp_multiplier=1e5,
        trunk_min_value=1e-6,
        trunk_max_value=5e-5,
    ):

        # super().__init__(id, entities, status)
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value
        self.max_tier = max_tier
        self.gdp_multiplier = gdp_multiplier

    def while_dormant(self, step: int):
        pass

    def auto_run(self):
        # go through all the countries and increase the B value of locus based on available economic zone and its b_value_increase
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                total_b_increase = 0
                total_gdp_increase = 0
                if locus.economic_zones != None:
                    for economicZone in locus.economic_zones:
                        # print(economicZone["name"], economicZone["b_val_increase"])
                        total_b_increase += truncated_sigmoid(
                            (self.max_tier - economicZone["zone_tier"])
                            * economicZone["effect"],
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                        total_gdp_increase += total_b_increase * self.gdp_multiplier
                    # print(locus.name, total_b_increase, "name", "Increase")
                    if locus.B + total_b_increase < 1:
                        locus.B += total_b_increase
                    else:
                        locus.B -= 0.1 * locus.B

                    self.entities[country].gdp += total_gdp_increase
                    self.entities[country].health_resource_stockpile += 25
                    self.entities[country].sanitation_equipment_stockpile += 25

    def while_alive(self, step: int):
        self.auto_run()


##########################################################################
##########################################################################
##########################################################################


class TouristZoneEffectChangeProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country=[],
        tourist_zone_names=[],
        effect=[],
    ):
        # super().__init__(id, entities, status)
        self.country = country
        self.tourist_zone_names = tourist_zone_names
        self.effect = effect

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        if len(self.country) > 0 and len(self.country) == len(self.tourist_zone_names):
            for i, country in enumerate(self.country):
                for locus in self.entities[country].loci:
                    for touristZone in locus.tourist_zones:
                        if touristZone["name"] == self.tourist_zone_names[i]:
                            touristZone["effect"] = self.effect[i]
        self.status = "DEAD"


class TouristContinous(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        max_tier=4,
        gdp_multiplier=1e5,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):

        # super().__init__(id, entities, status)
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value
        self.max_tier = max_tier
        self.gdp_multiplier = gdp_multiplier

    def while_dormant(self, step: int):
        pass

    def auto_run(self):
        # go through all the countries and increase the B value of locus based on available economic zone and its b_value_increase
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                total_b_increase = 0
                total_gdp_increase = 0
                if locus.tourist_zones != None:
                    for touristZone in locus.tourist_zones:
                        # print(touristZone["name"], touristZone["b_val_increase"])
                        total_b_increase += truncated_sigmoid(
                            (self.max_tier - touristZone["zone_tier"])
                            * touristZone["effect"],
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                        total_gdp_increase += total_b_increase * self.gdp_multiplier
                    # print(locus.name, total_b_increase, "name", "Increase")
                    if locus.B + total_b_increase < 1:
                        locus.B += total_b_increase
                    else:
                        locus.B -= 0.1 * locus.B

                    self.entities[country].gdp += total_gdp_increase
                    self.entities[country].health_resource_stockpile += 25
                    self.entities[country].sanitation_equipment_stockpile += 25

    def while_alive(self, step: int):
        self.auto_run()


##########################################################################
##########################################################################
##########################################################################


class PortContinousProcess(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        trunk_min_value=5e-5,
        trunk_max_value=9e-4,
        max_tier=4,
        gdp_multiplier=1e6,
    ):
        # Give Country and economic zone name as list with same index corresponding to each others country (with same name as Initialized Entity) and economic zone name

        # super().__init__(id, entities, status)
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value
        self.max_tier = max_tier
        self.gdp_multiplier = gdp_multiplier

    def while_dormant(self, step: int):
        pass

    def auto_run(self):
        # go through all the countries and increase the B value of locus based on available economic zone and its b_value_increase
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                total_b_increase = 0
                total_gdp_increase = 0
                if locus.ports != None:
                    for portZones in locus.ports:
                        # print(economicZone["name"], economicZone["b_val_increase"])
                        total_b_increase += truncated_sigmoid(
                            (self.max_tier - portZones["zone_tier"])
                            * portZones["effect"],
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                        total_gdp_increase += total_b_increase * self.gdp_multiplier
                    # print(locus.name, total_b_increase, "name", "Increase")
                    if locus.B + total_b_increase < 1:
                        locus.B += total_b_increase
                    else:
                        locus.B -= 0.1 * locus.B

                    self.entities[country].gdp += total_gdp_increase
                    self.entities[country].health_resource_stockpile += 25
                    self.entities[country].sanitation_equipment_stockpile += 25

    def while_alive(self, step: int):
        self.auto_run()


class PortEffectChangeProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country=[],
        port_names=[],
        effect=[],
    ):
        # Give Country and economic zone name as list with same index corresponding to each others country (with same name as Initialized Entity) and economic zone name

        # super().__init__(id, entities, status)
        self.country = country
        self.port_names = port_names
        self.effect = effect

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        if len(self.country) > 0 and len(self.country) == len(self.port_names):
            for i, country in enumerate(self.country):
                for locus in self.entities[country].loci:
                    if locus.ports != None:
                        for portZones in locus.ports:
                            if portZones["name"] == self.port_names[i]:
                                portZones["effect"] = self.effect[i]
        self.status = "DEAD"


##########################################################################
##########################################################################
##########################################################################


class AirPortEffectChangeProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country=[],
        airport_names=[],
        effect=[],
    ):
        # Give Country and economic zone name as list with same index corresponding to each others country (with same name as Initialized Entity) and economic zone name

        # super().__init__(id, entities, status)
        self.country = country
        self.airport_names = airport_names
        self.effect = effect

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        if len(self.country) > 0 and len(self.country) == len(self.airport_names):
            for i, country in enumerate(self.country):
                for locus in self.entities[country].loci:
                    if locus.airports != None:
                        for airportZones in locus.airports:
                            if airportZones["name"] == self.airport_names[i]:
                                airportZones["effect"] = self.effect[i]
        self.status = "DEAD"


class AirPortContinousProcess(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        trunk_min_value=5e-4,
        trunk_max_value=9e-4,
        max_tier=4,
        gdp_multiplier=1e6,
    ):
        # Give Country and economic zone name as list with same index corresponding to each others country (with same name as Initialized Entity) and economic zone name

        # super().__init__(id, entities, status)
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value
        self.max_tier = max_tier
        self.gdp_multiplier = gdp_multiplier

    def while_dormant(self, step: int):
        pass

    def auto_run(self):
        # go through all the countries and increase the B value of locus based on available economic zone and its b_value_increase
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                total_b_increase = 0
                total_gdp_increase = 0
                if locus.airports != None:
                    for airportZones in locus.airports:
                        # print(economicZone["name"], economicZone["b_val_increase"])
                        total_b_increase += truncated_sigmoid(
                            (self.max_tier - airportZones["zone_tier"])
                            * airportZones["effect"],
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                        total_gdp_increase += total_b_increase * self.gdp_multiplier
                    # print(locus.name, total_b_increase, "name", "Increase")
                    if locus.B + total_b_increase < 1:
                        locus.B += total_b_increase
                    else:
                        locus.B -= 0.1 * locus.B

                    self.entities[country].gdp += total_gdp_increase
                    self.entities[country].health_resource_stockpile += 25
                    self.entities[country].sanitation_equipment_stockpile += 25

    def while_alive(self, step: int):
        self.auto_run()


############################################################################################################
#################### C VALUE CHANGE#######################################################################


############################################################################################################
#################### C VALUE CHANGE#######################################################################


class MandatoryVaccinationProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        percent_infected_vaccinated: list,
        gdp_cost_per_infected=0.01,
        health_resource_cost_per_infected=0.005,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):
        # super().__init__(id, entities, status)
        self.gdp_cost_per_infected = gdp_cost_per_infected
        self.health_resource_cost_per_infected = health_resource_cost_per_infected
        self.status = status
        self.percent_infected_vaccinated = percent_infected_vaccinated
        self.state = state
        self.country = country
        self.state = state
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        for i, country in enumerate(self.country):
            # print(country)
            # print(self.entities)
            healthcare_resource = self.entities[country].health_resource_stockpile
            for locus in self.entities[country].loci:
                if locus.name == self.state[i]:

                    # print("Yes", locus.name)
                    if (
                        healthcare_resource
                        >= self.health_resource_cost_per_infected
                        * locus.infected
                        * self.percent_infected_vaccinated[i]
                    ):
                        # print("ENOUNG RESOURCES", healthcare_resource, self.health_resource_cost_per_infected *locus.infected * self.percent_infected_vaccinated[i])
                        if (
                            self.entities[country].health_resource_stockpile
                            - self.health_resource_cost_per_infected
                            * locus.infected
                            * self.percent_infected_vaccinated[i]
                            <= 0
                        ):
                            self.entities[country].health_resource_stockpile = 0
                        else:
                            self.entities[country].health_resource_stockpile -= (
                                self.health_resource_cost_per_infected
                                * locus.infected
                                * self.percent_infected_vaccinated[i]
                            )

                        # print(locus.C, "LOCUS B  BEFORE")
                        if (
                            locus.C
                            + truncated_sigmoid(
                                locus.C * self.percent_infected_vaccinated[i],
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                            < 1
                        ):
                            locus.C += truncated_sigmoid(
                                locus.C * self.percent_infected_vaccinated[i],
                                self.trunk_min_value,
                                self.trunk_max_value,
                            )
                        else:
                            locus.C = 0.8
                        # print(locus.C, "LOCUS B AFTER")

                    else:
                        # print("Insuff RES")
                        locus.C -= locus.C * 0.02

                else:
                    pass


class GeneralHospitalBuildingProcess(ProcessV1):
    RANK = 1
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        country: list,
        state: list,
        num_hospitals: list,
        gdp_cost_per_hospital=10000,
        min_recovered_people=50,
        trunk_min_value=1e-5,
        trunk_max_value=5e-4,
    ):
        # super().__init__(id, entities, status)
        self.gdp_cost_per_hospital = gdp_cost_per_hospital
        self.min_recovered_people = min_recovered_people
        self.num_hospitals = num_hospitals
        self.state = state
        self.country = country
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def while_alive(self, step: int):
        if len(self.country) > 0:
            for i, country in enumerate(self.country):
                # print(country)
                # print(self.entities)
                healthcare_resource = self.entities[country].health_resource_stockpile
                for locus in self.entities[country].loci:
                    if locus.name == self.state[i]:

                        # print("Yes", locus.name)
                        if (
                            healthcare_resource
                            >= self.gdp_cost_per_hospital * self.num_hospitals[i]
                            and locus.recovered >= self.min_recovered_people
                        ):
                            # print("ENOUNG RESOURCES", healthcare_resource,self.gdp_cost_per_hospital)
                            if (
                                self.entities[country].health_resource_stockpile
                                - self.gdp_cost_per_hospital
                                <= 0
                            ):
                                self.entities[country].health_resource_stockpile = 0
                            else:
                                self.entities[
                                    country
                                ].health_resource_stockpile -= (
                                    self.gdp_cost_per_hospital
                                )

                            # print(locus.general_hospitals, "LOCUS B  BEFORE")
                            locus.general_hospitals += self.num_hospitals[i]
                            # print(locus.general_hospitals, "LOCUS B AFTER")

                        else:
                            # print("Insuff RES")
                            locus.C -= locus.C * 0.0002
        self.status = "DEAD"


class GeneralHospitalContinousProcess(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(
        self,
        id: str,
        entities,
        status: str,
        gdp_cost_per_hospital=10000,
        min_recovered_people=50,
        trunk_min_value=1e-4,
        trunk_max_value=5e-4,
    ):
        # Give Country and economic zone name as list with same index corresponding to each others country (with same name as Initialized Entity) and economic zone name

        # super().__init__(id, entities, status)
        self.status = status
        self.gdp_cost_per_hospital = gdp_cost_per_hospital
        self.min_recovered_people = min_recovered_people
        self.trunk_min_value = trunk_min_value
        self.trunk_max_value = trunk_max_value

    def while_dormant(self, step: int):
        pass

    def auto_run(self):
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                if locus.recovered >= self.min_recovered_people:
                    if (
                        self.entities[country].health_resource_stockpile
                        - self.gdp_cost_per_hospital
                        <= 0
                    ):
                        self.entities[country].health_resource_stockpile = 0
                    else:
                        self.entities[
                            country
                        ].health_resource_stockpile -= self.gdp_cost_per_hospital

                    if (
                        locus.C
                        + truncated_sigmoid(
                            locus.C * locus.general_hospitals * 0.03,
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                        < 1
                    ):
                        locus.C += truncated_sigmoid(
                            locus.C * locus.general_hospitals * 0.03,
                            self.trunk_min_value,
                            self.trunk_max_value,
                        )
                    else:
                        locus.C = 0.8
                else:
                    pass

    def while_alive(self, step: int):
        self.auto_run()


########################################################
###########################################################
################# Ds Process######################
class IncreaseDsProcess(ProcessV1):

    RANK = 0

    DOMAIN = (geo_political_entities.Country,)

    def __init__(self, id, entities, status):

        # super().__init__(id, entities)

        self.status = status

    def while_dormant(self, step: int):
        pass

    def scale_Ds_value(self, input_value, recovered_percent):

        # Scale the input value from the input range to the output range

        scaled_value = (input_value * recovered_percent - 0) / (
            max_living_population - min_living_population
        ) * (5e-3 - 5e-5) + 5e-5

        return scaled_value

    def while_alive(self, step: int):

        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                # Check if the locus has susceptible people
                if locus.susceptible > 0:
                    # Calculate the percentage of susceptible people
                    recovered_percent = locus.susceptible / (
                        locus.susceptible + locus.infected + locus.recovered
                    )
                    # Increase Ds based on the susceptible percent
                    if locus.Ds < 0.2:
                        # Calculate scale based on country attributes and susceptible percent
                        scale = self.scale_Ds_value(
                            base_death_rate
                            * (1 - (min_gdp / self.entities[country].gdp))
                            * self.entities[country].happiness_index
                            * self.entities[country].human_welfare_resource,
                            recovered_percent,
                        )
                        # Increase Ds by scale, but ensure it does not exceed a certain limit (e.g., 0.4)
                        if locus.Ds + scale <= 0.2:
                            locus.Ds += scale
                        else:
                            locus.Ds = 0.2


class IncreaseDiProcess(ProcessV1):

    RANK = 0

    DOMAIN = (geo_political_entities.Country,)

    def __init__(self, id, entities, status):

        # super().__init__(id, entities)

        self.status = status

    def while_dormant(self, step: int):
        pass

    def scale_Ds_value(self, input_value, infected_percent):

        # Scale the input value from the input range to the output range

        scaled_value = (input_value * infected_percent - 0) / (
            max_living_population - min_living_population
        ) * (5e-3 - 5e-4) + 5e-4

        return scaled_value

    def while_alive(self, step: int):

        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                # Check if the locus has susceptible people
                if locus.infected > 0:
                    # Calculate the percentage of susceptible people
                    infected_percent = locus.infected / (
                        locus.susceptible + locus.infected + locus.recovered
                    )
                    # Increase Ds based on the susceptible percent
                    if locus.Di < 0.2:
                        # Calculate scale based on country attributes and susceptible percent
                        scale = self.scale_Ds_value(
                            base_infection_lethality
                            * base_death_rate
                            * (1 - (min_gdp / self.entities[country].gdp)),
                            infected_percent,
                        )
                        # Increase Ds by scale, but ensure it does not exceed a certain limit (e.g., 0.4)
                        if locus.Di + scale <= 0.3:
                            locus.Di += scale
                        else:
                            locus.Di = 0.2


class IncreaseDrProcess(ProcessV1):

    RANK = 0

    DOMAIN = (geo_political_entities.Country,)

    def __init__(self, id, entities, status):

        # super().__init__(id, entities)

        self.status = status

    def while_dormant(self, step: int):
        pass

    def scale_Ds_value(self, input_value, recovered_percent):

        # Scale the input value from the input range to the output range

        scaled_value = (input_value * recovered_percent - 0) / (
            max_living_population - min_living_population
        ) * (5e-4 - 5e-6) + 5e-6

        return scaled_value

    def while_alive(self, step: int):

        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                # Check if the locus has susceptible people
                if locus.recovered > 0:
                    # Calculate the percentage of susceptible people
                    recovered_percent = locus.recovered / (
                        locus.susceptible + locus.infected + locus.recovered
                    )
                    # Increase Ds based on the susceptible percent
                    if locus.Dr < 0.15:
                        # Calculate scale based on country attributes and susceptible percent
                        scale = self.scale_Ds_value(
                            base_death_rate
                            * (1 - (min_gdp / self.entities[country].gdp)),
                            recovered_percent,
                        )
                        # Increase Ds by scale, but ensure it does not exceed a certain limit (e.g., 0.4)
                        if locus.Dr + scale <= 0.15:
                            locus.Dr += scale
                        else:
                            locus.Dr = 0.1


class IncreaseEProcess(ProcessV1):
    RANK = 0
    DOMAIN = (geo_political_entities.Country,)

    def __init__(self, id, entities, status):
        self.status = status

    def while_dormant(self, step):
        pass

    def scale_E_value(self, input_value, recovered_infected):
        # Scale the input value from the input range to the output range
        scaled_value = (input_value * recovered_infected - 0) / (
            max_living_population - min_living_population
        ) * (5e-3 - 5e-5) + 5e-5
        return scaled_value

    def while_alive(self, step):
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                if locus.recovered > 0 and locus.E < 0.2:
                    # Calculate the percentage of recovered people in the locus
                    recovered_infected = locus.recovered / (
                        locus.susceptible + locus.infected + locus.recovered
                    )

                    # Calculate scale based on country attributes and recovered percent
                    scale = self.scale_E_value(
                        base_re_entry_rate
                        * (1 - (min_gdp / self.entities[country].gdp))
                        * self.entities[country].happiness_index
                        * self.entities[country].human_welfare_resource,
                        recovered_infected,
                    )

                    # Increase E by scale, but ensure it does not exceed a certain limit (e.g., 0.4)
                    if locus.E + scale <= 0.1:
                        locus.E += scale
                    else:
                        locus.E = 0.1


class DiseaseSpreadProcess(ProcessV1):
    RANK = 4
    DOMAIN = (geo_political_entities.Country,)

    def __init__(self, id, entities, status):
        self.status = status

    def while_dormant(self, step):
        pass

    def while_alive(self, step):
        for country in self.entities.keys():
            for locus in self.entities[country].loci:
                # Reduce susceptible by B percent and move the reduced value to infected
                infected = locus.susceptible * locus.B
                if locus.susceptible > infected:
                    locus.infected += infected
                    locus.susceptible -= infected
                else:
                    locus.infected += locus.susceptible
                    locus.susceptible = 0

                # Increase susceptible by A percent
                susceptible = locus.susceptible * locus.A
                locus.susceptible += susceptible

                # Reduce susceptible by Ds percent and move the reduced value to dead
                dead = locus.susceptible * locus.Ds
                if locus.susceptible > dead:
                    locus.dead += dead
                    locus.susceptible -= dead
                else:
                    locus.dead += locus.susceptible
                    locus.susceptible = 0

                # Reduce infected by C percent and move the reduced value to recovered
                recovered = locus.infected * locus.C
                if locus.infected > recovered:
                    locus.recovered += recovered
                    locus.infected -= recovered
                else:
                    locus.recovered += locus.infected
                    locus.infected = 0

                # Reduce infected by Di percent and move the reduced value to dead
                dead = locus.infected * locus.Di
                if locus.infected > dead:
                    locus.dead += dead
                    locus.infected -= dead
                else:
                    locus.dead += locus.infected
                    locus.infected = 0

                # Reduce recovered by Dr percent and move the reduced value to dead
                dead = locus.recovered * locus.Dr
                if locus.recovered > dead:
                    locus.dead += dead
                    locus.recovered -= dead
                else:
                    locus.dead += locus.recovered
                    locus.recovered = 0
                # Reduce recovered by E percent and move the reduced value to susceptible
                susceptible = locus.recovered * locus.E
                if locus.recovered > susceptible:
                    locus.susceptible += susceptible
                    locus.recovered -= susceptible
                else:
                    locus.susceptible += locus.recovered
                    locus.recovered = 0
