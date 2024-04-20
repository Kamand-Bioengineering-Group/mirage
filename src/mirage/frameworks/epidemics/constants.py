# ---INFO-----------------------------------------------------------------------
"""
Constants for geo-political entities.
"""


# ---CONSTANTS------------------------------------------------------------------
base_infection_rate = 0.003
base_recovery_rate = 0.001
base_re_entry_rate = 0.001
base_death_rate = 0.005
base_birth_rate = 0.005

epidemic_increased_infection_rate = 0.01
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

airport_mappings = {
    "Beijing Capital International Airport": (0, "China"),
    "Beijing Daxing International Airport": (1, "China"),
    "Shanghai Pudong International Airport": (2, "China"),
    "Shanghai Hongqiao International Airport": (3, "China"),
    "Guangzhou Baiyun International Airport": (4, "China"),
    "Shenzhen Bao'an International Airport": (5, "China"),
    "Hangzhou Xiaoshan International Airport": (6, "China"),
    "Ningbo Lishe International Airport": (7, "China"),
    "Charles de Gaulle Airport": (8, "France"),
    "Orly Airport": (9, "France"),
    "Lyon–Saint-Exupéry Airport": (10, "France"),
    "Lyon-Bron Airport": (11, "France"),
    "Marseille Provence Airport": (12, "France"),
    "Aix-en-Provence Aerodrome": (13, "France"),
    "Nice Côte d'Azur Airport": (14, "France"),
    "Cannes-Mandelieu Airport": (15, "France"),
    "Chhatrapati Shivaji Maharaj International Airport": (16, "India"),
    "Pune Airport": (17, "India"),
    "Indira Gandhi International Airport": (18, "India"),
    "Chaudhary Charan Singh International Airport": (19, "India"),
    "Cochin International Airport": (20, "India"),
    "Sardaar Vallabhbhai Patel International Airport": (21, "India"),
    "Narita International Airport": (22, "Japan"),
    "Haneda Airport": (23, "Japan"),
    "Kansai International Airport": (24, "Japan"),
    "Osaka International Airport": (25, "Japan"),
    "New Chitose Airport": (26, "Japan"),
    "Okadama Airport": (27, "Japan"),
    "Los Angeles International Airport": (28, "United States"),
    "San Francisco International Airport": (29, "United States"),
    "John F. Kennedy International Airport": (30, "United States"),
    "LaGuardia Airport": (31, "United States"),
    "Miami International Airport": (32, "United States"),
    "Orlando International Airport": (33, "United States"),
}

airport_adjacency = {
    0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 29, 30],
    1: [0, 1, 2, 4, 5, 6, 8, 18, 20, 24, 29],
    2: [0, 2, 3, 5, 6, 7, 18, 20, 23, 24, 29, 30],
    3: [0, 2, 3, 6, 7, 8, 18, 20, 23, 24],
    4: [0, 1, 2, 20, 24, 29],
    5: [0, 1, 2, 6, 20, 23, 24],
    6: [0, 1, 2, 18, 20],
    7: [0, 2, 3, 18, 20],
    8: [0, 3, 8, 9, 10, 11, 12, 14, 15, 18, 20, 23, 24, 29, 30],
    9: [8, 9, 10, 11, 12, 14, 15],
    10: [8, 9, 10, 11, 12, 14, 15],
    11: [8, 9, 10, 11, 12, 14, 15],
    12: [8, 9, 10, 11, 12, 14, 15],
    13: [8, 9, 10, 11, 12, 14, 15],
    14: [8, 9, 10, 11, 12, 14, 15],
    15: [8, 9, 10, 11, 12, 14, 15],
    16: [0, 1, 9, 8, 16, 17, 18, 19, 20, 21, 23, 24, 25, 29, 30, 32],
    17: [16, 17, 18, 19, 20, 21],
    18: [16, 17, 18, 19, 20, 21],
    19: [0, 1, 16, 17, 18, 19, 20, 21, 22, 23, 32, 33],
    20: [0, 1, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32],
    21: [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32],
    22: [0, 1, 8, 9, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32],
    23: [0, 1, 2, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32],
    24: [5, 21, 22, 23, 24, 25, 29, 30, 32],
    25: [0, 1, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32],
    26: [18, 20, 23, 24],
    27: [18, 20, 23, 24],
    28: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 28, 29, 30, 31, 32, 33],
    29: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 29, 30],
    30: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 28, 29, 30, 31, 32, 33],
    31: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 28, 29, 30, 31, 32, 33],
    32: [0, 1, 2, 3, 4, 5, 6, 7, 8, 18, 20, 23, 24, 29, 30],
}

port_mappings = {
    "Port of Tianjin": (0, "China"),
    "Port of Dalian": (1, "China"),
    "Port of Shanghai": (2, "China"),
    "Port of Guangzhou": (3, "China"),
    "Port of Shenzhen": (4, "China"),
    "Port of Ningbo-Zhoushan": (5, "China"),
    "Port of Le Havre": (6, "France"),
    "Port of Lyon": (7, "France"),
    "Port of Marseille": (8, "France"),
    "Port of Toulon": (9, "France"),
    "Port of Nice": (10, "France"),
    "Port of Cannes": (11, "France"),
    "Mumbai Port": (12, "India"),
    "Goa Port": (13, "India"),
    "Cochin Port": (14, "India"),
    "Kandla Port": (15, "India"),
    "Port of Tokyo": (16, "Japan"),
    "Port of Yokohama": (17, "Japan"),
    "Port of Osaka": (18, "Japan"),
    "Port of Otaru": (19, "Japan"),
    "Port of Los Angeles": (20, "United States"),
    "Port of Long Beach": (21, "United States"),
    "Port of New York and New Jersey": (22, "United States"),
    "Port of Miami": (23, "United States"),
}

port_adjacency = {
    0: [1, 2, 3, 4, 5, 16, 17, 15],
    1: [0, 2, 3, 4, 5, 16, 17, 15],
    2: [0, 1, 3, 4, 5, 16, 18, 15],
    3: [0, 1, 2, 4, 5],
    4: [0, 1, 2, 3, 5],
    5: [0, 1, 2, 3, 4],
    6: [7, 8, 9, 10, 11, 22, 23],
    7: [6, 8, 9, 10, 11],
    8: [6, 7, 9, 10, 11, 23],
    9: [6, 7, 8, 10, 11, 22],
    10: [6, 7, 8, 9, 11, 23, 22],
    11: [6, 7, 8, 9, 10],
    12: [13, 14, 15, 22, 23, 21, 0, 1, 16],
    13: [12, 14, 15, 22, 23, 0],
    14: [12, 13, 15, 22, 23, 21, 0, 1, 16],
    15: [12, 13, 14, 0, 1, 16],
    16: [17, 18, 19, 0, 1, 12, 14],
    17: [16, 18, 19, 0, 1],
    18: [16, 17, 19, 0, 1],
    19: [16, 17, 18, 0, 1, 12, 14],
    20: [21, 22, 23, 0, 1, 12, 14, 15, 16, 6],
    21: [20, 22, 23, 0, 12, 15, 8],
    22: [20, 21, 23, 12, 15, 6],
    23: [20, 21, 22],
}
