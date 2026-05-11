"""
=============================================================
  SPICE SPACE TRADER  —  Changelog
=============================================================

v8  (current)
  + Date & Calendar: turn, month (10-month year), year 2201
    Month names: Ianu Febu Mari Aprix Maiu Iuin Septr Octo Nova Dedl
    Travel and cantina rest both advance month+turn
  + Extra Goods: each good now on 3 planets
    Zeta-9 +Cinnamon(40), Agrica +Cardamom(60), Void Colony +Vanilla(100)
    Nexus +Allspice(90), Terra +Paprika(50), Agrica +Nutmeg(100), Terra +Ginger(70)
  + Death and Taxes: 2% tax on every sale, min 1cr, rounded up
  + Inflation: each turn, neutral good prices drift ±1-10 / ±1-9, floor 10
    Production and Demand prices remain frozen
  + Galaxy Harvest Season: each good has a harvest month and seasonal pattern
    Low / Mid / High patterns; Void Pepper has no season
  + Pumpkin Latte Festival: each planet has one annual festival month+good
    Low +50cr spike, Mid +100cr spike; post-festival drop next month
    5 flavour bartender tips about festivals added to advice pool
  + Engineering Bay: Fuel Up, Drain Fuel, Upgrades
    FUEL_PRICE global (1cr/unit); min 50 fuel to leave port
    Drain options: 100/200/500/1000/90% — cannot drain below 50
  + Ship Upgrades (bought once, some planet-locked):
    Kinetic Launcher, Mining Laser (Zeta-9), Void Torpedo (Void Colony)
    Stern/Portside/Cylindrical tanks (+fuel cap)
    Small Hold, Side Hold (Terra), Grain Silo (Agrica) (+cargo)
    Broker License (Nexus) — unlocks price_check
    Passenger Quoters — unlocks passenger slot
    Long Range Radar (Terra) — -15% pirate chance
    Booster (Void Colony) — flee cost 5×angst instead of 20×angst
  + Galactic Broker License gate on price_check
  + Passenger mechanic: 20% spawn per planet visit / cantina rest
    One slot; Whitemaine the Pride Mercenary implemented
    Cantina shows traveler status; deliver for +300cr
  + Pirate Encounters overhauled:
    25% base chance (-15% with radar); piratangst runtime, piratbribe runtime
    Options: Fight / Flee / Bribe / Drop Cargo / Bluff / Surrender(GAME OVER)
    Fight compares weapons vs Max(1, angst//20)
    Bribe persists and rises +100 each use
    Flee cost 20×angst (5×angst with Booster), capped at fuel-50
    Bounty on superior fight: 100×angst
  + Cheat code: type "!credits N" at action prompt for N credits (silent)
  + Save/Load updated to persist all new state

v7
  + requests hook for remote RNG seed
  + Event system dict-driven (no string parsing)
  + Fuel and cargo separated
  + Infinite recursion fixed (farm, cantina)
  + Input validation _get_int() everywhere
  + price_check columnar formatting
  + save_game / load_game JSON
  + Distance-based travel fuel costs
  + Galaxy background story queue

v6  (original public version)
  Basic trading loop, cantina, farm win condition
=============================================================
"""

import random
import json
import math
import os

try:
    import requests as _requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

SAVE_FILE = "spice_trader_save.json"
FUEL_PRICE = 1          # credits per fuel unit — global so OPEC crisis is one line
MIN_FUEL_TO_DEPART = 50 # can't leave port below this

# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

MONTH_NAMES = ["Ianu", "Febu", "Mari", "Aprix", "Maiu",
               "Iuin", "Septr", "Octo", "Nova", "Dedl"]
MONTHS_PER_YEAR = 10


def month_name(month_index: int) -> str:
    """month_index is 0-based internally."""
    return MONTH_NAMES[month_index % MONTHS_PER_YEAR]


def advance_time(state: dict, months: int = 1):
    """Advance turn, month, year. Returns nothing — mutates state."""
    for _ in range(months):
        state["turn"] += 1
        state["month_index"] += 1
        if state["month_index"] >= MONTHS_PER_YEAR:
            state["month_index"] = 0
            state["year"] += 1
    apply_inflation(state)
    check_festival_drop(state)


def date_str(state: dict) -> str:
    return f"{month_name(state['month_index'])} {state['year']}"


# ═══════════════════════════════════════════════════════════════════════════════
# REMOTE SEED (requests hook)
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_remote_seed() -> int:
    if not REQUESTS_AVAILABLE:
        return random.randint(0, 99)
    try:
        resp = _requests.get(
            "https://www.randomnumberapi.com/api/v1.0/random?min=0&max=99&count=1",
            timeout=2,
        )
        resp.raise_for_status()
        return resp.json()[0]
    except Exception:
        return random.randint(0, 99)


# ═══════════════════════════════════════════════════════════════════════════════
# HARVEST SEASONS & FESTIVALS
# ═══════════════════════════════════════════════════════════════════════════════

# Seasonal offset pattern (index 0 = harvest month, index 5 = anti-harvest)
SEASON_LOW  = [0, 0, +5, +5, +10, +10, +15, +15, +20, +10]
SEASON_MID  = [-20, -15, -5, 0, +5, +10, +20, +15, +10, 0]
SEASON_HIGH = [-20, -10, 0, +10, +20, +30, +40, +50, +30, +20]

# Each good: (harvest_month_index, pattern_key)
# Void Pepper has no season (None)
GOOD_SEASONS = {
    "Cinnamon":   (0,  "low"),   # harvest Ianu
    "Turmeric":   (1,  "low"),   # harvest Febu
    "Paprika":    (2,  "mid"),   # harvest Mari
    "Ginger":     (3,  "mid"),   # harvest Aprix
    "Clove":      (4,  "mid"),   # harvest Maiu
    "Vanilla":    (5,  "mid"),   # harvest Iuin
    "Cardamom":   (6,  "mid"),   # harvest Septr
    "Allspice":   (7,  "high"),  # harvest Octo
    "Saffron":    (8,  "high"),  # harvest Nova
    "Nutmeg":     (9,  "high"),  # harvest Dedl
    "Void Pepper": None,
    "Mystery Crate": None,
}

SEASON_PATTERNS = {"low": SEASON_LOW, "mid": SEASON_MID, "high": SEASON_HIGH}

FESTIVAL_BOOST  = {"low": 50, "mid": 100}

