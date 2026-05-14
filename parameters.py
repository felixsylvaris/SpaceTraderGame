# =============================================================
#  SPICE SPACE TRADER — parameters.py
#  Balance data only. No functions, no logic.
#  Edit this file to adjust game balance.
# =============================================================

# ── FILE PATHS ────────────────────────────────────────────────
SAVE_FILE  = "spice_trader_save.json"

# ── FUEL ─────────────────────────────────────────────────────
FUEL_PRICE         = 1   # credits per fuel unit — raise for OPEC crisis event
MIN_FUEL_TO_DEPART = 50  # minimum fuel required to leave port

# ── STARTING SHIP STATE ───────────────────────────────────────
SHIP_START = {
    "credits":        1000,
    "cargo":          {},
    "location":       "Terra",
    "fuel":           500,
    "max_fuel":       500,
    "max_cargo":      100,
    "farm_bought":    False,
    "weapons":        0,
    "broker_license": False,
    "passenger_slot": False,
    "passenger":      None,
    "radar":          False,
    "booster":        False,
    "upgrades_bought": [],
}

# ── CALENDAR ─────────────────────────────────────────────────
MONTH_NAMES     = ["Ianu","Febu","Mari","Aprix","Maiu","Iuin","Septr","Octo","Nova","Dedl"]
MONTHS_PER_YEAR = 10
START_YEAR      = 2201

# ── PLANET ORDER ─────────────────────────────────────────────
# Order matters — travel fuel cost scales with index distance
PLANET_NAMES = ["Terra", "Zeta-9", "Void Colony", "Agrica", "Nexus"]

# ── TRAVEL FUEL COST ─────────────────────────────────────────
# cost = abs(index_diff) * TRAVEL_COST_PER_HOP + random jitter
# clamped to [TRAVEL_MIN, TRAVEL_MAX]
TRAVEL_COST_PER_HOP = 12
TRAVEL_JITTER       = 5   # ± random added to cost
TRAVEL_MIN          = 10
TRAVEL_MAX          = 50

# ── GOOD DATA ─────────────────────────────────────────────────
# (spread_type, min_price, mean_price, max_price)
# spread_type: "low"=±5  "mid"=±10  "high"=±15
# min/max clamp the drifting base price; mean is the starting reference
# production/demand prices on home planets may differ (set in planets_template)

GOOD_DATA = {
    #                 spread    min   mean    max
    "Cinnamon":      ("low",     15,    50,   150),
    "Turmeric":      ("low",     18,    60,   180),
    "Paprika":       ("low",     21,    70,   210),
    "Ginger":        ("mid",     24,    80,   240),
    "Clove":         ("mid",     27,    90,   270),
    "Vanilla":       ("mid",     30,   100,   300),
    "Cardamom":      ("mid",     33,   110,   330),
    "Allspice":      ("high",    36,   120,   360),
    "Saffron":       ("high",    45,   150,   450),
    "Nutmeg":        ("high",    42,   140,   420),
    "Void Pepper":   ("high",   150,   500,  1500),
    "Mystery Crate": ("low",      1,    10,   500),  # wildcard — wide range
}

SPREAD_AMOUNT = {"low": 5, "mid": 10, "high": 15}

# ── INFLATION ────────────────────────────────────────────────
# Each turn, neutral goods drift by a random amount.
# 50% chance up, 50% chance down. Clamped to GOOD_DATA bounds.
INFLATION_UP_MAX   = 10   # max drift upward per turn
INFLATION_DOWN_MAX = 9    # max drift downward per turn

# ── HARVEST SEASONS ──────────────────────────────────────────
# (harvest_month_index, pattern_key)
# month index is 0-based; 0=Ianu, 9=Dedl
# None = no seasonal effect

GOOD_SEASONS = {
    "Cinnamon":      (0, "low"),
    "Turmeric":      (1, "low"),
    "Paprika":       (2, "low"),
    "Ginger":        (3, "mid"),
    "Clove":         (4, "mid"),
    "Vanilla":       (5, "mid"),
    "Cardamom":      (6, "mid"),
    "Allspice":      (7, "high"),
    "Saffron":       (8, "high"),
    "Nutmeg":        (9, "high"),
    "Void Pepper":   None,         # exotic drug — no harvest cycle
    "Mystery Crate": None,
}

