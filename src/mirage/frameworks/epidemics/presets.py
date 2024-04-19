# ---INFO-----------------------------------------------------------------------
"""
Module for presets, epidemics.
"""

__all__ = [
    "preset_kbg_epidemic_2_0",
]


# ---DEPENDENCIES---------------------------------------------------------------
import os, yaml, requests
from . import gpe, all_processes as ap
from ...engines import firefly
from ...monitors.loggers.tbx_loggers import TbxTimeseriesLoggerV1


# ---EPICDEMIC 2.0--------------------------------------------------------------
def preset_kbg_epidemic_2_0(
    player_name: str, engine_speed: int = 7, log_dir: str = None
):
    """
    Preset for KBG - Epidemic 2.0.

    Parameters
    ----------
    player_name : str
        Name of the player.
    engine_speed : int, optional
        Speed of the engine, by default 7.
    log_dir : str, optional
        Directory to log the data.

    Returns
    -------
    tuple
        Tuple of countries, core_processes, epidemic_two_engine, tboard.
    """
    countries = {}
    for country in ["india", "china", "france", "japan", "usa"]:
        configl = (
            "https://raw.githubusercontent.com/"
            "Kamand-Bioengineering-Group/mirage/epidemic-two/"
            f"configs/frameworks/epidemics/countries/{country}.yaml"
        )
        try:
            config = requests.get(configl).text
            config = yaml.load(config, Loader=yaml.FullLoader)
            countries[config["name"]] = gpe.Country(**config)
        except:
            raise ValueError(f"{country} not found from {configl}")

    core_processes = {}
    for pname, pclass in {
        "birth": ap.BirthProcess,
        "ecosp": ap.EcoSpotContinous,
        "inc_e": ap.IncreaseEProcess,
        "incdr": ap.IncreaseDrProcess,
        "incdi": ap.IncreaseDiProcess,
        "incds": ap.IncreaseDsProcess,
        "touri": ap.TouristContinous,
        "airpo": ap.AirPortContinousProcess,
        "portp": ap.PortContinousProcess,
        "dissp": ap.DiseaseSpreadProcess,
        "ghocp": ap.GeneralHospitalContinousProcess,
    }.items():
        core_processes[pname] = pclass(pname, countries, "ALIVE")

    epidemic_two_engine = firefly.FireflyV1(
        f"EPIDEMIC2.0_{player_name}",
        firefly.FireflyV1State(baba_black_sheep=player_name),
        list(core_processes.values()),
        list(countries.values()),
        engine_speed,
        7,
        None,
        player_name,
    )

    if not log_dir:
        log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    direc = os.listdir(log_dir)
    latexp = 0
    for x in direc:
        if "experiment" in x:
            latexp = max(latexp, int(x.split("-")[-1]))

    tboard = TbxTimeseriesLoggerV1(
        epidemic_two_engine, f"{log_dir}/experiment-{latexp+1}", "local"
    )
    for attr in (
        "gdp",
        "health_resource_stockpile",
        "sanitation_equipment_stockpile",
        "human_welfare_resource",
    ):
        config = {
            attr: (
                attr,
                [(country, country.name) for country in countries.values()],
            )
        }
        tboard.register_objects(config)
    for country, cobj in countries.items():
        for sir in ("susceptible", "infected", "recovered"):
            config = {
                f"{country}/loci_{sir}": (
                    sir,
                    [(locus, f"{locus.name}") for locus in cobj.loci],
                )
            }
            tboard.register_objects(config)
    for epi_model_param in ["A", "B", "C", "Ds", "Di", "Dr", "E"]:
        for country, cobj in countries.items():
            ldata = {
                f"{country}/{epi_model_param}": (
                    epi_model_param,
                    [(locus, f"{locus.name}") for locus in cobj.loci],
                )
            }
            tboard.register_objects(ldata)

    peri_proc_config = {
        "maski": ("DORMANT", countries, ap.MaskImplementationProcess),
        "aidki": ("DORMANT", countries, ap.AidKitImplementationProcess),
        "gsani": ("DORMANT", countries, ap.General_Sanitation_Implementation),
        "quafa": ("DORMANT", countries, ap.QuarantineFacilitiesQProcess),
        "eczec": ("DORMANT", countries, ap.EconomicZoneEffectChangeProcess),
        "trzec": ("DORMANT", countries, ap.TouristZoneEffectChangeProcess),
        "airec": ("DORMANT", countries, ap.AirPortEffectChangeProcess),
        "porec": ("DORMANT", countries, ap.PortEffectChangeProcess),
        "mvacp": ("DORMANT", countries, ap.MandatoryVaccinationProcess),
        "ghobp": ("ALIVE", countries, ap.GeneralHospitalBuildingProcess),
    }
    epidemic_two_engine.register_peripheral_processes(peri_proc_config)
    epidemic_two_engine.intervene = epidemic_two_engine.spawn_peripheral_process

    tboard.start_server()

    return countries, core_processes, epidemic_two_engine, tboard