# Planet festivals: (good, month_index, festival_name, boost_type)
PLANET_FESTIVALS = {
    "Terra":       ("Cinnamon",   2, "Cinnamon Roll Festival",   "low"),
    "Zeta-9":      ("Ginger",     5, "Golden Ginger Gala",       "mid"),
    "Void Colony": ("Vanilla",    7, "Void Vanilla Vigil",       "mid"),
    "Agrica":      ("Paprika",    3, "Paprika Panic Parade",     "mid"),
    "Nexus":       ("Allspice",   9, "Allspice Arbitrage Fête",  "low"),
}


def season_offset(good: str, current_month: int) -> int:
    """Return the seasonal price modifier for a good in the current month."""
    entry = GOOD_SEASONS.get(good)
    if entry is None:
        return 0
    harvest_month, pattern_key = entry
    pattern = SEASON_PATTERNS[pattern_key]
    offset_index = (current_month - harvest_month) % MONTHS_PER_YEAR
    return pattern[offset_index]


def festival_boost_this_month(planet_name: str, current_month: int) -> tuple:
    """Returns (good, boost) if there's a festival this month, else (None, 0)."""
    if planet_name not in PLANET_FESTIVALS:
        return None, 0
    good, fest_month, _name, boost_type = PLANET_FESTIVALS[planet_name]
    if current_month == fest_month:
        return good, FESTIVAL_BOOST[boost_type]
    return None, 0


def check_festival_drop(state: dict):
    """
    The month after a festival the price drops by the same amount.
    We track last_festival_drop to apply it once.
    """
    m = state["month_index"]
    for planet_name, (good, fest_month, _name, boost_type) in PLANET_FESTIVALS.items():
        drop_month = (fest_month + 1) % MONTHS_PER_YEAR
        if m == drop_month:
            drop_key = f"{planet_name}_{good}_dropped_{state['year']}"
            if drop_key not in state["festival_drops_applied"]:
                state["festival_drops_applied"].add(drop_key)
                planet = state["planets"][planet_name]
                if good in planet["base_prices"]:
                    boost = FESTIVAL_BOOST[boost_type]
                    planet["base_prices"][good] = max(
                        10, planet["base_prices"][good] - boost
                    )


# ═══════════════════════════════════════════════════════════════════════════════
# INFLATION
# ═══════════════════════════════════════════════════════════════════════════════

def apply_inflation(state: dict):
    """Drift all neutral good prices by ±1-10/±1-9 per turn. Floor 10."""
    planets = state["planets"]
    for planet_name, planet in planets.items():
        prod = planet["production"]
        dem  = planet["demand"]
        for good in list(planet["base_prices"].keys()):
            if good in (prod, dem):
                continue  # frozen
            if random.random() < 0.5:
                delta = random.randint(1, 10)
            else:
                delta = -random.randint(1, 9)
            planet["base_prices"][good] = max(10, planet["base_prices"][good] + delta)


# ═══════════════════════════════════════════════════════════════════════════════
# EFFECTIVE PRICE (season + festival applied on read)
# ═══════════════════════════════════════════════════════════════════════════════

def effective_price(state: dict, planet_name: str, good: str) -> int:
    """
    Returns the price a player actually sees and pays/receives.
    Base price + seasonal offset + festival boost if applicable.
    Never below 1.
    """
    planet = state["planets"][planet_name]
    base = planet["base_prices"].get(good, 1)

    # Season (applies to all goods with a season; production/demand included for flavour
    # but production/demand base prices are frozen — season still shifts effective price)
    season = season_offset(good, state["month_index"])

    # Festival
    fest_good, fest_boost = festival_boost_this_month(planet_name, state["month_index"])
    festival = fest_boost if good == fest_good else 0

    return max(1, base + season + festival)


# ═══════════════════════════════════════════════════════════════════════════════
# PLANET & GAME DATA
# ═══════════════════════════════════════════════════════════════════════════════

PLANET_NAMES = ["Terra", "Zeta-9", "Void Colony", "Agrica", "Nexus"]

planets_template = {
    "Terra": {
        "production": "Cinnamon",
        "demand":     "Allspice",
        "spices": ["Cinnamon", "Cardamom", "Vanilla", "Allspice", "Clove",
                   "Paprika", "Ginger"],
        "base_prices": {
            "Cinnamon": 25, "Cardamom": 100, "Vanilla": 90,
            "Allspice": 100, "Clove": 70, "Paprika": 50, "Ginger": 70,
        },
    },
    "Zeta-9": {
        "production": "Saffron",
        "demand":     "Ginger",
        "spices": ["Saffron", "Turmeric", "Paprika", "Ginger", "Nutmeg", "Cinnamon"],
        "base_prices": {
            "Saffron": 100, "Turmeric": 50, "Paprika": 60,
            "Ginger": 90, "Nutmeg": 135, "Cinnamon": 40,
        },
    },
    "Void Colony": {
        "production": "Void Pepper",
        "demand":     "Cardamom",
        "spices": ["Void Pepper", "Saffron", "Ginger", "Cardamom", "Clove", "Vanilla"],
        "base_prices": {
            "Void Pepper": 500, "Saffron": 200, "Ginger": 65,
            "Cardamom": 80, "Clove": 70, "Vanilla": 100,
        },
    },
    "Agrica": {
        "production": "Paprika",
        "demand":     "Vanilla",
        "spices": ["Paprika", "Cinnamon", "Turmeric", "Vanilla", "Allspice",
                   "Cardamom", "Nutmeg"],
        "base_prices": {
            "Paprika": 30, "Cinnamon": 50, "Turmeric": 30,
            "Vanilla": 120, "Allspice": 80, "Cardamom": 60, "Nutmeg": 100,
        },
    },
    "Nexus": {
        "production": "Clove",
        "demand":     "Turmeric",
        "spices": ["Clove", "Void Pepper", "Nutmeg", "Saffron", "Turmeric", "Allspice"],
        "base_prices": {
            "Clove": 35, "Void Pepper": 750, "Nutmeg": 110,
            "Saffron": 175, "Turmeric": 40, "Allspice": 90,
        },
    },
}

cantinas = {
    "Terra":       {"name": "The Cinnamon Tavern",  "drink": {"name": "Cinnamon Beer",       "ingredient": "Cinnamon",   "fluff": ["The warm beer tastes like home.", "Sweet, spicy—exactly what you needed.", "The bartender winks. 'Terra's finest.'"]}},
    "Zeta-9":      {"name": "The Golden Saffron",   "drink": {"name": "Saffron Mead",         "ingredient": "Saffron",    "fluff": ["Golden and rich. Liquid sunlight.", "The glass might actually be gold.", "You feel fancy. The bartender smirks."]}},
    "Void Colony": {"name": "The Pepper's Shadow",  "drink": {"name": "Void Pepper Whiskey",  "ingredient": "Void Pepper","fluff": ["Burns like a supernova. You see stars.", "Rumoured to power small starships.", "One sip: forget your name. Two: forget your debts."]}},
    "Agrica":      {"name": "The Paprika Den",       "drink": {"name": "Spiced Paprika Ale",   "ingredient": "Paprika",    "fluff": ["Fiery and bold. You cough. Worth it.", "The bartender: 'House special. Last season's best.'", "You feel warmer immediately."]}},
    "Nexus":       {"name": "The Clove & Dagger",   "drink": {"name": "Clove Rum",            "ingredient": "Clove",      "fluff": ["Smooth but packs a punch.", "On the house—if you say where you got that Void Pepper.", "Complex, like every deal made here."]}},
}

