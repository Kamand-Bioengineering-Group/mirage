base_infection_rate = 0.003  # Fractional increase in infected population per day
base_recovery_rate = 0.001  # Fractional increase in recovered population per day
base_re_entry_rate = 0.001  # Fractional increase in re-entered population per day
base_death_rate = 0.005  # Fractional increase in death rate per day
base_birth_rate = 0.005  # Fractional increase in birth rate per day
epidemic_increased_infection_rate = 0.01  # Will be present in the parent locus of disease origin,
base_infection_lethality = 0.2

min_gdp = 1000
min_health_resource_stockpile = 10
min_sanitation_equipment_stockpile = 10
min_human_welfare_resource = 10

max_living_population = 1e10
min_living_population = 0

gdp_trickle_min = 5000
gdp_trickle_max = 20000

human_welfare_trickle_min = 100
human_welfare_trickle_max = 300

vaccine_trickle = 100
sanitation_trickle = 100
health_resource_trickle = 100

max_limit_disease_research_center = 50
# if a new locus get more than 30% of its population infected then its base_infection_rate will be increased to this values