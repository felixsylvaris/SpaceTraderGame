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
    "mining_drones":  False,
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
    # ── Industrial goods — no harvest, produced every month ──
    "Minerals":      ("low",     24,    80,   240),
    "Soybeans":      ("low",     18,    60,   180),
    "Alloys":        ("mid",     36,   120,   360),
    "Robots":        ("mid",     48,   160,   480),
    "Weapons":       ("high",    60,   200,   600),
    "Medicine":      ("high",    90,   300,   900),
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
    # Industrial goods — no harvest cycle
    "Minerals":      None,
    "Soybeans":      None,
    "Alloys":        None,
    "Robots":        None,
    "Weapons":       None,
    "Medicine":      None,
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
# production     = spice produced here (◀ SPICE marker, frozen price)
# demand         = spice in demand here (▶ DEMAND marker, frozen price)
# ind_production = industrial goods produced here (◀ INDUSTRY marker)
# goods          = all goods available on this planet (spices + industrials)
# base_prices    = starting base prices for all goods

planets_template = {
    "Terra": {
        "production":     "Cinnamon",
        "demand":         "Allspice",
        "ind_production": ["Weapons", "Robots"],
        "goods": [
            "Cinnamon","Cardamom","Vanilla","Allspice","Clove","Paprika","Ginger",
            "Alloys","Weapons","Robots","Medicine",
        ],
        "base_prices": {
            "Cinnamon": 25,  "Cardamom": 100, "Vanilla": 90,
            "Allspice": 120, "Clove": 70,     "Paprika": 50,  "Ginger": 70,
            "Alloys":   120, "Weapons": 200,  "Robots":  160, "Medicine": 300,
        },
    },
    "Zeta-9": {
        "production":     "Saffron",
        "demand":         "Ginger",
        "ind_production": ["Alloys"],
        "goods": [
            "Saffron","Turmeric","Paprika","Ginger","Nutmeg","Cinnamon",
            "Minerals","Alloys","Robots","Soybeans",
        ],
        "base_prices": {
            "Saffron": 100, "Turmeric": 50, "Paprika": 60,
            "Ginger":  90,  "Nutmeg":  135, "Cinnamon": 40,
            "Minerals": 80, "Alloys":  120, "Robots":  160, "Soybeans": 60,
        },
    },
    "Void Colony": {
        "production":     "Void Pepper",
        "demand":         "Cardamom",
        "ind_production": ["Minerals"],
        "goods": [
            "Void Pepper","Saffron","Ginger","Cardamom","Clove","Vanilla",
            "Minerals","Weapons","Medicine","Robots",
        ],
        "base_prices": {
            "Void Pepper": 500, "Saffron": 200, "Ginger": 65,
            "Cardamom": 80,     "Clove": 40,    "Vanilla": 100,
            "Minerals": 80,     "Weapons": 200, "Medicine": 300, "Robots": 160,
        },
    },
    "Agrica": {
        "production":     "Paprika",
        "demand":         "Vanilla",
        "ind_production": ["Soybeans"],
        "goods": [
            "Paprika","Cinnamon","Turmeric","Vanilla","Allspice","Cardamom","Nutmeg",
            "Soybeans","Weapons","Robots",
        ],
        "base_prices": {
            "Paprika": 30,  "Cinnamon": 50, "Turmeric": 30,
            "Vanilla": 120, "Allspice": 80, "Cardamom": 60, "Nutmeg": 100,
            "Soybeans": 60, "Weapons": 200, "Robots":  160,
        },
    },
    "Nexus": {
        "production":     "Clove",
        "demand":         "Turmeric",
        "ind_production": ["Medicine"],
        "goods": [
            "Clove","Void Pepper","Nutmeg","Saffron","Turmeric","Allspice",
            "Alloys","Soybeans","Medicine",
        ],
        "base_prices": {
            "Clove": 35,     "Void Pepper": 750, "Nutmeg": 110,
            "Saffron": 175,  "Turmeric": 40,     "Allspice": 90,
            "Alloys": 120,   "Soybeans": 60,     "Medicine": 300,
        },
    },
}

# ── UPGRADES DATA ─────────────────────────────────────────────
# Logic (apply functions) lives in game.py as UPGRADE_EFFECTS.
# This dict contains only balance-relevant fields: name, cost, planet, desc.