advice_pools = {
    "game": [
        "Buy low, sell high. Simple in theory. The galaxy complicates it.",
        "Weapons are expensive. Losing cargo to pirates is more expensive.",
        "Not all pirates are worth fighting. Running away is also valid.",
        "Nexus bankers are high on Void Pepper. They pay anything for a fix.",
        "Bad trades won't block future good ones.",
        "Upgrading your ship opens options you couldn't imagine before.",
    ],
    "divorced": [
        "Never date a Psionic Girl. Judged by thoughts, not words.",
        "If you see a Space Whale, feast your eyes. It may never happen again.",
        "Don't drink a hold full of Void Whiskey in one night.",
        "There is no grand destiny. Only semi-random dice. Make your own.",
    ],
    "iroh": [
        "Wide horizons reveal opportunities invisible on stable routes.",
        "Life happens whether you manage it or not. Make it cozy.",
        "Bad trades happen. Let go of pride. Trading in anger makes it worse.",
        "Leave spare cargo space. Surprise opportunities are real.",
        "A good ship and a few credits already puts you ahead of many.",
    ],
    "festival": [
        "During the Cinnamon Roll Festival on Terra in Mari, prices spike hard. "
        "They bake a thirty-metre cinnamon roll and roll it down the main street. "
        "The cleanup takes all of Aprix.",

        "Zeta-9's Golden Ginger Gala in Iuin is wild. Traders dress as giant ginger roots "
        "and race hovercarts through the market district. First prize is a barrel of Saffron Mead.",

        "The Void Vanilla Vigil on Void Colony every Octo is technically a funeral. "
        "For the harvest. They bury a vanilla pod in a zero-G chamber and everyone weeps. "
        "Vanilla prices go insane. The bartender always cries telling this story.",

        "Agrica's Paprika Panic Parade in Aprix: they stuff a giant dummy of a tentacle monster "
        "with paprikas and beat it with plasma hammers until it explodes. "
        "Children scramble for the spice shrapnel. Very traditional.",

        "Nexus hosts the Allspice Arbitrage Fête every Dedl. Brokers in formal wear outbid each other "
        "on rare allspice futures while drunk on Clove Rum. "
        "The prices crash spectacularly the next month. Everyone pretends this is surprising.",
    ],
}

galaxy_story = [
    "A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle.",
    "A rogue freighter with 10,000 units of Void Pepper vanished near Nexus. No trace.",
    "A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.",
    "AGRICA DROUGHT — paprika yields expected to halve next season.",
    "The old Void Colony governor was arrested. The new one is... friendlier to black-market deals.",
    "The jump lanes near Terra are being taxed now. Change is coming.",
    "The galaxy feels different lately. The old routes are shifting.",
]

# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADES
# ═══════════════════════════════════════════════════════════════════════════════

UPGRADES = {
    "kinetic_launcher": {
        "name": "Kinetic Launcher", "cost": 2000, "planet": None,
        "desc": "Weapon+1. A classic.",
        "apply": lambda ship: ship.update({"weapons": ship["weapons"] + 1}),
    },
    "mining_laser": {
        "name": "Mining Laser", "cost": 1000, "planet": "Zeta-9",
        "desc": "Weapon+1. Cuts ore and pirates equally well.",
        "apply": lambda ship: ship.update({"weapons": ship["weapons"] + 1}),
    },
    "void_torpedo": {
        "name": "Void Torpedo", "cost": 5000, "planet": "Void Colony",
        "desc": "Weapon+1. Void Colony special. Extremely illegal elsewhere.",
        "apply": lambda ship: ship.update({"weapons": ship["weapons"] + 1}),
    },
    "stern_tank": {
        "name": "Stern Tank", "cost": 1000, "planet": None,
        "desc": "+200 fuel capacity.",
        "apply": lambda ship: ship.update({"max_fuel": ship["max_fuel"] + 200}),
    },
    "portside_tank": {
        "name": "Portside Tank", "cost": 2000, "planet": None,
        "desc": "+300 fuel capacity.",
        "apply": lambda ship: ship.update({"max_fuel": ship["max_fuel"] + 300}),
    },
    "cylindrical_tank": {
        "name": "Cylindrical Tank", "cost": 3000, "planet": None,
        "desc": "+500 fuel capacity.",
        "apply": lambda ship: ship.update({"max_fuel": ship["max_fuel"] + 500}),
    },
    "small_hold": {
        "name": "Small Hold", "cost": 1000, "planet": None,
        "desc": "+100 cargo capacity.",
        "apply": lambda ship: ship.update({"max_cargo": ship["max_cargo"] + 100}),
    },
    "side_hold": {
        "name": "Side Hold", "cost": 2000, "planet": "Terra",
        "desc": "+100 cargo capacity. Terra exclusive.",
        "apply": lambda ship: ship.update({"max_cargo": ship["max_cargo"] + 100}),
    },
    "grain_silo": {
        "name": "Grain Silo", "cost": 3000, "planet": "Agrica",
        "desc": "+200 cargo capacity. Agrica exclusive.",
        "apply": lambda ship: ship.update({"max_cargo": ship["max_cargo"] + 200}),
    },
    "broker_license": {
        "name": "Galactic Broker License", "cost": 1000, "planet": "Nexus",
        "desc": "Unlock price check across all planets. Nexus only.",
        "apply": lambda ship: ship.update({"broker_license": True}),
    },
    "passenger_quoters": {
        "name": "Passenger Quoters", "cost": 1000, "planet": None,
        "desc": "Unlock 1 passenger slot.",
        "apply": lambda ship: ship.update({"passenger_slot": True}),
    },
    "long_range_radar": {
        "name": "Long Range Radar", "cost": 3000, "planet": "Terra",
        "desc": "-15% pirate encounter chance. Terra exclusive.",
        "apply": lambda ship: ship.update({"radar": True}),
    },
    "booster": {
        "name": "Booster", "cost": 1000, "planet": "Void Colony",
        "desc": "Flee costs 5×angst fuel instead of 20×. Void Colony only. "
                "Also cuts Void Colony→Nexus to 3 parsec.",
        "apply": lambda ship: ship.update({"booster": True}),
    },
}