# Seasonal price offset by months-since-harvest (index 0 = harvest month)
SEASON_LOW  = [  0,   0,  +5,  +5, +10, +10, +15, +15, +20, +10]
SEASON_MID  = [-20, -15,  -5,   0,  +5, +10, +20, +15, +10,   0]
SEASON_HIGH = [-20, -10,   0, +10, +20, +30, +40, +50, +30, +20]

SEASON_PATTERNS = {"low": SEASON_LOW, "mid": SEASON_MID, "high": SEASON_HIGH}

# ── FESTIVALS ────────────────────────────────────────────────
# (good, month_index, festival_name, boost_type)
# boost_type maps to FESTIVAL_BOOST amounts below
# month after festival the good's base price drops by same amount

FESTIVAL_BOOST = {"low": 25, "mid": 35, "high": 50}

PLANET_FESTIVALS = {
    "Terra":       ("Cinnamon", 2, "Cinnamon Roll Festival",  "low"),
    "Zeta-9":      ("Ginger",   5, "Golden Ginger Gala",      "mid"),
    "Void Colony": ("Vanilla",  7, "Void Vanilla Vigil",      "mid"),
    "Agrica":      ("Paprika",  3, "Paprika Panic Parade",    "low"),
    "Nexus":       ("Allspice", 9, "Allspice Arbitrage Fête", "high"),
}

# ── PLANETS ───────────────────────────────────────────────────
# production price = fixed cheap local price (frozen, never drifts)
# demand price = fixed high local price (frozen, never drifts)
# neutral good prices drift each turn within GOOD_DATA bounds

planets_template = {
    "Terra": {
        "production": "Cinnamon",
        "demand":     "Allspice",
        "spices": ["Cinnamon","Cardamom","Vanilla","Allspice","Clove","Paprika","Ginger"],
        "base_prices": {
            "Cinnamon": 25, "Cardamom": 100, "Vanilla": 90,
            "Allspice": 120, "Clove": 70, "Paprika": 50, "Ginger": 70,
        },
    },
    "Zeta-9": {
        "production": "Saffron",
        "demand":     "Ginger",
        "spices": ["Saffron","Turmeric","Paprika","Ginger","Nutmeg","Cinnamon"],
        "base_prices": {
            "Saffron": 100, "Turmeric": 50, "Paprika": 60,
            "Ginger": 90, "Nutmeg": 135, "Cinnamon": 40,
        },
    },
    "Void Colony": {
        "production": "Void Pepper",
        "demand":     "Cardamom",
        "spices": ["Void Pepper","Saffron","Ginger","Cardamom","Clove","Vanilla"],
        "base_prices": {
            "Void Pepper": 500, "Saffron": 200, "Ginger": 65,
            "Cardamom": 80, "Clove": 40, "Vanilla": 100,
        },
    },
    "Agrica": {
        "production": "Paprika",
        "demand":     "Vanilla",
        "spices": ["Paprika","Cinnamon","Turmeric","Vanilla","Allspice","Cardamom","Nutmeg"],
        "base_prices": {
            "Paprika": 30, "Cinnamon": 50, "Turmeric": 30,
            "Vanilla": 120, "Allspice": 80, "Cardamom": 60, "Nutmeg": 100,
        },
    },
    "Nexus": {
        "production": "Clove",
        "demand":     "Turmeric",
        "spices": ["Clove","Void Pepper","Nutmeg","Saffron","Turmeric","Allspice"],
        "base_prices": {
            "Clove": 35, "Void Pepper": 750, "Nutmeg": 110,
            "Saffron": 175, "Turmeric": 40, "Allspice": 90,
        },
    },
}

# ── UPGRADES DATA ─────────────────────────────────────────────
# Logic (apply functions) lives in game.py as UPGRADE_EFFECTS.
# This dict contains only balance-relevant fields: name, cost, planet, desc.