UPGRADES_DATA = {
    "kinetic_launcher":  {"name": "Kinetic Launcher",         "cost": 2000, "planet": None,          "desc": "Weapon+1. A classic."},
    "mining_laser":      {"name": "Mining Laser",             "cost": 1000, "planet": "Zeta-9",      "desc": "Weapon+1. Required for asteroid mining."},
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
    "mining_drones":     {"name": "Mining Drones",            "cost":10000, "planet": "Zeta-9",      "desc": "Mine entire asteroid field in 1 month. Zeta-9 only."},
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

# ── INDUSTRIAL GOODS ─────────────────────────────────────────
# Industrial goods are produced every month (no harvest season).
# Single production planet per good. No home multiplier — just flat output.

# Base monthly production on the production planet only
INDUSTRIAL_PRODUCTION = {
    "Minerals": 8,
    "Soybeans": 8,
    "Alloys":   4,
    "Robots":   4,
    "Weapons":  2,
    "Medicine": 2,
}

# Monthly consumption per planet that carries the good.
# Explicit per-good rates — does not use CONSUMPTION_BASE.
INDUSTRIAL_CONSUMPTION = {
    "Minerals": 4,
    "Soybeans": 4,
    "Alloys":   2,
    "Robots":   2,
    "Weapons":  2,
    "Medicine": 2,
}

# Cross-good production bonus rules.
# (trigger_planet, trigger_good, threshold, target_planet, target_good, multiplier)
# If trigger_good stockpile at trigger_planet >= threshold fraction → multiply target production.
INDUSTRIAL_BONUS_RULES = [
    ("Void Colony", "Minerals", 0.50, "Zeta-9",       "Alloys",   2.0),
    ("Zeta-9",      "Alloys",   0.50, "Terra",         "Weapons",  2.0),
    ("Terra",       "Weapons",  0.50, "Agrica",        "Soybeans", 2.0),  # kill bugs → farm more
    ("Terra",       "Robots",   0.50, "Agrica",        "Soybeans", 2.0),  # robots harvest fields
    ("Terra",       "Robots",   0.50, "Void Colony",   "Minerals", 2.0),  # robots mine
    ("Terra",       "Robots",   0.50, "Zeta-9",        "Alloys",   2.0),  # robots smelt
]

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
    # Spices
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
    # Industrial goods — min_price + spread + 5 (Weapons/Robots +1 only, made on Terra)
    "Minerals":    34,   # 24 + 5 + 5
    "Soybeans":    28,   # 18 + 5 + 5
    "Alloys":      51,   # 36 + 10 + 5
    "Medicine":    110,  # 90 + 15 + 5
    "Weapons":     76,   # 60 + 15 + 1  (Terra production)
    "Robots":      59,   # 48 + 10 + 1  (Terra production)
}

# ── INDEPENDENT TRADER ───────────────────────────────────────
# Fires at end of each month cycle, after all price/stockpile adjustments.
# Scans planet pairs, finds best arbitrage good, moves stock between planets.
IND_TR_CHANCE      = 0.30   # probability independent trader activates this month
IND_TR_SKIP_CHANCE = 0.30   # probability to skip each individual planet pair
# Units moved per trade, by price category (high-price planet receives this amount)
IND_TR_VOLUME      = {"low": 40, "mid": 20, "high": 10}
IND_TR_PRICE_NUDGE = 5      # base_price shift applied to both planets after trade

# ── MINING OPERATIONS ────────────────────────────────────────
# Asteroid fields spawn at Zeta-9 and Void Colony on month 0 (Ianu) each year.
# Field size is random in [MINE_FIELD_MIN, MINE_FIELD_MAX].
# Fields reset each new year — unclaimed ore is taken by someone else.
MINE_PLANETS       = ["Zeta-9", "Void Colony"]
MINE_FIELD_MIN     = 10
MINE_FIELD_MAX     = 100
MINE_PER_MONTH     = 10     # minerals extracted per month of mining (without drones)

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

# ── CHARACTER SHEET ──────────────────────────────────────────
# Separate from ship state. Persists across all expeditions and sessions.
# Stats are numeric. Equipment is a list of purchased item keys.

CHAR_START = {
    "stats": {
        "power":      0,
        "science":    0,
        "medicine":   0,
        "perception": 0,
        "agility":    0,
        "health":     3,
        "supply":     0,
        "cargo":      1,
    },
    "equipment":      [],   # list of purchased equipment keys
    "easy_job_token": 1,    # attempts remaining for Easy Job mission
}

# ── CHARACTER EQUIPMENT SHOP ─────────────────────────────────
# Sold at Expedition Center on Agrica. Bought once. Permanent.
# effects: applied to character["stats"] on purchase.

CHAR_EQUIPMENT = {
    "guns": {
        "name":    "Guns",
        "cost":    1000,
        "desc":    "A trusty sidearm. Adds authority to negotiations.",
        "effects": {"power": 1},
    },
    "body_armor": {
        "name":    "Body Armor",
        "cost":    2000,
        "desc":    "Plates and padding. You feel heavier but safer.",
        "effects": {"power": 1, "health": 2},
    },
    "med_kit": {
        "name":    "Med Kit",
        "cost":    2000,
        "desc":    "Field surgery supplies. Solid foam sealant, fake skin, stimulants.",
        "effects": {"medicine": 2, "science": 1},
    },
    "scout_drone": {
        "name":    "Scout Drone",
        "cost":    3000,
        "desc":    "Quiet little flier. Sees what you can't.",
        "effects": {"perception": 3},
    },
    "bodyguard": {
        "name":    "Hire Bodyguard",
        "cost":    5000,
        "desc":    "A scarred mercenary who has seen worse. Much worse.",
        "effects": {"power": 3, "health": 3, "agility": 1, "perception": 1},
    },
    "jet_pack": {
        "name":    "Jet Pack",
        "cost":    2000,
        "desc":    "Short-burst propulsion. Great for escaping. Or arriving dramatically.",
        "effects": {"agility": 2},
    },
}
