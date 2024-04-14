base_infection_rate = 0.003  # Fractional increase in infected population per day
base_recovery_rate = 0.001  # Fractional increase in recovered population per day
base_death_rate = 0.005  # Fractional increase in death rate per day
base_birth_rate = 0.005  # Fractional increase in birth rate per day
epidemic_increased_infection_rate = 0.01  # Will be present in the parent locus of disease origin,
# if a new locus get more than 30% of its population infected then its base_infection_rate will be increased to this value