UPGRADES_DATA = {
    "kinetic_launcher":  {"name": "Kinetic Launcher",         "cost": 2000, "planet": None,          "desc": "Weapon+1. A classic."},
    "mining_laser":      {"name": "Mining Laser",             "cost": 1000, "planet": "Zeta-9",      "desc": "Weapon+1. Cuts ore and pirates equally well."},
    "void_torpedo":      {"name": "Void Torpedo",             "cost": 5000, "planet": "Void Colony", "desc": "Weapon+2. Extremely illegal elsewhere."},
    "stern_tank":        {"name": "Stern Tank",               "cost": 1000, "planet": None,          "desc": "+200 fuel capacity."},
    "portside_tank":     {"name": "Portside Tank",            "cost": 2000, "planet": None,          "desc": "+300 fuel capacity."},
    "cylindrical_tank":  {"name": "Cylindrical Tank",         "cost": 3000, "planet": None,          "desc": "+500 fuel capacity."},
    "small_hold":        {"name": "Small Hold",               "cost": 1000, "planet": None,          "desc": "+100 cargo capacity."},
    "side_hold":         {"name": "Side Hold",                "cost": 2000, "planet": "Terra",       "desc": "+100 cargo capacity. Terra exclusive."},
    "grain_silo":        {"name": "Grain Silo",               "cost": 3000, "planet": "Agrica",      "desc": "+200 cargo capacity. Agrica exclusive."},
    "broker_license":    {"name": "Galactic Broker License",  "cost": 1000, "planet": "Nexus",       "desc": "Unlock live price-check across all planets."},
    "passenger_quoters": {"name": "Passenger Quoters",        "cost": 1000, "planet": None,          "desc": "Unlock 1 passenger slot."},
    "long_range_radar":  {"name": "Long Range Radar",         "cost": 3000, "planet": "Terra",       "desc": "-15% pirate encounter chance. Terra exclusive."},
    "booster":           {"name": "Booster",                  "cost": 1000, "planet": "Void Colony", "desc": "Flee costs 5×angst fuel instead of 20×. Void Colony only."},
}

# ── PIRATES ───────────────────────────────────────────────────
PIRATE_BASE_CHANCE    = 0.25   # per jump
PIRATE_RADAR_CHANCE   = 0.10   # per jump with Long Range Radar
PIRATE_START_ANGST    = 10
PIRATE_START_BRIBE    = 100    # credits; +100 per successful bribe use
PIRATE_FLEE_MULT      = 20     # fuel cost = FLEE_MULT * angst
PIRATE_FLEE_MULT_BOOST= 5      # fuel cost with Booster installed
PIRATE_BOUNTY_PER_ANGST = 100  # bounty = this * angst on superior fight

# ── PASSENGERS ───────────────────────────────────────────────
PASSENGER_SPAWN_CHANCE = 0.20  # per planet arrival or cantina rest
PASSENGER_DELIVERY_PAY = 300   # credits on successful delivery

# ── TRAVEL EVENTS (non-pirate) ───────────────────────────────
# (probability, event_key) — handled in game.py
TRAVEL_EVENT_PROBS = {
    "festival":      0.12,
    "fuel_leak":     0.10,
    "mystery_cargo": 0.08,
}
FUEL_LEAK_MIN        = 15
FUEL_LEAK_MAX        = 35
MYSTERY_CARGO_AMOUNT = 5

# ── FARM ─────────────────────────────────────────────────────
FARM_COST    = 10000
FARM_PLANET  = "Terra"

# ── CONCERT ──────────────────────────────────────────────────
CONCERT_TICKET = 10

# ── TAXES ────────────────────────────────────────────────────
SALE_TAX_RATE = 0.02   # 2% of gross sale value
SALE_TAX_MIN  = 1      # minimum tax per transaction

# ── STOCKPILES ───────────────────────────────────────────────
# Maximum stockpile size per price category
STOCKPILE_MAX   = {"low": 500, "mid": 300, "high": 100}
# Starting stockpile (roughly half of max — hand-mod per planet below)
STOCKPILE_START = {"low": 250, "mid": 150, "high":  50}

# Stockpile pressure on prices — applied after drift each turn
# If stockpile < LOW_THRESHOLD * max  → price rises by PRESSURE amount
# If stockpile > HIGH_THRESHOLD * max → price drops by PRESSURE amount
STOCKPILE_LOW_THRESHOLD  = 0.20
STOCKPILE_HIGH_THRESHOLD = 0.80
STOCKPILE_PRESSURE       = {"low": 5, "mid": 10, "high": 20}

# Per-planet starting stockpile overrides.
# Key: (planet_name, good) → starting amount.
# If not listed here, STOCKPILE_START[category] is used.
# Hand-mod this to create interesting starting conditions.
STOCKPILE_OVERRIDES = {
    # ("Void Colony", "Void Pepper"): 10,   # example: start very scarce
    # ("Nexus", "Void Pepper"):       5,    # example: nearly dry at Nexus
}

