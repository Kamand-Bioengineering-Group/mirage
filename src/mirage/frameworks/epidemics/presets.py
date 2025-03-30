# ---INFO-----------------------------------------------------------------------
"""
Module for presets, epidemics.
"""

__all__ = [
    "preset_kbg_epidemic_2_0",
    "preset_kbg_epidemic_2_0_competition",
]


# ---DEPENDENCIES---------------------------------------------------------------
import os, yaml, requests, types
from . import geo_political_entities, all_processes as ap
from ...engines import firefly
from ...monitors.loggers.tbx_loggers import TbxTimeseriesLoggerV1
from . import competition

import ipywidgets
from IPython.display import display
from typing import Dict, Optional, Tuple, Any


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
            countries[config["name"]] = geo_political_entities.Country(**config)
        except:
            raise ValueError(f"{country} not found fron on {configl}")

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
        "eczec": ("ALIVE", countries, ap.EconomicZoneEffectChangeProcess),
        "trzec": ("ALIVE", countries, ap.TouristZoneEffectChangeProcess),
        "airec": ("ALIVE", countries, ap.AirPortEffectChangeProcess),
        "porec": ("ALIVE", countries, ap.PortEffectChangeProcess),
        "ghobp": ("ALIVE", countries, ap.GeneralHospitalBuildingProcess),
        "mvacp": ("DORMANT", countries, ap.MandatoryVaccinationProcess),
        "maski": ("DORMANT", countries, ap.MaskImplementationProcess),
        "aidki": ("DORMANT", countries, ap.AidKitImplementationProcess),
        "gsani": ("DORMANT", countries, ap.General_Sanitation_Implementation),
        "quafa": ("DORMANT", countries, ap.QuarantineFacilitiesQProcess),
    }
    epidemic_two_engine.register_peripheral_processes(peri_proc_config)
    epidemic_two_engine.intervene = epidemic_two_engine.spawn_peripheral_process

    # TODO: Migrate to EngineV1?
    def dynamics_control_panel(self):
        play_b = ipywidgets.Button(description="▶️")
        paus_b = ipywidgets.Button(description="⏸️")
        stop_b = ipywidgets.Button(description="⏹️")
        speeds = ipywidgets.IntSlider(
            value=self.speed, min=1, max=30, step=1, description="⏩"
        )
        flabel = ipywidgets.Label(value="🎛️ Control Panel")
        cli_pl = lambda b: self.play()
        cli_pa = lambda b: self.pause()
        cli_st = lambda b: self.stop()

        def del_sp(c):
            self.speed = c["new"]

        play_b.on_click(cli_pl)
        paus_b.on_click(cli_pa)
        stop_b.on_click(cli_st)
        speeds.observe(del_sp, names="value")
        display(ipywidgets.HBox([flabel, play_b, paus_b, stop_b, speeds]))

    epidemic_two_engine.dynamics_control_panel = types.MethodType(
        dynamics_control_panel, epidemic_two_engine
    )

    tboard.start_server()

    return countries, core_processes, epidemic_two_engine, tboard

# ---EPIDEMIC 2.0 COMPETITION--------------------------------------------------
def preset_kbg_epidemic_2_0_competition(
    player_name: str, 
    engine_speed: int = 7, 
    log_dir: str = None,
    competition_results_dir: str = None,
    score_weights: Optional[Dict[str, float]] = None
):
    """
    Preset for KBG - Epidemic 2.0 Competition.

    This preset extends the standard Epidemic 2.0 preset with competition elements:
    - Standardized initial conditions for all players
    - Score tracking and evaluation
    - Leaderboard generation

    Parameters
    ----------
    player_name : str
        Name of the player.
    engine_speed : int, optional
        Speed of the engine, by default 7.
    log_dir : str, optional
        Directory to log the data.
    competition_results_dir : str, optional
        Directory to store competition results.
    score_weights : Dict[str, float], optional
        Custom weights for scoring components.

    Returns
    -------
    tuple
        Tuple of (countries, core_processes, epidemic_two_engine, tboard, 
                 competition_manager, competition_leaderboard)
    """
    # First, get the standard preset
    countries, core_processes, epidemic_two_engine, tboard = preset_kbg_epidemic_2_0(
        player_name=player_name,
        engine_speed=engine_speed,
        log_dir=log_dir
    )
    
    # Add competition components
    competition_manager, competition_leaderboard = competition.add_competition_to_preset(
        countries,
        core_processes,
        epidemic_two_engine,
        tboard,
        score_weights,
        competition_results_dir
    )
    
    # Add competition-specific controls to the engine
    def calculate_and_display_score(self):
        """Calculate and display the current score."""
        score = competition_manager.calculate_score()
        
        # Create a formatted output of the score
        score_display = [
            "📊 Current Score",
            f"Overall: {score['final_score']:.2f}",
            "",
            "Component Scores (weighted):",
            f"Population Survived: {score['population_survived']:.2f} × {competition_manager.score_weights['population_survived']} = {score['population_survived'] * competition_manager.score_weights['population_survived']:.2f}",
            f"GDP Preserved: {score['gdp_preserved']:.2f} × {competition_manager.score_weights['gdp_preserved']} = {score['gdp_preserved'] * competition_manager.score_weights['gdp_preserved']:.2f}",
            f"Infection Control: {score['infection_control']:.2f} × {competition_manager.score_weights['infection_control']} = {score['infection_control'] * competition_manager.score_weights['infection_control']:.2f}",
            f"Resource Efficiency: {score['resource_efficiency']:.2f} × {competition_manager.score_weights['resource_efficiency']} = {score['resource_efficiency'] * competition_manager.score_weights['resource_efficiency']:.2f}",
            f"Time to Containment: {score['time_to_containment']:.2f} × {competition_manager.score_weights['time_to_containment']} = {score['time_to_containment'] * competition_manager.score_weights['time_to_containment']:.2f}",
        ]
        
        return "\n".join(score_display)
    
    def display_current_score(self):
        """Display the current score."""
        score_text = calculate_and_display_score(self)
        print(score_text)
    
    def save_competition_results(self):
        """Save competition results and return path to results file."""
        result_file = competition_manager.save_results()
        print(f"Competition results saved to: {result_file}")
        return result_file
    
    def display_leaderboard(self):
        """Generate and display the current leaderboard."""
        leaderboard = competition_leaderboard.generate_leaderboard()
        return leaderboard
    
    def save_leaderboard(self):
        """Save the current leaderboard and return path to file."""
        leaderboard_file = competition_leaderboard.save_leaderboard()
        print(f"Leaderboard saved to: {leaderboard_file}")
        return leaderboard_file
    
    # Attach methods to the engine instance
    epidemic_two_engine.calculate_score = types.MethodType(calculate_and_display_score, epidemic_two_engine)
    epidemic_two_engine.display_score = types.MethodType(display_current_score, epidemic_two_engine)
    epidemic_two_engine.save_results = types.MethodType(save_competition_results, epidemic_two_engine)
    epidemic_two_engine.display_leaderboard = types.MethodType(display_leaderboard, epidemic_two_engine)
    epidemic_two_engine.save_leaderboard = types.MethodType(save_leaderboard, epidemic_two_engine)
    
    return countries, core_processes, epidemic_two_engine, tboard, competition_manager, competition_leaderboard
