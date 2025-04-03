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
SOLAR_BATTERIES_NUM_CELLS = 260
SOLAR_BATTERIES_I_SC_REF = 9

# Wind Turbine Constants

WIND_SPEED_BY_TIME = {
    tuple(range(0, 2)): (8, 9),
    tuple(range(2, 4)): (10, 11),
    tuple(range(4, 6)): (9, 10),
    tuple(range(6, 8)): (3, 4),
    tuple(range(8, 10)): (4, 5),
    tuple(range(10, 12)): (1, 2),
    tuple(range(12, 14)): (2, 3),
    tuple(range(14, 16)): (5, 6),
    tuple(range(16, 18)): (6, 7),
    tuple(range(18, 20)): (8, 9),
    tuple(range(20, 22)): (7, 8),
    tuple(range(22, 24)): (6, 7)
}

ROTOR_RADIUS = 1.7
TIP_SPEED_RATIO = 7

# Generator Constants

FUEL_RATE_BY_CONSUMPTION = {
    tuple(range(0, 10_000)): 3,
    tuple(range(10_000, 15_000)): 8,
    tuple(range(15_000, 21_000)): 13
}

MINIMUM_FUEL_RATE = 3
FUEL_VOLUME = 60

# Consamption Constants

CONSUPTION_BY_TIME = {
    tuple(range(0, 6)): 10_000,
    tuple(range(6, 12)): 15_000,
    tuple(range(12, 18)): 20_000,
    tuple(range(18, 24)): 15_000
}
MINIMUM_CONSUMPTION = 10_000

# Power Transformer Constants

MAX_OUTPUT_POWER = 49_000
DAILY_RATE_HOURS = tuple(range(6, 24))
CONSUMPTION_RESET_PERIOD = 168  # 7 days

# Battery Constants

MAX_CAPACITY_WH = 100_000
CHARGING_DURATION_IN_HOURS = 4
MAX_CHARGING_LEVEL_WITH_BATTERY_LIFE = 80
CHARGIN_DURATION_AFTER_80_PERCENT = 10
MAX_VOLTAGE = 110.4
MIN_VOLTAGE = 89.6