# ── PRODUCTION ───────────────────────────────────────────────
# Base production added to stockpile during harvest month, per price category.
# Only on planets that carry the good.
PRODUCTION_BASE = {"low": 64, "mid": 32, "high": 16}

# Multiplier if planet is the PRODUCTION planet for that good
PRODUCTION_HOME_MULT = 3.0

# Multiplier if stockpile is literally 0 at time of production (generous harvest)
PRODUCTION_ZERO_MULT = 1.5

# ── CONSUMPTION ──────────────────────────────────────────────
# Units consumed per month per planet that carries the good.
CONSUMPTION_BASE = {"low": 7, "mid": 4, "high": 2}

# Multiplier if planet is the DEMAND planet for that good
CONSUMPTION_DEMAND_MULT = 2.0

# Multiplier if stockpile >= HIGH_THRESHOLD (abundance drives extra use)
# Stacks with demand multiplier — max effective multiplier = 4×
CONSUMPTION_OVERFLOW_MULT = 2.0

# ── VOID PEPPER SPECIAL ──────────────────────────────────────
# Void Pepper has no standard harvest season.
# It gets a fixed annual production event and fixed consumption.
VOID_PEPPER_PRODUCTION_MONTH  = 9        # month index 9 = Dedl (10th month)
VOID_PEPPER_PRODUCTION_AMOUNT = 30       # units produced on Void Colony only
VOID_PEPPER_CONSUMPTION = {              # units consumed per month per planet
    "Void Colony": 2,
    "Nexus":       4,
}

# ── LOCAL MARKET ─────────────────────────────────────────────
# 5 independent trader slots rolled fresh on each planet arrival.
# Traders operate outside local stockpile — goods from the void.
LOCAL_MARKET_SLOTS    = 5
# Quantity available per slot, by price category
LOCAL_MARKET_QTY      = {"low": 20, "mid": 10, "high": 5}
# Price = sell_price + spread_amount ± random(0, LOCAL_MARKET_VARIANCE)
LOCAL_MARKET_VARIANCE = {"low": 5, "mid": 10, "high": 15}
# Mystery Crate excluded from local market rolls
LOCAL_MARKET_EXCLUDE  = {"Mystery Crate"}

# ── FLEET SUPPLY DEPOT ───────────────────────────────────────
# Terra-only. Sell-only. Fixed prices. No stockpile — goods vanish on sale.
# Prices are set as a guaranteed floor dump valve for the galaxy.
# Cinnamon is special (produced on Terra) so its depot price is slightly higher.
FLEET_DEPOT_PLANET = "Terra"
FLEET_DEPOT_PRICES = {
    "Cinnamon":    21,
    "Turmeric":    28,
    "Paprika":     31,
    "Ginger":      39,
    "Clove":       42,
    "Vanilla":     45,
    "Cardamom":    48,
    "Allspice":    56,
    "Saffron":     65,
    "Nutmeg":      62,
    "Void Pepper": 170,
}

# ── RANDOMISED START BOUNDS ──────────────────────────────────
# Applied once on new game only (not on load).
# Stockpile random range: [RAND_STK_LOW_FRAC, RAND_STK_HIGH_FRAC] × stockpile_max
# Price random range:     [min_price, RAND_PRICE_HIGH_MULT × default_price]
# Final value = mean(random_value, parameter_value), then clamped.
# Price clamped to [RAND_PRICE_MIN_FRAC × default, RAND_PRICE_MAX_FRAC × default]
# and also always within GOOD_DATA [min, max].
RAND_STK_LOW_FRAC   = 0.25
RAND_STK_HIGH_FRAC  = 0.75
RAND_PRICE_HIGH_MULT = 2.0
RAND_PRICE_MIN_FRAC  = 0.30
RAND_PRICE_MAX_FRAC  = 3.00

# ── RANDOM EVENTS ────────────────────────────────────────────
# Fired on planet arrival and cantina rest (both = 1 month passing).
# RND_EVENT_SPLIT: probability the fired event is an impact event.
# Remaining probability draws from the blank (flavour-only) pool.
RND_EVENT_SPLIT = 0.20   # 20% impact, 80% blank
