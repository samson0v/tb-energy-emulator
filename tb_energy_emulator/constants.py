# Solar Batteries Constants

LUX_BY_TIME = {
    tuple(range(6, 12)): 25_000,
    tuple(range(12, 18)): 100_000,
    tuple(range(18, 21)): 50_000,
    tuple(range(21, 24)): 0
}

TEMPERATURE_BY_TIME = {
    tuple(range(6, 12)): 15,
    tuple(range(12, 18)): 30,
    tuple(range(18, 21)): 26
}

SOLAR_BATTERIES_V_CELL = 1.67
SOLAR_BATTERIES_C_V = -0.002
SOLAR_BATTERIES_NUM_CELLS = 36
SOLAR_BATTERIES_I_SC_REF = 10

# Wind Turbine Constants

WIND_SPEED_BY_TIME = {
    tuple(range(0, 6)): (15, 25),
    tuple(range(6, 12)): (3, 5),
    tuple(range(12, 18)): (10, 20),
    tuple(range(18, 24)): (5, 10)
}

ROTOR_RADIUS = 0.7
TIP_SPEED_RATIO = 7

# Generator Constants

FUEL_RATE_BY_CONSUMPTION = {
    10000: 3,
    15_000: 8,
    20_000: 13
}

MINIMUM_FUEL_RATE = 3
GENERATOR_EFFICIENCY = 0.85
FUEL_ENERGY_DENSITY = 34.2

# Consamption Constants

CONSUPTION_BY_TIME = {
    tuple(range(0, 6)): 10_000,
    tuple(range(6, 12)): 15_000,
    tuple(range(12, 18)): 20_000,
    tuple(range(18, 24)): 15_000
}
MINIMUM_CONSUMPTION = 10_000

# Power Transformer Constants

DAILY_RATE_HOURS = (6, 23)
NIGHT_RATE_HOURS = (23, 6)

# Battery Constants

CAPACITY_WH = 100_000
CHARGING_DURATION_IN_HOURS = 4
MAX_CHARGING_LEVEL_WITH_BATTERY_LIFE = 80
CHARGIN_DURATION_AFTER_80_PERCENT = 10