def visit_engineering_bay(ship, state):
    while True:
        print("\n── ENGINEERING BAY ──────────────────────────────────")
        print(f"  Fuel: {ship['fuel']} / {ship['max_fuel']}  |  Credits: {ship['credits']:,}")
        print("  [1] Fuel Up")
        print("  [2] Drain Fuel")
        print("  [3] Upgrades")
        print("  [9] Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            _fuel_up(ship)
        elif choice == "2":
            _drain_fuel(ship)
        elif choice == "3":
            _upgrades_menu(ship, state)
        elif choice == "9":
            break
        else:
            print("Invalid choice.")


def _fuel_up(ship):
    available_space = ship["max_fuel"] - ship["fuel"]
    if available_space <= 0:
        print("Tank is full.")
        return
    print(f"\n  Fuel costs {FUEL_PRICE}cr/unit. Space available: {available_space}")
    options = [100, 200, 500, 1000]
    valid = [(n, n * FUEL_PRICE) for n in options if n <= available_space]
    valid.append((available_space, available_space * FUEL_PRICE))
    seen = {}
    display = []
    for amt, cost in valid:
        if amt not in seen:
            seen[amt] = True
            display.append((amt, cost))
    for i, (amt, cost) in enumerate(display, 1):
        label = "FULL" if amt == available_space else str(amt)
        print(f"  [{i}] +{label} fuel  →  {cost:,} cr")
    print("  [0] Cancel")
    choice = _get_int("Choose: ", 0, len(display))
    if choice == 0:
        return
    amt, cost = display[choice - 1]
    if ship["credits"] < cost:
        print(f"Not enough credits. Need {cost:,}, have {ship['credits']:,}.")
        return
    ship["credits"] -= cost
    ship["fuel"] = min(ship["max_fuel"], ship["fuel"] + amt)
    print(f"✓ Fuelled +{amt}. Tank: {ship['fuel']}/{ship['max_fuel']}")


def _drain_fuel(ship):
    drainable = ship["fuel"] - MIN_FUEL_TO_DEPART
    if drainable <= 0:
        print(f"Cannot drain — must keep at least {MIN_FUEL_TO_DEPART} fuel to depart.")
        return
    print(f"\n  Drainable: {drainable} units → {drainable * FUEL_PRICE:,} cr max")
    raw_options = [100, 200, 500, 1000, int(ship["fuel"] * 0.9)]
    options = sorted(set(min(n, drainable) for n in raw_options if n > 0))
    options = [n for n in options if n <= drainable]
    for i, amt in enumerate(options, 1):
        cr = amt * FUEL_PRICE
        label = "90%" if amt == int(ship["fuel"] * 0.9) else str(amt)
        print(f"  [{i}] Drain {label} fuel  →  +{cr:,} cr")
    print("  [0] Cancel")
    choice = _get_int("Choose: ", 0, len(options))
    if choice == 0:
        return
    amt = options[choice - 1]
    ship["fuel"] -= amt
    ship["credits"] += amt * FUEL_PRICE
    print(f"✓ Drained {amt} fuel. Tank: {ship['fuel']}/{ship['max_fuel']}. Gained {amt * FUEL_PRICE:,} cr.")


def _upgrades_menu(ship, state):
    location = ship["location"]
    print(f"\n── UPGRADES  ({location}) ──────────────────────────────")
    available = [
        (uid, u) for uid, u in UPGRADES.items()
        if (u["planet"] is None or u["planet"] == location)
        and uid not in ship["upgrades_bought"]
    ]
    if not available:
        print("  No upgrades available here (or all purchased).")
        return
    for i, (uid, u) in enumerate(available, 1):
        planet_tag = f" [{u['planet']} only]" if u["planet"] else ""
        print(f"  [{i}] {u['name']}  —  {u['cost']:,} cr{planet_tag}")
        print(f"       {u['desc']}")
    print("  [0] Cancel")
    choice = _get_int("Choose upgrade: ", 0, len(available))
    if choice == 0:
        return
    uid, u = available[choice - 1]
    if ship["credits"] < u["cost"]:
        print(f"Not enough credits. Need {u['cost']:,}, have {ship['credits']:,}.")
        return
    ship["credits"] -= u["cost"]
    u["apply"](ship)
    ship["upgrades_bought"].append(uid)
    print(f"✓ {u['name']} installed.")


# ═══════════════════════════════════════════════════════════════════════════════
# PASSENGERS
# ═══════════════════════════════════════════════════════════════════════════════

PASSENGER_ROSTER = [
    {
        "shortname": "Whitemaine",
        "fullname":  "Whitemaine, Pride Mercenary",
        "cantina_text": (
            "A large lion-like mercenary with two laser guns holstered on his back "
            "is nursing a drink in the corner. He's looking for his lost cub — "
            "the little furball is always on another planet, apparently."
        ),
        "exit_text": (
            "Whitemaine lumbers off the ship the moment the ramp drops. "
            "'I hate hyperlines,' he growls. 'I hate teleportation. I hate space.' "
            "He slaps 300 credits into your hand without looking back."
        ),
    },
]


def maybe_spawn_passenger(ship, state):
    """20% chance to spawn a passenger if slot is unlocked and none waiting."""
    if not ship.get("passenger_slot"):
        return
    if state.get("passenger_waiting"):
        return  # already one waiting, don't stack
    if random.random() < 0.20:
        p = random.choice(PASSENGER_ROSTER).copy()
        other_planets = [pl for pl in PLANET_NAMES if pl != ship["location"]]
        p["destination"] = random.choice(other_planets)
        state["passenger_waiting"] = p


def check_passenger_delivery(ship, state):
    """Call on arrival. If passenger matches planet, pay out."""
    p = ship.get("passenger")
    if p and p["destination"] == ship["location"]:
        print("\n" + "─" * 50)
        print(p["exit_text"])
        ship["credits"] += 300
        print(f"  +300 credits received.")
        print("─" * 50)
        ship["passenger"] = None


# ═══════════════════════════════════════════════════════════════════════════════
# PIRATES
# ═══════════════════════════════════════════════════════════════════════════════

def pirate_encounter(ship, state):
    """Full pirate encounter. Returns True if voyage continues, False on GAME OVER."""
    state["piratangst"] += 1
    angst = state["piratangst"]
    bribe_cost = state["piratbribe"]

    print("\n" + "⚠" * 50)
    print(f"  PIRATE INTERCEPT!  (Angst level: {angst})")
    print("⚠" * 50)

    flee_mult = 5 if ship.get("booster") else 20
    flee_cost = min(flee_mult * angst, ship["fuel"] - MIN_FUEL_TO_DEPART)
    flee_cost = max(0, flee_cost)

    print(f"\n  [1] Fight    (weapons: {ship['weapons']})")
    print(f"  [2] Flee     (costs {flee_cost} fuel)")
    print(f"  [3] Bribe    ({bribe_cost} cr — price rises each use)")
    print(f"  [4] Drop Cargo (lose half of each good, min 1)")
    print(f"  [5] Bluff    (claim empty; auto-pass if cargo ≤10)")
    print(f"  [6] Surrender (WARNING: this ends your game)")

    choice = _get_int("Choose: ", 1, 6)

    # ── FIGHT ──────────────────────────────────────────────────────────────────
    if choice == 1:
        pirate_power = max(1, angst // 20)
        state["piratangst"] += 2
        print(f"\n  Pirate power: {pirate_power}  vs  Your weapons: {ship['weapons']}")
        if ship["weapons"] < pirate_power:
            # Weaker
            _drop_half_cargo(ship)
            print("  Outgunned! You lose half your cargo but escape with your life.")
        elif ship["weapons"] == pirate_power:
            print("  Standoff! The pirate sees you're equally matched and backs off.")
            print("  You're known as 'The Porcupine' in these lanes now.")
        else:
            # Superior
            bounty = 100 * angst
            ship["credits"] += bounty
            state["piratangst"] += 3
            print(f"  You obliterate the pirate scum! Bounty collected: {bounty:,} cr.")
        return True

    # ── FLEE ──────────────────────────────────────────────────────────────────
    elif choice == 2:
        if ship["fuel"] - flee_cost < MIN_FUEL_TO_DEPART:
            print(f"  Not enough fuel to flee! You'd need {flee_cost} fuel but can't go below {MIN_FUEL_TO_DEPART}.")
            print("  Choose another option.")
            return pirate_encounter_retry(ship, state, exclude=2)
        ship["fuel"] -= flee_cost
        print(f"  You gun the engines and escape! Fuel burned: {flee_cost}. Remaining: {ship['fuel']}")
        return True

    # ── BRIBE ──────────────────────────────────────────────────────────────────
    elif choice == 3:
        if ship["credits"] < bribe_cost:
            print(f"  You can't afford the bribe ({bribe_cost} cr). They take everything.")
            loss = ship["credits"]
            ship["credits"] = 0
            print(f"  Lost all {loss} credits.")
            state["piratbribe"] += 100
        else:
            ship["credits"] -= bribe_cost
            state["piratbribe"] += 100
            state["piratangst"] = max(0, state["piratangst"] - 3)
            print(f"  You pay {bribe_cost} cr. The pirate waves you through, pleased.")
            print(f"  Next bribe will cost {state['piratbribe']} cr.")
        return True

    # ── DROP CARGO ──────────────────────────────────────────────────────────────
    elif choice == 4:
        if not ship["cargo"]:
            print("  Nothing to drop! Pirates board you anyway.")
            loss = min(200, ship["credits"])
            ship["credits"] -= loss
            print(f"  They take {loss} cr and leave, disgusted.")
        else:
            _drop_half_cargo(ship)
            state["piratangst"] = max(0, state["piratangst"] - 2)
            print("  You jettison half your cargo. Pirates scoop it up and leave.")
        return True

    # ── BLUFF ──────────────────────────────────────────────────────────────────
    elif choice == 5:
        total_cargo = sum(ship["cargo"].values())
        if total_cargo <= 10:
            print("  'Nothing here, officer.' The pirate squints, shrugs, and leaves.")
            print("  Auto-pass — your hold was basically empty.")
        elif random.random() < 0.5:
            print("  Your poker face is legendary. The pirate buys it and warps off.")
        else:
            print("  They don't believe you. The bluff is burned for this encounter.")
            state["piratangst"] += 2
            print("  Forced into a worse position — choose again (no bluffing).")
            return pirate_encounter_retry(ship, state, exclude=5)
        return True

    # ── SURRENDER ──────────────────────────────────────────────────────────────
    elif choice == 6:
        confirm = input("\n  Are you sure? You will be sold as a crypto miner on Zeta-9. [yes/no]: ").strip().lower()
        if confirm == "yes":
            print("\n  The pirate docks with your ship. You're stripped of everything.")
            print("  Six months later you're mining blockchain hashes in a Zeta-9 server farm.")
            print("  The smell of saffron is the last thing you remember of freedom.")
            print("\n  ─── GAME OVER ───")
            return False
        else:
            print("  You reconsider. Choose again.")
            return pirate_encounter(ship, state)

    return True


def pirate_encounter_retry(ship, state, exclude: int):
    """Re-prompt pirate options excluding one choice (bluff burned / flee impossible)."""
    angst = state["piratangst"]
    bribe_cost = state["piratbribe"]
    flee_mult = 5 if ship.get("booster") else 20
    flee_cost = min(flee_mult * angst, ship["fuel"] - MIN_FUEL_TO_DEPART)

    options = []
    if exclude != 1:
        options.append(("1", f"Fight (weapons: {ship['weapons']})"))
    if exclude != 2:
        options.append(("2", f"Flee ({flee_cost} fuel)"))
    if exclude != 3:
        options.append(("3", f"Bribe ({bribe_cost} cr)"))
    if exclude != 4:
        options.append(("4", "Drop Cargo"))
    if exclude != 5:
        options.append(("5", "Bluff"))
    options.append(("6", "Surrender (GAME OVER)"))

    print()
    for key, label in options:
        print(f"  [{key}] {label}")

    valid_keys = [k for k, _ in options]
    while True:
        raw = input("Choose: ").strip()
        if raw in valid_keys:
            # Patch choice back into original handler by mutating and re-calling
            # Simplest: map key back to int and re-enter
            state_backup_exclude = exclude
            # Re-enter main encounter with fake choice injection is messy.
            # Instead handle inline:
            c = int(raw)
            if c == 1:
                pirate_power = max(1, angst // 20)
                state["piratangst"] += 2
                if ship["weapons"] < pirate_power:
                    _drop_half_cargo(ship)
                    print("  Outgunned! Lost half cargo.")
                elif ship["weapons"] == pirate_power:
                    print("  Standoff. Pirate backs off.")
                else:
                    bounty = 100 * angst
                    ship["credits"] += bounty
                    state["piratangst"] += 3
                    print(f"  Pirate destroyed! Bounty: {bounty:,} cr.")
                return True
            elif c == 3:
                if ship["credits"] < bribe_cost:
                    loss = ship["credits"]; ship["credits"] = 0
                    print(f"  Can't afford bribe. Lost {loss} cr.")
                else:
                    ship["credits"] -= bribe_cost
                    state["piratbribe"] += 100
                    state["piratangst"] = max(0, state["piratangst"] - 3)
                    print(f"  Bribed for {bribe_cost} cr. Next: {state['piratbribe']} cr.")
                return True
            elif c == 4:
                _drop_half_cargo(ship)
                state["piratangst"] = max(0, state["piratangst"] - 2)
                print("  Dropped half cargo. Pirates leave.")
                return True
            elif c == 6:
                confirm = input("  Sure? [yes/no]: ").strip().lower()
                if confirm == "yes":
                    print("  GAME OVER — crypto miner on Zeta-9.")
                    return False
                else:
                    return pirate_encounter_retry(ship, state, exclude)
        print(f"  Choose from: {', '.join(valid_keys)}")


def _drop_half_cargo(ship):
    for good in list(ship["cargo"].keys()):
        drop = max(1, math.ceil(ship["cargo"][good] / 2))
        ship["cargo"][good] -= drop
        if ship["cargo"][good] <= 0:
            del ship["cargo"][good]
        print(f"  Dropped {drop}× {good}.")


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL EVENTS (non-pirate)
# ═══════════════════════════════════════════════════════════════════════════════

def event_spice_festival_travel(ship, state, destination):
    planet = state["planets"][destination]
    for good in planet["base_prices"]:
        planet["base_prices"][good] = int(planet["base_prices"][good] * 1.1)
    print(f"🎉 SPICE FESTIVAL on {destination}! All prices +10%.")


def event_fuel_leak(ship, state, destination):
    lost = random.randint(15, 35)
    ship["fuel"] = max(0, ship["fuel"] - lost)
    print(f"🔧 FUEL LEAK mid-jump. Lost {lost} fuel.")


def event_mystery_cargo(ship, state, destination):
    free = ship["max_cargo"] - sum(ship["cargo"].values())
    if free >= 5:
        ship["cargo"]["Mystery Crate"] = ship["cargo"].get("Mystery Crate", 0) + 5
        print("📦 Drifting cargo pod attached to hull. +5 Mystery Crate.")
    else:
        print("📦 Drifting cargo pod — no room. It drifts on.")


NON_PIRATE_EVENTS = [
    (0.12, event_spice_festival_travel),
    (0.10, event_fuel_leak),
    (0.08, event_mystery_cargo),
]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_int(prompt: str, lo: int = None, hi: int = None) -> int:
    while True:
        try:
            val = int(input(prompt))
            if lo is not None and val < lo:
                print(f"  ≥ {lo} please.")
                continue
            if hi is not None and val > hi:
                print(f"  ≤ {hi} please.")
                continue
            return val
        except ValueError:
            print("  Enter a number.")


def _col(text, width):
    return str(text).ljust(width)


def _cargo_used(ship):
    return sum(ship["cargo"].values())


def _cargo_free(ship):
    return ship["max_cargo"] - _cargo_used(ship)


def _travel_fuel_cost(origin: str, destination: str) -> int:
    i = PLANET_NAMES.index(origin)
    j = PLANET_NAMES.index(destination)
    dist = abs(i - j)
    return max(10, min(50, dist * 12 + random.randint(-5, 5)))


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def show_status(ship, state):
    print("\n" + "═" * 50)
    print(f"  STATUS  —  {date_str(state)}  (turn {state['turn']})")
    print("═" * 50)
    print(f"  Location : {ship['location']}")
    print(f"  Credits  : {ship['credits']:,}")
    print(f"  Fuel     : {ship['fuel']} / {ship['max_fuel']}")
    print(f"  Cargo    : {_cargo_used(ship)} / {ship['max_cargo']} units")
    if ship["cargo"]:
        for good, qty in ship["cargo"].items():
            print(f"             • {good}: {qty}")
    else:
        print("             (empty)")
    print(f"  Weapons  : {ship['weapons']}")
    extras = []
    if ship.get("broker_license"):   extras.append("Broker License")
    if ship.get("radar"):            extras.append("Radar")
    if ship.get("booster"):          extras.append("Booster")
    if ship.get("passenger_slot"):
        p = ship.get("passenger")
        extras.append(f"Passenger: {p['shortname']} → {p['destination']}" if p else "Passenger slot (empty)")
    if extras:
        print(f"  Upgrades : {', '.join(extras)}")
    if ship["location"] == "Terra" and ship.get("farm_bought"):
        print("  🌿 You own a cinnamon farm here.")
    print("═" * 50)


def show_market(ship, state):
    planet_name = ship["location"]
    planet = state["planets"][planet_name]
    m = state["month_index"]

    # Festival notice
    fest_good, fest_boost = festival_boost_this_month(planet_name, m)
    if fest_good:
        _name = PLANET_FESTIVALS[planet_name][2]
        print(f"\n  🎊 {_name.upper()} this month! {fest_good} price +{fest_boost}cr")

    print(f"\n── MARKET: {planet_name} ────────────────────────────────")
    print(f"  {'Good':<18} {'Price':>6}  {'Role'}")
    print(f"  {'─'*18} {'─'*6}  {'─'*12}")
    for good in planet["spices"]:
        price = effective_price(state, planet_name, good)
        role = ""
        if good == planet["production"]:
            role = "◀ PRODUCTION"
        elif good == planet["demand"]:
            role = "▶ DEMAND"
        print(f"  {good:<18} {price:>6}  {role}")
    print()
    print("  [1] Buy   [2] Sell   [3] Travel   [4] Status")
    print("  [5] Price Check   [6] Farm   [7] Cantina   [8] Engineering Bay")
    print("  [9] Save   [0] Quit")


# ═══════════════════════════════════════════════════════════════════════════════
# TRADE
# ═══════════════════════════════════════════════════════════════════════════════

def buy_spice(ship, state):
    planet_name = ship["location"]
    planet = state["planets"][planet_name]
    if _cargo_free(ship) == 0:
        print("Cargo hold is full!")
        return
    print("\n── BUY ──────────────────────────────────────────────")
    spices = planet["spices"]
    for i, good in enumerate(spices, 1):
        price = effective_price(state, planet_name, good)
        print(f"  [{i}] {good:<18} {price:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose good: ", 0, len(spices))
    if choice == 0:
        return
    good = spices[choice - 1]
    price = effective_price(state, planet_name, good)
    max_buy = min(ship["credits"] // price, _cargo_free(ship))
    if max_buy <= 0:
        print("Not enough credits or cargo space!")
        return
    amount = _get_int(f"How many {good}? (0 cancel, max {max_buy}): ", 0, max_buy)
    if amount == 0:
        return
    cost = amount * price
    ship["credits"] -= cost
    ship["cargo"][good] = ship["cargo"].get(good, 0) + amount
    print(f"✓ Bought {amount}× {good} for {cost:,} cr.")


def sell_spice(ship, state):
    if not ship["cargo"]:
        print("Cargo hold is empty!")
        return
    planet_name = ship["location"]
    cargo_items = list(ship["cargo"].items())
    print("\n── SELL ─────────────────────────────────────────────")
    for i, (good, qty) in enumerate(cargo_items, 1):
        price = effective_price(state, planet_name, good)
        print(f"  [{i}] {good:<18} {qty:>4} units @ {price:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose good: ", 0, len(cargo_items))
    if choice == 0:
        return
    good, available = cargo_items[choice - 1]
    price = effective_price(state, planet_name, good)
    amount = _get_int(f"How many {good}? (max {available}): ", 1, available)
    gross = amount * price
    tax = max(1, math.ceil(gross * 0.02))
    net = gross - tax
    ship["credits"] += net
    ship["cargo"][good] -= amount
    if ship["cargo"][good] <= 0:
        del ship["cargo"][good]
    print(f"✓ Sold {amount}× {good} for {gross:,} cr.  Tax: {tax} cr.  Net: {net:,} cr.")


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL
# ═══════════════════════════════════════════════════════════════════════════════

def travel(ship, state):
    if ship["fuel"] < MIN_FUEL_TO_DEPART:
        print(f"Need at least {MIN_FUEL_TO_DEPART} fuel to depart. Refuel in Engineering Bay.")
        return

    other_planets = [p for p in PLANET_NAMES if p != ship["location"]]
    print("\n── TRAVEL ───────────────────────────────────────────")
    for i, planet in enumerate(other_planets, 1):
        cost = _travel_fuel_cost(ship["location"], planet)
        print(f"  [{i}] {planet:<16}  ~{cost} fuel")
    print("  [0] Cancel")
    choice = _get_int("Destination: ", 0, len(other_planets))
    if choice == 0:
        return

    destination = other_planets[choice - 1]
    fuel_cost = _travel_fuel_cost(ship["location"], destination)

    if ship["fuel"] - fuel_cost < MIN_FUEL_TO_DEPART:
        print(f"Not enough fuel. Need {fuel_cost} + {MIN_FUEL_TO_DEPART} reserve. Have {ship['fuel']}.")
        return

    # Remote seed for event roll
    random.seed(fetch_remote_seed())

    ship["fuel"] -= fuel_cost
    ship["location"] = destination
    advance_time(state)  # month + turn advance on successful departure
    print(f"\n🚀 Jumped to {destination}. Fuel used: {fuel_cost}. Date: {date_str(state)}")

    # Drift neutral prices on arrival (separate from turn-based inflation)
    planet = state["planets"][destination]
    for good in planet["base_prices"]:
        if good not in (planet["production"], planet["demand"]):
            planet["base_prices"][good] = max(
                10, planet["base_prices"][good] + random.randint(-5, 5)
            )

    random.seed()

    # Pirate check
    pirate_chance = 0.10 if ship.get("radar") else 0.25
    if random.random() < pirate_chance:
        alive = pirate_encounter(ship, state)
        if not alive:
            return "GAME_OVER"
    else:
        # Non-pirate events
        roll = random.random()
        cumulative = 0.0
        for prob, fn in NON_PIRATE_EVENTS:
            cumulative += prob
            if roll < cumulative:
                fn(ship, state, destination)
                break

    check_passenger_delivery(ship, state)
    maybe_spawn_passenger(ship, state)


# ═══════════════════════════════════════════════════════════════════════════════
# PRICE CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def price_check(ship, state):
    if not ship.get("broker_license"):
        print("\n  Access denied. You need a Galactic Broker License.")
        print("  Head to Nexus to purchase one. Maybe sell the ship to afford it.")
        return
    W = [14, 16, 7, 7, 12]
    header = (f"  {_col('Planet', W[0])} {_col('Good', W[1])} "
              f"{_col('Base', W[2])} {_col('Eff.', W[3])} {_col('Role', W[4])}")
    sep = "  " + "─" * (sum(W) + 4)
    print("\n── PRICE CHECK (ALL PLANETS) ────────────────────────")
    print(header)
    print(sep)
    for planet_name in PLANET_NAMES:
        planet = state["planets"][planet_name]
        for good in planet["spices"]:
            base  = planet["base_prices"][good]
            eff   = effective_price(state, planet_name, good)
            role  = ""
            if good == planet["production"]:  role = "PRODUCTION"
            elif good == planet["demand"]:    role = "DEMAND"
            print(f"  {_col(planet_name, W[0])} {_col(good, W[1])} "
                  f"{_col(base, W[2])} {_col(eff, W[3])} {_col(role, W[4])}")
        print(sep)


# ═══════════════════════════════════════════════════════════════════════════════
# FARM
# ═══════════════════════════════════════════════════════════════════════════════

def visit_farm(ship, state):
    while True:
        print("\n" + "=" * 50)
        print(random.choice(state["planets"]["Terra"]["farm_fluff"]))
        print("=" * 50)
        print("  [1] Stay a little longer   [2] Return to the stars")
        c = input("Choose: ").strip()
        if c == "2":
            print("You leave the farm, ready to face the galaxy again.")
            break


# ═══════════════════════════════════════════════════════════════════════════════
# CANTINA
# ═══════════════════════════════════════════════════════════════════════════════

def visit_cantina(ship, state):
    cantina = cantinas[ship["location"]]
    while True:
        pw = state.get("passenger_waiting")
        traveler_line = f"  [3] Traveler — {pw['shortname']} → {pw['destination']}" if pw else "  [3] Traveler — (none)"
        print(f"\n── {cantina['name'].upper()} ({ship['location']}) ───────────────────")
        print("  [1] I need a drink")
        print("  [2] Ask for advice")
        print(traveler_line)
        print("  [4] Rest for a while  (1 month passes)")
        print("  [9] Back to spaceport")
        choice = input("Choose: ").strip()

        if choice == "1":
            drink = cantina["drink"]
            price = effective_price(state, ship["location"], drink["ingredient"])
            drink_cost = max(1, int(price * 0.5))
            if ship["credits"] < drink_cost:
                print(f"  Can't afford a {drink['name']} ({drink_cost} cr).")
            else:
                ship["credits"] -= drink_cost
                print(f"\n  You buy a {drink['name']} for {drink_cost} cr.")
                print(f"  {random.choice(drink['fluff'])}")

        elif choice == "2":
            pool = random.choice(list(advice_pools.keys()))
            advice = random.choice(advice_pools[pool])
            print(f"\n  [Bartender — {pool.upper()}]: {advice}")

        elif choice == "3":
            if not ship.get("passenger_slot"):
                print("  You don't have a Passenger Quoters upgrade installed.")
            elif not pw:
                print("  Nobody looking for a ride right now.")
            else:
                print(f"\n  {pw['fullname']}")
                print(f"  {pw['cantina_text']}")
                print(f"  Destination: {pw['destination']}")
                if ship.get("passenger"):
                    print(f"  (You already have {ship['passenger']['shortname']} aboard — they will be dropped off.)")
                take = input("  Take them aboard? [y/n]: ").strip().lower()
                if take == "y":
                    ship["passenger"] = pw
                    state["passenger_waiting"] = None
                    print(f"  {pw['shortname']} boards your ship.")

        elif choice == "4":
            print("\n" + "─" * 50)
            print("  You spend a month in the cantina. The days blur together.")
            if state["galaxy_story_index"] < len(galaxy_story):
                print(f"\n  [GALAXY NEWS]: {galaxy_story[state['galaxy_story_index']]}")
                state["galaxy_story_index"] += 1
            else:
                print("  The galaxy turns, quietly.")
            print("─" * 50)
            input("  [Enter to continue...]")
            advance_time(state)
            maybe_spawn_passenger(ship, state)
            print(f"  Date is now: {date_str(state)}")

        elif choice == "9":
            break
        else:
            print("  Invalid choice.")


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════════════

def save_game(ship, state):
    data = {
        "ship": {k: v for k, v in ship.items()},
        "planets_prices": {
            name: {"base_prices": pdata["base_prices"]}
            for name, pdata in state["planets"].items()
        },
        "turn":                   state["turn"],
        "month_index":            state["month_index"],
        "year":                   state["year"],
        "piratangst":             state["piratangst"],
        "piratbribe":             state["piratbribe"],
        "galaxy_story_index":     state["galaxy_story_index"],
        "passenger_waiting":      state.get("passenger_waiting"),
        "festival_drops_applied": list(state["festival_drops_applied"]),
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved to {SAVE_FILE}")
    except OSError as e:
        print(f"⚠️  Save failed: {e}")


def load_game(planets, state):
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        for name, pdata in data["planets_prices"].items():
            if name in planets:
                planets[name]["base_prices"].update(pdata["base_prices"])
        state["turn"]               = data.get("turn", 1)
        state["month_index"]        = data.get("month_index", 0)
        state["year"]               = data.get("year", 2201)
        state["piratangst"]         = data.get("piratangst", 10)
        state["piratbribe"]         = data.get("piratbribe", 100)
        state["galaxy_story_index"] = data.get("galaxy_story_index", 0)
        state["passenger_waiting"]  = data.get("passenger_waiting")
        state["festival_drops_applied"] = set(data.get("festival_drops_applied", []))
        print(f"📂 Loaded from {SAVE_FILE}")
        return data["ship"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Load failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════════════════

def init_planets():
    planets = {}
    for planet_name, planet_data in planets_template.items():
        new_prices = {}
        for good, price in planet_data["base_prices"].items():
            if good in (planet_data["production"], planet_data["demand"]):
                new_prices[good] = price
            else:
                new_prices[good] = max(10, price + random.randint(-10, 10))
        planets[planet_name] = {
            **planet_data,
            "base_prices": new_prices,
        }
    planets["Terra"]["farm_fluff"] = [
        "You sit on the porch of your cinnamon farm. The sunset paints the orchard in gold.",
        "The cinnamon trees rustle. A neighbor waves. 'Harvest was good this year.'",
        "The scent of cinnamon fills the air. No fuel calculations. No pirate attacks. Just peace.",
    ]
    return planets


def new_ship():
    return {
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


def new_state(planets):
    return {
        "planets":                planets,
        "turn":                   1,
        "month_index":            0,
        "year":                   2201,
        "piratangst":             10,
        "piratbribe":             100,
        "galaxy_story_index":     0,
        "passenger_waiting":      None,
        "festival_drops_applied": set(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    planets = init_planets()
    state   = new_state(planets)

    print("═" * 55)
    print("  SPICE SPACE TRADER  v8")
    print("  Trade spices. Dodge pirates. Maybe buy a farm.")
    print("═" * 55)

    if os.path.exists(SAVE_FILE):
        ans = input("\nSave file found. Load it? [y/n]: ").strip().lower()
        if ans == "y":
            loaded = load_game(planets, state)
            ship = loaded if loaded else new_ship()
        else:
            ship = new_ship()
    else:
        ship = new_ship()

    while True:
        show_status(ship, state)
        show_market(ship, state)

        raw = input("\nChoose action: ").strip()

        # ── CHEAT CODE ─────────────────────────────────────────────────────────
        if raw.startswith("!credits "):
            try:
                amount = int(raw.split()[1])
                ship["credits"] += amount
            except (ValueError, IndexError):
                pass
            continue

        try:
            action = int(raw)
        except ValueError:
            print("Enter a number.")
            continue

        if action == 0:
            print(f"\nFinal credits: {ship['credits']:,}  |  Date: {date_str(state)}")
            if ship.get("farm_bought"):
                print("You retired to your cinnamon farm. You won. 🌿")
            break

        elif action == 1:
            buy_spice(ship, state)

        elif action == 2:
            sell_spice(ship, state)

        elif action == 3:
            result = travel(ship, state)
            if result == "GAME_OVER":
                break

        elif action == 4:
            show_status(ship, state)

        elif action == 5:
            price_check(ship, state)

        elif action == 6:
            if ship["location"] != "Terra":
                print("The farm is on Terra.")
            elif not ship.get("farm_bought"):
                print(f"\nBuy a cinnamon farm for 10,000 cr? (You have {ship['credits']:,})")
                if ship["credits"] >= 10000:
                    if input("Confirm [y/n]: ").strip().lower() == "y":
                        ship["credits"] -= 10000
                        ship["farm_bought"] = True
                        print("🌿 You now own a cinnamon farm on Terra.")
                else:
                    print(f"Need {10000 - ship['credits']:,} more credits.")
            else:
                visit_farm(ship, state)

        elif action == 7:
            visit_cantina(ship, state)

        elif action == 8:
            visit_engineering_bay(ship, state)

        elif action == 9:
            save_game(ship, state)

        else:
            print("Invalid action.")


if __name__ == "__main__":
    main()
