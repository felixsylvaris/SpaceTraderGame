"""
=============================================================
  SPICE SPACE TRADER  —  Changelog
=============================================================

v9
  + Farm moved to [f] key; frees number keys on spaceport
  + Promenade added as [6] on spaceport — all planet services live here
    Cantina moved under Promenade
    Farm (Terra only) accessible via [f] inside Promenade
    Infobroker added to Promenade (free): Goods / Harvest / Festivals tables
    Concert Hall added to Promenade — loads songs.json, graceful fail
  + Price Spread: buy price = mean+spread, sell price = mean-spread
    Low goods ±5, Mid goods ±10, High goods ±15
    Market and price-check show Sell/Buy columns
  + Good price bounds: each good has min/mean/max from GOOD_DATA table
    Mean price (base_price) clamped to [min_price, max_price] each turn
    Effective price (with season/festival) may push slightly beyond but
    is hard-clamped at [max(1, min-spread), max_price+spread]
  + GOOD_DATA table centralises: spread_type, min, mean, max per good
  + News feed printed once per planet visit (flag resets on departure)
    Shows: active traveler notice, festival notice, current harvest good
  + songs.json multi-song support; shortname/fullname/text/art fields
    Event Horizon by (unknown) included as first song
  + Paprika pattern corrected to low (was mid in v8)
  + Allspice base price corrected to 120 on Terra (demand price)
  + Traveler [3] in cantina only shown if passenger_quoters installed

v8.1
  - Clove price on Void Colony dropped to 40 (avoid perfect Nexus pair)
  - Allspice festival boost upgraded to high (100cr)
  - Void Torpedo weapon bonus raised to +2

v8
  + Date & Calendar, Extra Goods, Taxes, Inflation, Harvest Seasons,
    Festivals, Engineering Bay, Upgrades, Broker License, Passengers,
    Pirates overhauled, Cheat code, Save/Load

v7
  + requests hook, event system, fuel/cargo split, recursion fixes,
    input validation, columnar price check, save/load JSON, distance travel

v6  (original)
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

SAVE_FILE     = "spice_trader_save.json"
SONGS_FILE    = "songs.json"
FUEL_PRICE    = 1    # cr per fuel unit — change for OPEC crisis
MIN_FUEL_TO_DEPART = 50

# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

MONTH_NAMES    = ["Ianu","Febu","Mari","Aprix","Maiu","Iuin","Septr","Octo","Nova","Dedl"]
MONTHS_PER_YEAR = 10

def month_name(idx):   return MONTH_NAMES[idx % MONTHS_PER_YEAR]
def date_str(state):   return f"{month_name(state['month_index'])} {state['year']}"

def advance_time(state, months=1):
    for _ in range(months):
        state["turn"]        += 1
        state["month_index"] += 1
        if state["month_index"] >= MONTHS_PER_YEAR:
            state["month_index"] = 0
            state["year"]       += 1
    apply_inflation(state)
    check_festival_drop(state)

# ═══════════════════════════════════════════════════════════════════════════════
# GOOD DATA  — single source of truth for price bounds and spread type
# ═══════════════════════════════════════════════════════════════════════════════
#
#  spread_type  low=±5   mid=±10   high=±15
#  min / mean / max  →  mean is the default base price used at game start
#  production/demand base prices may differ per planet (cheaper/pricier)
#  but the bounds apply globally to the drifting base_price on each planet

GOOD_DATA = {
    #            spread   min   mean   max
    "Cinnamon":  ("low",   15,   50,   150),
    "Turmeric":  ("low",   18,   60,   180),
    "Paprika":   ("low",   21,   70,   210),
    "Ginger":    ("mid",   24,   80,   240),
    "Clove":     ("mid",   27,   90,   270),
    "Vanilla":   ("mid",   30,  100,   300),
    "Cardamom":  ("mid",   33,  110,   330),
    "Allspice":  ("high",  36,  120,   360),
    "Saffron":   ("high",  45,  150,   450),
    "Nutmeg":    ("high",  42,  140,   420),
    "Void Pepper":("high", 150, 500,  1500),
    "Mystery Crate": ("low", 1,  10,   500),  # wild card — wide range
}

SPREAD_AMOUNT = {"low": 5, "mid": 10, "high": 15}

def _spread(good):
    entry = GOOD_DATA.get(good)
    if entry is None: return 5
    return SPREAD_AMOUNT[entry[0]]

def _price_min(good):
    entry = GOOD_DATA.get(good)
    return entry[1] if entry else 1

def _price_max(good):
    entry = GOOD_DATA.get(good)
    return entry[3] if entry else 9999

def _clamp_base(good, price):
    """Clamp a drifting base price within [min, max] for this good."""
    return max(_price_min(good), min(_price_max(good), price))

# ═══════════════════════════════════════════════════════════════════════════════
# HARVEST SEASONS & FESTIVALS
# ═══════════════════════════════════════════════════════════════════════════════

SEASON_LOW  = [0, 0, +5, +5, +10, +10, +15, +15, +20, +10]
SEASON_MID  = [-20,-15,-5, 0,+5,+10,+20,+15,+10, 0]
SEASON_HIGH = [-20,-10, 0,+10,+20,+30,+40,+50,+30,+20]

GOOD_SEASONS = {
    "Cinnamon":    (0, "low"),
    "Turmeric":    (1, "low"),
    "Paprika":     (2, "low"),   # corrected from mid
    "Ginger":      (3, "mid"),
    "Clove":       (4, "mid"),
    "Vanilla":     (5, "mid"),
    "Cardamom":    (6, "mid"),
    "Allspice":    (7, "high"),
    "Saffron":     (8, "high"),
    "Nutmeg":      (9, "high"),
    "Void Pepper": None,
    "Mystery Crate": None,
}

SEASON_PATTERNS = {"low": SEASON_LOW, "mid": SEASON_MID, "high": SEASON_HIGH}
FESTIVAL_BOOST  = {"low": 50, "mid": 75, "high": 100}

PLANET_FESTIVALS = {
    "Terra":       ("Cinnamon", 2, "Cinnamon Roll Festival",  "low"),
    "Zeta-9":      ("Ginger",   5, "Golden Ginger Gala",      "mid"),
    "Void Colony": ("Vanilla",  7, "Void Vanilla Vigil",      "mid"),
    "Agrica":      ("Paprika",  3, "Paprika Panic Parade",    "low"),
    "Nexus":       ("Allspice", 9, "Allspice Arbitrage Fête", "high"),
}

def season_offset(good, current_month):
    entry = GOOD_SEASONS.get(good)
    if entry is None: return 0
    harvest_month, pattern_key = entry
    pattern = SEASON_PATTERNS[pattern_key]
    return pattern[(current_month - harvest_month) % MONTHS_PER_YEAR]

def festival_boost_this_month(planet_name, current_month):
    if planet_name not in PLANET_FESTIVALS: return None, 0
    good, fest_month, _name, boost_type = PLANET_FESTIVALS[planet_name]
    if current_month == fest_month:
        return good, FESTIVAL_BOOST[boost_type]
    return None, 0

def check_festival_drop(state):
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
                    planet["base_prices"][good] = _clamp_base(
                        good, planet["base_prices"][good] - boost
                    )

def current_harvest_good(month_index):
    """Return whichever good is being harvested this month (there's always one)."""
    for good, entry in GOOD_SEASONS.items():
        if entry is None: continue
        if entry[0] == month_index:
            return good
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# INFLATION
# ═══════════════════════════════════════════════════════════════════════════════

def apply_inflation(state):
    """Drift all neutral good prices each turn. Clamped to good's [min,max]."""
    for planet_name, planet in state["planets"].items():
        prod = planet["production"]
        dem  = planet["demand"]
        for good in list(planet["base_prices"].keys()):
            if good in (prod, dem): continue
            if random.random() < 0.5:
                delta = random.randint(1, 10)
            else:
                delta = -random.randint(1, 9)
            planet["base_prices"][good] = _clamp_base(
                good, planet["base_prices"][good] + delta
            )

# ═══════════════════════════════════════════════════════════════════════════════
# EFFECTIVE PRICE  (mean + season + festival, then spread for buy/sell)
# ═══════════════════════════════════════════════════════════════════════════════

def effective_mean(state, planet_name, good):
    """Base price + season + festival. Clamped to [min-spread, max+spread]."""
    base    = state["planets"][planet_name]["base_prices"].get(good, 1)
    season  = season_offset(good, state["month_index"])
    fg, fb  = festival_boost_this_month(planet_name, state["month_index"])
    festival= fb if good == fg else 0
    sp      = _spread(good)
    raw     = base + season + festival
    return max(_price_min(good) - sp, min(_price_max(good) + sp, raw))

def buy_price(state, planet_name, good):
    """Price the player pays when buying (mean + spread)."""
    return max(1, effective_mean(state, planet_name, good) + _spread(good))

def sell_price(state, planet_name, good):
    """Price the player receives when selling (mean - spread)."""
    return max(1, effective_mean(state, planet_name, good) - _spread(good))

# ═══════════════════════════════════════════════════════════════════════════════
# REMOTE SEED
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_remote_seed():
    if not REQUESTS_AVAILABLE: return random.randint(0, 99)
    try:
        resp = _requests.get(
            "https://www.randomnumberapi.com/api/v1.0/random?min=0&max=99&count=1",
            timeout=2)
        resp.raise_for_status()
        return resp.json()[0]
    except Exception:
        return random.randint(0, 99)

# ═══════════════════════════════════════════════════════════════════════════════
# PLANET DATA
# ═══════════════════════════════════════════════════════════════════════════════

PLANET_NAMES = ["Terra", "Zeta-9", "Void Colony", "Agrica", "Nexus"]

planets_template = {
    "Terra": {
        "production": "Cinnamon", "demand": "Allspice",
        "spices": ["Cinnamon","Cardamom","Vanilla","Allspice","Clove","Paprika","Ginger"],
        "base_prices": {
            "Cinnamon":25,"Cardamom":100,"Vanilla":90,
            "Allspice":120,"Clove":70,"Paprika":50,"Ginger":70},
    },
    "Zeta-9": {
        "production": "Saffron", "demand": "Ginger",
        "spices": ["Saffron","Turmeric","Paprika","Ginger","Nutmeg","Cinnamon"],
        "base_prices": {
            "Saffron":100,"Turmeric":50,"Paprika":60,
            "Ginger":90,"Nutmeg":135,"Cinnamon":40},
    },
    "Void Colony": {
        "production": "Void Pepper", "demand": "Cardamom",
        "spices": ["Void Pepper","Saffron","Ginger","Cardamom","Clove","Vanilla"],
        "base_prices": {
            "Void Pepper":500,"Saffron":200,"Ginger":65,
            "Cardamom":80,"Clove":40,"Vanilla":100},
    },
    "Agrica": {
        "production": "Paprika", "demand": "Vanilla",
        "spices": ["Paprika","Cinnamon","Turmeric","Vanilla","Allspice","Cardamom","Nutmeg"],
        "base_prices": {
            "Paprika":30,"Cinnamon":50,"Turmeric":30,
            "Vanilla":120,"Allspice":80,"Cardamom":60,"Nutmeg":100},
    },
    "Nexus": {
        "production": "Clove", "demand": "Turmeric",
        "spices": ["Clove","Void Pepper","Nutmeg","Saffron","Turmeric","Allspice"],
        "base_prices": {
            "Clove":35,"Void Pepper":750,"Nutmeg":110,
            "Saffron":175,"Turmeric":40,"Allspice":90},
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# CANTINA / ADVICE DATA
# ═══════════════════════════════════════════════════════════════════════════════

cantinas = {
    "Terra":       {"name":"The Cinnamon Tavern", "drink":{"name":"Cinnamon Beer",      "ingredient":"Cinnamon",   "fluff":["The warm beer tastes like home.","Sweet, spicy—exactly what you needed.","The bartender winks. 'Terra's finest.'"]}},
    "Zeta-9":      {"name":"The Golden Saffron",  "drink":{"name":"Saffron Mead",        "ingredient":"Saffron",    "fluff":["Golden and rich. Liquid sunlight.","The glass might actually be gold.","You feel fancy. The bartender smirks."]}},
    "Void Colony": {"name":"The Pepper's Shadow", "drink":{"name":"Void Pepper Whiskey", "ingredient":"Void Pepper","fluff":["Burns like a supernova. You see stars.","Rumoured to power small starships.","One sip: forget your name. Two: forget your debts."]}},
    "Agrica":      {"name":"The Paprika Den",      "drink":{"name":"Spiced Paprika Ale",  "ingredient":"Paprika",    "fluff":["Fiery and bold. You cough. Worth it.","The bartender: 'House special. Last season's best.'","You feel warmer immediately."]}},
    "Nexus":       {"name":"The Clove & Dagger",  "drink":{"name":"Clove Rum",           "ingredient":"Clove",      "fluff":["Smooth but packs a punch.","On the house—if you say where you got that Void Pepper.","Complex, like every deal made here."]}},
}

advice_pools = {
    "game": [
        "Buy low, sell high. Simple in theory. The galaxy complicates it.",
        "Weapons are expensive. Losing cargo to pirates is more expensive.",
        "Not all pirates are worth fighting. Running away is also valid.",
        "Nexus bankers are high on Void Pepper. They pay anything for a fix.",
        "Bad trades won't block future good ones.",
        "Upgrading your ship opens options you couldn't imagine before.",
        "The spread is real. You buy high and sell low. Trade volume is your friend.",
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
        "Zeta-9's Golden Ginger Gala in Iuin: traders dress as giant ginger roots "
        "and race hovercarts through the market. First prize: a barrel of Saffron Mead.",
        "The Void Vanilla Vigil on Void Colony every Octo is technically a funeral. "
        "For the harvest. They bury a vanilla pod in zero-G. Vanilla prices go insane.",
        "Agrica's Paprika Panic Parade in Aprix: they stuff a tentacle monster dummy "
        "with paprikas and beat it with plasma hammers. Children scramble for the shrapnel.",
        "Nexus hosts the Allspice Arbitrage Fête every Dedl. Brokers in formal wear "
        "outbid each other on allspice futures while drunk on Clove Rum. "
        "Prices crash the next month. Everyone pretends to be surprised.",
    ],
}

galaxy_story = [
    "A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle.",
    "A rogue freighter with 10,000 units of Void Pepper vanished near Nexus. No trace.",
    "A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.",
    "AGRICA DROUGHT — paprika yields expected to halve next season.",
    "The old Void Colony governor was arrested. The new one is friendlier to black-market deals.",
    "The jump lanes near Terra are being taxed now. Change is coming.",
    "The galaxy feels different lately. The old routes are shifting.",
]

# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADES
# ═══════════════════════════════════════════════════════════════════════════════

UPGRADES = {
    "kinetic_launcher": {"name":"Kinetic Launcher",        "cost":2000,"planet":None,         "desc":"Weapon+1. A classic.",                                        "apply":lambda s: s.update({"weapons":s["weapons"]+1})},
    "mining_laser":     {"name":"Mining Laser",            "cost":1000,"planet":"Zeta-9",     "desc":"Weapon+1. Cuts ore and pirates equally well.",                 "apply":lambda s: s.update({"weapons":s["weapons"]+1})},
    "void_torpedo":     {"name":"Void Torpedo",            "cost":5000,"planet":"Void Colony","desc":"Weapon+2. Void Colony special. Extremely illegal elsewhere.",  "apply":lambda s: s.update({"weapons":s["weapons"]+2})},
    "stern_tank":       {"name":"Stern Tank",              "cost":1000,"planet":None,         "desc":"+200 fuel capacity.",                                         "apply":lambda s: s.update({"max_fuel":s["max_fuel"]+200})},
    "portside_tank":    {"name":"Portside Tank",           "cost":2000,"planet":None,         "desc":"+300 fuel capacity.",                                         "apply":lambda s: s.update({"max_fuel":s["max_fuel"]+300})},
    "cylindrical_tank": {"name":"Cylindrical Tank",        "cost":3000,"planet":None,         "desc":"+500 fuel capacity.",                                         "apply":lambda s: s.update({"max_fuel":s["max_fuel"]+500})},
    "small_hold":       {"name":"Small Hold",              "cost":1000,"planet":None,         "desc":"+100 cargo capacity.",                                        "apply":lambda s: s.update({"max_cargo":s["max_cargo"]+100})},
    "side_hold":        {"name":"Side Hold",               "cost":2000,"planet":"Terra",      "desc":"+100 cargo capacity. Terra exclusive.",                       "apply":lambda s: s.update({"max_cargo":s["max_cargo"]+100})},
    "grain_silo":       {"name":"Grain Silo",              "cost":3000,"planet":"Agrica",     "desc":"+200 cargo capacity. Agrica exclusive.",                      "apply":lambda s: s.update({"max_cargo":s["max_cargo"]+200})},
    "broker_license":   {"name":"Galactic Broker License", "cost":1000,"planet":"Nexus",      "desc":"Unlock live price-check across all planets.",                  "apply":lambda s: s.update({"broker_license":True})},
    "passenger_quoters":{"name":"Passenger Quoters",       "cost":1000,"planet":None,         "desc":"Unlock 1 passenger slot.",                                    "apply":lambda s: s.update({"passenger_slot":True})},
    "long_range_radar": {"name":"Long Range Radar",        "cost":3000,"planet":"Terra",      "desc":"-15% pirate encounter chance. Terra exclusive.",               "apply":lambda s: s.update({"radar":True})},
    "booster":          {"name":"Booster",                 "cost":1000,"planet":"Void Colony","desc":"Flee costs 5×angst fuel instead of 20×. Void Colony only.",   "apply":lambda s: s.update({"booster":True})},
}

# ═══════════════════════════════════════════════════════════════════════════════
# PASSENGERS
# ═══════════════════════════════════════════════════════════════════════════════

PASSENGER_ROSTER = [
    {
        "shortname":    "Whitemaine",
        "fullname":     "Whitemaine, Pride Mercenary",
        "cantina_text": (
            "A large lion-like mercenary with two laser guns holstered on his back "
            "nurses a drink in the corner. He's looking for his lost cub — "
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
    if not ship.get("passenger_slot"): return
    if state.get("passenger_waiting"):  return
    if random.random() < 0.20:
        p = random.choice(PASSENGER_ROSTER).copy()
        p["destination"] = random.choice([pl for pl in PLANET_NAMES if pl != ship["location"]])
        state["passenger_waiting"] = p

def check_passenger_delivery(ship, state):
    p = ship.get("passenger")
    if p and p["destination"] == ship["location"]:
        print("\n" + "─"*50)
        print(p["exit_text"])
        ship["credits"] += 300
        print("  +300 credits received.")
        print("─"*50)
        ship["passenger"] = None

# ═══════════════════════════════════════════════════════════════════════════════
# PIRATES
# ═══════════════════════════════════════════════════════════════════════════════

def pirate_encounter(ship, state):
    state["piratangst"] += 1
    angst      = state["piratangst"]
    bribe_cost = state["piratbribe"]
    flee_mult  = 5 if ship.get("booster") else 20
    flee_cost  = max(0, min(flee_mult * angst, ship["fuel"] - MIN_FUEL_TO_DEPART))

    print("\n" + "⚠"*50)
    print(f"  PIRATE INTERCEPT!  (Angst level: {angst})")
    print("⚠"*50)
    print(f"\n  [1] Fight       (your weapons: {ship['weapons']})")
    print(f"  [2] Flee        (costs {flee_cost} fuel)")
    print(f"  [3] Bribe       ({bribe_cost} cr — rises each use)")
    print(f"  [4] Drop Cargo  (lose half of each good, min 1)")
    print(f"  [5] Bluff       (claim empty; auto-pass if cargo ≤10)")
    print(f"  [6] Surrender   (WARNING: ends your game)")

    return _pirate_resolve(ship, state, _get_int("Choose: ", 1, 6), exclude=None)

def _pirate_resolve(ship, state, choice, exclude):
    angst      = state["piratangst"]
    bribe_cost = state["piratbribe"]
    flee_mult  = 5 if ship.get("booster") else 20
    flee_cost  = max(0, min(flee_mult * angst, ship["fuel"] - MIN_FUEL_TO_DEPART))

    if choice == 1:
        pirate_power = max(1, angst // 20)
        state["piratangst"] += 2
        print(f"\n  Pirate power: {pirate_power}  vs  Your weapons: {ship['weapons']}")
        if ship["weapons"] < pirate_power:
            _drop_half_cargo(ship)
            print("  Outgunned! Lost half cargo, but you escape.")
        elif ship["weapons"] == pirate_power:
            print("  Standoff. The pirate backs off. You're known as 'The Porcupine'.")
        else:
            bounty = 100 * angst
            ship["credits"] += bounty
            state["piratangst"] += 3
            print(f"  Pirate scum obliterated! Bounty collected: {bounty:,} cr.")
        return True

    elif choice == 2:
        if ship["fuel"] - flee_cost < MIN_FUEL_TO_DEPART:
            print(f"  Not enough fuel to flee (need {flee_cost}). Choose again.")
            return _pirate_retry(ship, state, exclude=2)
        ship["fuel"] -= flee_cost
        print(f"  You gun the engines and escape! Fuel burned: {flee_cost}.")
        return True

    elif choice == 3:
        if ship["credits"] < bribe_cost:
            loss = ship["credits"]; ship["credits"] = 0
            print(f"  Can't afford bribe. They strip your last {loss} cr.")
        else:
            ship["credits"] -= bribe_cost
            state["piratangst"] = max(0, state["piratangst"] - 3)
            print(f"  You pay {bribe_cost} cr. They wave you through.")
        state["piratbribe"] += 100
        print(f"  Next bribe will cost {state['piratbribe']} cr.")
        return True

    elif choice == 4:
        if not ship["cargo"]:
            loss = min(200, ship["credits"]); ship["credits"] -= loss
            print(f"  Nothing to drop. They board and take {loss} cr.")
        else:
            _drop_half_cargo(ship)
            state["piratangst"] = max(0, state["piratangst"] - 2)
            print("  You jettison half cargo. Pirates scoop it and leave.")
        return True

    elif choice == 5:
        total = sum(ship["cargo"].values())
        if total <= 10:
            print("  'Nothing here, officer.' Auto-pass — hold was basically empty.")
        elif random.random() < 0.5:
            print("  Your poker face is legendary. The pirate warps off.")
        else:
            print("  They don't buy it. Bluff burned for this encounter.")
            state["piratangst"] += 2
            return _pirate_retry(ship, state, exclude=5)
        return True

    elif choice == 6:
        confirm = input("\n  Sure? You will be sold as a crypto miner on Zeta-9. [yes/no]: ").strip().lower()
        if confirm == "yes":
            print("\n  You're stripped of everything. Six months later you're mining")
            print("  blockchain hashes in a Zeta-9 server farm.")
            print("  The smell of saffron is the last thing you remember of freedom.")
            print("\n  ─── GAME OVER ───")
            return False
        else:
            print("  You reconsider.")
            return pirate_encounter(ship, state)
    return True

def _pirate_retry(ship, state, exclude):
    angst      = state["piratangst"]
    flee_mult  = 5 if ship.get("booster") else 20
    flee_cost  = max(0, min(flee_mult * angst, ship["fuel"] - MIN_FUEL_TO_DEPART))
    opts = []
    if exclude != 1: opts.append(("1", f"Fight (weapons:{ship['weapons']})"))
    if exclude != 2: opts.append(("2", f"Flee ({flee_cost} fuel)"))
    if exclude != 3: opts.append(("3", f"Bribe ({state['piratbribe']} cr)"))
    if exclude != 4: opts.append(("4", "Drop Cargo"))
    if exclude != 5: opts.append(("5", "Bluff"))
    opts.append(("6", "Surrender (GAME OVER)"))
    print()
    for k, lbl in opts: print(f"  [{k}] {lbl}")
    valid = [k for k, _ in opts]
    while True:
        raw = input("Choose: ").strip()
        if raw in valid:
            return _pirate_resolve(ship, state, int(raw), exclude=exclude)
        print(f"  Choose from: {', '.join(valid)}")

def _drop_half_cargo(ship):
    for good in list(ship["cargo"].keys()):
        drop = max(1, math.ceil(ship["cargo"][good] / 2))
        ship["cargo"][good] -= drop
        if ship["cargo"][good] <= 0: del ship["cargo"][good]
        print(f"  Dropped {drop}× {good}.")

# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

def _ev_festival(ship, state, dest):
    for good in state["planets"][dest]["base_prices"]:
        state["planets"][dest]["base_prices"][good] = int(
            state["planets"][dest]["base_prices"][good] * 1.1)
    print(f"🎉 SPICE FESTIVAL on {dest}! All prices +10%.")

def _ev_fuel_leak(ship, state, dest):
    lost = random.randint(15, 35)
    ship["fuel"] = max(0, ship["fuel"] - lost)
    print(f"🔧 FUEL LEAK mid-jump. Lost {lost} fuel.")

def _ev_mystery_cargo(ship, state, dest):
    free = ship["max_cargo"] - sum(ship["cargo"].values())
    if free >= 5:
        ship["cargo"]["Mystery Crate"] = ship["cargo"].get("Mystery Crate", 0) + 5
        print("📦 Drifting cargo pod attached. +5 Mystery Crate.")
    else:
        print("📦 Drifting cargo pod — no room. It drifts on.")

NON_PIRATE_EVENTS = [
    (0.12, _ev_festival),
    (0.10, _ev_fuel_leak),
    (0.08, _ev_mystery_cargo),
]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_int(prompt, lo=None, hi=None):
    while True:
        try:
            val = int(input(prompt))
            if lo is not None and val < lo: print(f"  ≥ {lo} please."); continue
            if hi is not None and val > hi: print(f"  ≤ {hi} please."); continue
            return val
        except ValueError:
            print("  Enter a number.")

def _col(text, width): return str(text).ljust(width)
def _cargo_used(ship): return sum(ship["cargo"].values())
def _cargo_free(ship): return ship["max_cargo"] - _cargo_used(ship)

def _travel_fuel_cost(origin, destination):
    i = PLANET_NAMES.index(origin)
    j = PLANET_NAMES.index(destination)
    return max(10, min(50, abs(i-j) * 12 + random.randint(-5, 5)))

# ═══════════════════════════════════════════════════════════════════════════════
# NEWS FEED
# ═══════════════════════════════════════════════════════════════════════════════

def print_news(ship, state):
    """Print once per planet visit. Caller sets state['news_printed']=True."""
    loc = ship["location"]
    m   = state["month_index"]
    lines = []

    # Traveler notice (only if passenger_slot installed)
    if ship.get("passenger_slot"):
        pw = state.get("passenger_waiting")
        if pw:
            lines.append(f"  📋 Traveler waiting in the Promenade Cantina: {pw['shortname']} → {pw['destination']}")

    # Festival notice (only on this planet this month)
    if loc in PLANET_FESTIVALS:
        good, fest_month, fest_name, _ = PLANET_FESTIVALS[loc]
        if m == fest_month:
            lines.append(f"  🎊 Join the {fest_name} on {loc} this {month_name(m)}! Let the fun begin!")

    # Harvest notice (always one good)
    harvest_good = current_harvest_good(m)
    if harvest_good:
        lines.append(f"  🌾 {harvest_good} harvest in full swing this {month_name(m)}. Fill your hold while yields last.")

    if lines:
        print("\n" + "─"*50)
        for line in lines: print(line)
        print("─"*50)

    state["news_printed"] = True

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def show_status(ship, state):
    print("\n" + "═"*52)
    print(f"  STATUS  —  {date_str(state)}  (turn {state['turn']})")
    print("═"*52)
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
    if ship.get("broker_license"):  extras.append("Broker License")
    if ship.get("radar"):           extras.append("Radar")
    if ship.get("booster"):         extras.append("Booster")
    if ship.get("passenger_slot"):
        p = ship.get("passenger")
        extras.append(f"Passenger: {p['shortname']} → {p['destination']}" if p else "Passenger slot (empty)")
    if extras: print(f"  Upgrades : {', '.join(extras)}")
    if ship["location"] == "Terra" and ship.get("farm_bought"):
        print("  🌿 You own a cinnamon farm on Terra.")
    print("═"*52)

def show_market(ship, state):
    planet_name = ship["location"]
    planet      = state["planets"][planet_name]

    print(f"\n── MARKET: {planet_name} ──────────────────────────────────")
    print(f"  {'Good':<18} {'Sell':>6} {'Buy':>6}  {'Role'}")
    print(f"  {'─'*18} {'─'*6} {'─'*6}  {'─'*12}")
    for good in planet["spices"]:
        sp   = sell_price(state, planet_name, good)
        bp   = buy_price(state, planet_name, good)
        role = ""
        if good == planet["production"]: role = "◀ PRODUCTION"
        elif good == planet["demand"]:   role = "▶ DEMAND"
        print(f"  {good:<18} {sp:>6} {bp:>6}  {role}")
    print()
    print("  [1] Buy   [2] Sell   [3] Travel")
    print("  [4] Status   [5] Price Check   [6] Promenade")
    print("  [8] Engineering Bay   [9] Save   [0] Quit")

# ═══════════════════════════════════════════════════════════════════════════════
# TRADE
# ═══════════════════════════════════════════════════════════════════════════════

def do_buy(ship, state):
    planet_name = ship["location"]
    planet      = state["planets"][planet_name]
    if _cargo_free(ship) == 0:
        print("Cargo hold is full!"); return
    spices = planet["spices"]
    print("\n── BUY ──────────────────────────────────────────────")
    for i, good in enumerate(spices, 1):
        bp = buy_price(state, planet_name, good)
        print(f"  [{i}] {good:<18} {bp:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose good: ", 0, len(spices))
    if choice == 0: return
    good  = spices[choice-1]
    bp    = buy_price(state, planet_name, good)
    max_b = min(ship["credits"] // bp, _cargo_free(ship))
    if max_b <= 0:
        print("Not enough credits or cargo space!"); return
    amount = _get_int(f"How many {good}? (0 cancel, max {max_b}): ", 0, max_b)
    if amount == 0: return
    ship["credits"] -= amount * bp
    ship["cargo"][good] = ship["cargo"].get(good, 0) + amount
    print(f"✓ Bought {amount}× {good} for {amount*bp:,} cr.")

def do_sell(ship, state):
    if not ship["cargo"]:
        print("Cargo hold is empty!"); return
    planet_name = ship["location"]
    cargo_items = list(ship["cargo"].items())
    print("\n── SELL ─────────────────────────────────────────────")
    for i, (good, qty) in enumerate(cargo_items, 1):
        sp = sell_price(state, planet_name, good)
        print(f"  [{i}] {good:<18} {qty:>4} units @ {sp:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose good: ", 0, len(cargo_items))
    if choice == 0: return
    good, available = cargo_items[choice-1]
    sp     = sell_price(state, planet_name, good)
    amount = _get_int(f"How many {good}? (max {available}): ", 1, available)
    gross  = amount * sp
    tax    = max(1, math.ceil(gross * 0.02))
    net    = gross - tax
    ship["credits"] += net
    ship["cargo"][good] -= amount
    if ship["cargo"][good] <= 0: del ship["cargo"][good]
    print(f"✓ Sold {amount}× {good} for {gross:,} cr.  Tax: {tax} cr.  Net: {net:,} cr.")

# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL
# ═══════════════════════════════════════════════════════════════════════════════

def do_travel(ship, state):
    if ship["fuel"] < MIN_FUEL_TO_DEPART:
        print(f"Need ≥{MIN_FUEL_TO_DEPART} fuel to depart. Refuel in Engineering Bay.")
        return
    other = [p for p in PLANET_NAMES if p != ship["location"]]
    print("\n── TRAVEL ───────────────────────────────────────────")
    for i, planet in enumerate(other, 1):
        cost = _travel_fuel_cost(ship["location"], planet)
        print(f"  [{i}] {planet:<16}  ~{cost} fuel")
    print("  [0] Cancel")
    choice = _get_int("Destination: ", 0, len(other))
    if choice == 0: return
    destination = other[choice-1]
    fuel_cost   = _travel_fuel_cost(ship["location"], destination)
    if ship["fuel"] - fuel_cost < MIN_FUEL_TO_DEPART:
        print(f"Not enough fuel. Need {fuel_cost}+{MIN_FUEL_TO_DEPART} reserve. Have {ship['fuel']}.")
        return

    random.seed(fetch_remote_seed())
    ship["fuel"]     -= fuel_cost
    ship["location"]  = destination
    state["news_printed"] = False   # reset news for new planet
    advance_time(state)
    print(f"\n🚀 Jumped to {destination}. Fuel used: {fuel_cost}. Date: {date_str(state)}")

    planet = state["planets"][destination]
    for good in planet["base_prices"]:
        if good not in (planet["production"], planet["demand"]):
            planet["base_prices"][good] = _clamp_base(
                good, planet["base_prices"][good] + random.randint(-5, 5))
    random.seed()

    pirate_chance = 0.10 if ship.get("radar") else 0.25
    if random.random() < pirate_chance:
        alive = pirate_encounter(ship, state)
        if not alive: return "GAME_OVER"
    else:
        roll = random.random(); cum = 0.0
        for prob, fn in NON_PIRATE_EVENTS:
            cum += prob
            if roll < cum:
                fn(ship, state, destination); break

    check_passenger_delivery(ship, state)
    maybe_spawn_passenger(ship, state)

# ═══════════════════════════════════════════════════════════════════════════════
# PRICE CHECK (broker license required)
# ═══════════════════════════════════════════════════════════════════════════════

def do_price_check(ship, state):
    if not ship.get("broker_license"):
        print("\n  Access denied. You need a Galactic Broker License.")
        print("  Head to Nexus to purchase one. Maybe sell the ship to afford it.")
        return
    W = [14, 16, 7, 7, 7, 12]
    header = (f"  {_col('Planet',W[0])} {_col('Good',W[1])} "
              f"{_col('Base',W[2])} {_col('Sell',W[3])} {_col('Buy',W[4])} {_col('Role',W[5])}")
    sep = "  " + "─"*(sum(W)+5)
    print("\n── PRICE CHECK (ALL PLANETS) ────────────────────────")
    print(header); print(sep)
    for pn in PLANET_NAMES:
        planet = state["planets"][pn]
        for good in planet["spices"]:
            base = planet["base_prices"][good]
            sp   = sell_price(state, pn, good)
            bp   = buy_price(state, pn, good)
            role = ""
            if good == planet["production"]: role = "PRODUCTION"
            elif good == planet["demand"]:   role = "DEMAND"
            print(f"  {_col(pn,W[0])} {_col(good,W[1])} "
                  f"{_col(base,W[2])} {_col(sp,W[3])} {_col(bp,W[4])} {_col(role,W[5])}")
        print(sep)

# ═══════════════════════════════════════════════════════════════════════════════
# FARM
# ═══════════════════════════════════════════════════════════════════════════════

def visit_farm(ship, state):
    while True:
        print("\n" + "="*50)
        print(random.choice(state["planets"]["Terra"]["farm_fluff"]))
        print("="*50)
        print("  [1] Stay a little longer   [2] Return to the stars")
        c = input("Choose: ").strip()
        if c == "2":
            print("You leave the farm, ready to face the galaxy again."); break

# ═══════════════════════════════════════════════════════════════════════════════
# CANTINA
# ═══════════════════════════════════════════════════════════════════════════════

def visit_cantina(ship, state):
    cantina = cantinas[ship["location"]]
    while True:
        pw = state.get("passenger_waiting")
        has_quoters = ship.get("passenger_slot", False)

        print(f"\n── {cantina['name'].upper()} ({ship['location']}) ───────────────────")
        print("  [1] I need a drink")
        print("  [2] Ask for advice")
        if has_quoters:
            traveler_tag = f"{pw['shortname']} → {pw['destination']}" if pw else "(none)"
            print(f"  [3] Traveler — {traveler_tag}")
        print("  [4] Rest for a while  (1 month passes)")
        print("  [9] Back to Promenade")
        choice = input("Choose: ").strip()

        if choice == "1":
            drink = cantina["drink"]
            price = sell_price(state, ship["location"], drink["ingredient"])
            dc    = max(1, int(price * 0.5))
            if ship["credits"] < dc:
                print(f"  Can't afford a {drink['name']} ({dc} cr).")
            else:
                ship["credits"] -= dc
                print(f"\n  You buy a {drink['name']} for {dc} cr.")
                print(f"  {random.choice(drink['fluff'])}")

        elif choice == "2":
            pool   = random.choice(list(advice_pools.keys()))
            advice = random.choice(advice_pools[pool])
            print(f"\n  [Bartender — {pool.upper()}]: {advice}")

        elif choice == "3":
            if not has_quoters:
                print("  Invalid choice.")
            elif not pw:
                print("  Nobody looking for a ride right now.")
            else:
                print(f"\n  {pw['fullname']}")
                print(f"  {pw['cantina_text']}")
                print(f"  Destination: {pw['destination']}")
                if ship.get("passenger"):
                    print(f"  (Replacing {ship['passenger']['shortname']} — they will be left here.)")
                if input("  Take them aboard? [y/n]: ").strip().lower() == "y":
                    ship["passenger"] = pw
                    state["passenger_waiting"] = None
                    print(f"  {pw['shortname']} boards your ship.")

        elif choice == "4":
            print("\n" + "─"*50)
            print("  You spend a month in the cantina. The days blur together.")
            if state["galaxy_story_index"] < len(galaxy_story):
                print(f"\n  [GALAXY NEWS]: {galaxy_story[state['galaxy_story_index']]}")
                state["galaxy_story_index"] += 1
            else:
                print("  The galaxy turns, quietly.")
            print("─"*50)
            input("  [Enter to continue...]")
            advance_time(state)
            maybe_spawn_passenger(ship, state)
            print(f"  Date is now: {date_str(state)}")

        elif choice == "9":
            break
        else:
            print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# INFOBROKER TABLES
# ═══════════════════════════════════════════════════════════════════════════════

def infobroker_goods_table():
    data = [
        ("Allspice",    "Terra, Agrica, Nexus",           "—",           "Terra"),
        ("Cardamom",    "Terra, Agrica, Void Colony",      "—",           "Void Colony"),
        ("Cinnamon",    "Terra, Zeta-9, Agrica",           "Terra",       "—"),
        ("Clove",       "Terra, Void Colony, Nexus",       "Nexus",       "—"),
        ("Ginger",      "Terra, Zeta-9, Void Colony",      "—",           "Zeta-9"),
        ("Nutmeg",      "Zeta-9, Agrica, Nexus",           "—",           "—"),
        ("Paprika",     "Terra, Zeta-9, Agrica",           "Agrica",      "—"),
        ("Saffron",     "Zeta-9, Void Colony, Nexus",      "Zeta-9",      "—"),
        ("Turmeric",    "Zeta-9, Agrica, Nexus",           "—",           "Nexus"),
        ("Vanilla",     "Terra, Void Colony, Agrica",      "—",           "Agrica"),
        ("Void Pepper", "Void Colony, Nexus",              "Void Colony", "—"),
    ]
    W = [14, 30, 14, 14]
    sep = "  +" + "+".join("-"*w for w in W) + "+"
    print("\n── INFOBROKER: GOODS DIRECTORY ─────────────────────")
    print(sep)
    print("  |" + "Good".ljust(W[0]) + "|" + "Planets".ljust(W[1]) + "|" + "Production".ljust(W[2]) + "|" + "Demand".ljust(W[3]) + "|")
    print(sep)
    for row in data:
        print("  |" + row[0].ljust(W[0]) + "|" + row[1].ljust(W[1]) + "|" + row[2].ljust(W[2]) + "|" + row[3].ljust(W[3]) + "|")
    print(sep)

def infobroker_harvest_table():
    data = [
        ("Cinnamon",    1,  "Ianu",  "Low"),
        ("Turmeric",    2,  "Febu",  "Low"),
        ("Paprika",     3,  "Mari",  "Low"),
        ("Ginger",      4,  "Aprix", "Mid"),
        ("Clove",       5,  "Maiu",  "Mid"),
        ("Vanilla",     6,  "Iuin",  "Mid"),
        ("Cardamom",    7,  "Septr", "Mid"),
        ("Allspice",    8,  "Octo",  "High"),
        ("Saffron",     9,  "Nova",  "High"),
        ("Nutmeg",      10, "Dedl",  "High"),
        ("Void Pepper", "—","—",     "None — no harvest cycle"),
    ]
    W = [14, 4, 7, 26]
    sep = "  +" + "+".join("-"*w for w in W) + "+"
    print("\n── INFOBROKER: HARVEST SEASONS ─────────────────────")
    print(sep)
    print("  |" + "Good".ljust(W[0]) + "|" + "Mo#".ljust(W[1]) + "|" + "Month".ljust(W[2]) + "|" + "Season Pattern".ljust(W[3]) + "|")
    print(sep)
    for row in data:
        print("  |" + str(row[0]).ljust(W[0]) + "|" + str(row[1]).ljust(W[1]) + "|" + str(row[2]).ljust(W[2]) + "|" + str(row[3]).ljust(W[3]) + "|")
    print(sep)
    print("  Low:  prices rise slowly after harvest (+20 peak at anti-harvest).")
    print("  Mid:  prices dip at harvest (-20), peak 5mo later (+20).")
    print("  High: prices dip hard at harvest (-20), peak 5mo later (+50).")

def infobroker_festival_table():
    data = [
        ("Terra",       3,  "Mari",  "Cinnamon Roll Festival",  "Cinnamon"),
        ("Agrica",      4,  "Aprix", "Paprika Panic Parade",    "Paprika"),
        ("Zeta-9",      6,  "Iuin",  "Golden Ginger Gala",      "Ginger"),
        ("Void Colony", 8,  "Octo",  "Void Vanilla Vigil",      "Vanilla"),
        ("Nexus",       10, "Dedl",  "Allspice Arbitrage Fête", "Allspice"),
    ]
    W = [13, 4, 7, 26, 12]
    sep = "  +" + "+".join("-"*w for w in W) + "+"
    print("\n── INFOBROKER: FESTIVAL CALENDAR ───────────────────")
    print(sep)
    print("  |" + "Planet".ljust(W[0]) + "|" + "Mo#".ljust(W[1]) + "|" + "Month".ljust(W[2]) + "|" + "Festival".ljust(W[3]) + "|" + "Good".ljust(W[4]) + "|")
    print(sep)
    for row in data:
        print("  |" + str(row[0]).ljust(W[0]) + "|" + str(row[1]).ljust(W[1]) + "|" + str(row[2]).ljust(W[2]) + "|" + str(row[3]).ljust(W[3]) + "|" + str(row[4]).ljust(W[4]) + "|")
    print(sep)
    print("  Note: festival month = price spike. Following month = price drop.")

def visit_infobroker(ship, state):
    while True:
        print("\n── INFOBROKER ───────────────────────────────────────")
        print("  [1] Goods Directory")
        print("  [2] Harvest Seasons")
        print("  [3] Festival Calendar")
        print("  [9] Back to Promenade")
        choice = input("Choose: ").strip()
        if choice == "1": infobroker_goods_table()
        elif choice == "2": infobroker_harvest_table()
        elif choice == "3": infobroker_festival_table()
        elif choice == "9": break
        else: print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# CONCERT HALL
# ═══════════════════════════════════════════════════════════════════════════════

def visit_concert(ship, state):
    TICKET = 10
    if ship["credits"] < TICKET:
        print(f"\n  Ticket costs {TICKET} cr. You're too broke for culture right now.")
        return
    ship["credits"] -= TICKET
    print(f"\n  You pay {TICKET} cr and take your seat...")

    try:
        with open(SONGS_FILE, encoding="utf-8") as f:
            songs_data = json.load(f)
        songs = songs_data.get("songs", [])
        if not songs:
            raise ValueError("empty")
        song = random.choice(songs)

        print("\n" + "★"*52)
        print(f"  NOW PLAYING: {song.get('fullname', song.get('shortname', 'Unknown'))}")
        print("★"*52)
        print()
        print(song.get("text", "(no lyrics found)"))
        if song.get("art"):
            print()
            print(song["art"])
        print("\n" + "★"*52)

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        ship["credits"] += TICKET   # refund
        print("\n  The stage is empty.")
        print("  A stagehand appears and clears their throat:")
        print("  \"The artist was stopped on the Hyperlanes by pirates.")
        print("   We all pray for their swift recovery and near comeback.\"")
        print(f"  Your {TICKET} cr ticket has been refunded.")

# ═══════════════════════════════════════════════════════════════════════════════
# PROMENADE
# ═══════════════════════════════════════════════════════════════════════════════

def visit_promenade(ship, state):
    loc = ship["location"]
    while True:
        print(f"\n── PROMENADE  —  {loc} ──────────────────────────────")
        print("  [1] Cantina")
        print("  [2] Infobroker")
        print("  [3] Concert Hall  [10 cr]")
        if loc == "Terra":
            if ship.get("farm_bought"):
                print("  [f] Visit Your Cinnamon Farm")
            else:
                print("  [f] Buy Cinnamon Farm  [10,000 cr]")
        print("  [0] Back to Spaceport")
        choice = input("Choose: ").strip().lower()

        if choice == "1":
            visit_cantina(ship, state)
        elif choice == "2":
            visit_infobroker(ship, state)
        elif choice == "3":
            visit_concert(ship, state)
        elif choice == "f" and loc == "Terra":
            if not ship.get("farm_bought"):
                print(f"\n  Buy a cinnamon farm for 10,000 cr? (You have {ship['credits']:,})")
                if ship["credits"] >= 10000:
                    if input("  Confirm [y/n]: ").strip().lower() == "y":
                        ship["credits"] -= 10000
                        ship["farm_bought"] = True
                        print("  🌿 You now own a cinnamon farm on Terra.")
                else:
                    print(f"  Need {10000 - ship['credits']:,} more credits.")
            else:
                visit_farm(ship, state)
        elif choice == "0":
            break
        else:
            print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# ENGINEERING BAY  (stays on spaceport)
# ═══════════════════════════════════════════════════════════════════════════════

def visit_engineering_bay(ship, state):
    while True:
        print("\n── ENGINEERING BAY ──────────────────────────────────")
        print(f"  Fuel: {ship['fuel']} / {ship['max_fuel']}  |  Credits: {ship['credits']:,}")
        print("  [1] Fuel Up")
        print("  [2] Drain Fuel")
        print("  [3] Upgrades")
        print("  [9] Back")
        choice = input("Choose: ").strip()
        if choice == "1":   _fuel_up(ship)
        elif choice == "2": _drain_fuel(ship)
        elif choice == "3": _upgrades_menu(ship, state)
        elif choice == "9": break
        else: print("Invalid choice.")

def _fuel_up(ship):
    space = ship["max_fuel"] - ship["fuel"]
    if space <= 0: print("Tank is full."); return
    print(f"\n  Fuel: {FUEL_PRICE} cr/unit. Space: {space}")
    raw  = [100, 200, 500, 1000]
    disp = []
    seen = set()
    for n in raw + [space]:
        amt = min(n, space)
        if amt > 0 and amt not in seen:
            seen.add(amt); disp.append(amt)
    for i, amt in enumerate(disp, 1):
        label = "FULL" if amt == space else str(amt)
        print(f"  [{i}] +{label} fuel  →  {amt*FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(disp))
    if c == 0: return
    amt  = disp[c-1]
    cost = amt * FUEL_PRICE
    if ship["credits"] < cost:
        print(f"  Not enough credits. Need {cost:,}, have {ship['credits']:,}."); return
    ship["credits"] -= cost
    ship["fuel"]     = min(ship["max_fuel"], ship["fuel"] + amt)
    print(f"✓ Fuelled +{amt}. Tank: {ship['fuel']}/{ship['max_fuel']}")

def _drain_fuel(ship):
    drainable = ship["fuel"] - MIN_FUEL_TO_DEPART
    if drainable <= 0:
        print(f"  Must keep ≥{MIN_FUEL_TO_DEPART} fuel. Nothing to drain."); return
    print(f"\n  Drainable: {drainable} units → up to {drainable*FUEL_PRICE:,} cr")
    raw  = [100, 200, 500, 1000, int(ship["fuel"] * 0.9)]
    opts = sorted(set(min(n, drainable) for n in raw if 0 < n <= drainable))
    for i, amt in enumerate(opts, 1):
        label = "90%" if amt == int(ship["fuel"]*0.9) else str(amt)
        print(f"  [{i}] Drain {label}  →  +{amt*FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(opts))
    if c == 0: return
    amt = opts[c-1]
    ship["fuel"]    -= amt
    ship["credits"] += amt * FUEL_PRICE
    print(f"✓ Drained {amt} fuel. Tank: {ship['fuel']}/{ship['max_fuel']}. Gained {amt*FUEL_PRICE:,} cr.")

def _upgrades_menu(ship, state):
    loc = ship["location"]
    available = [(uid, u) for uid, u in UPGRADES.items()
                 if (u["planet"] is None or u["planet"] == loc)
                 and uid not in ship["upgrades_bought"]]
    print(f"\n── UPGRADES  ({loc}) ──────────────────────────────")
    if not available:
        print("  No upgrades available here (or all purchased)."); return
    for i, (uid, u) in enumerate(available, 1):
        tag = f" [{u['planet']} only]" if u["planet"] else ""
        print(f"  [{i}] {u['name']}  —  {u['cost']:,} cr{tag}")
        print(f"       {u['desc']}")
    print("  [0] Cancel")
    c = _get_int("Choose upgrade: ", 0, len(available))
    if c == 0: return
    uid, u = available[c-1]
    if ship["credits"] < u["cost"]:
        print(f"  Not enough credits. Need {u['cost']:,}, have {ship['credits']:,}."); return
    ship["credits"] -= u["cost"]
    u["apply"](ship)
    ship["upgrades_bought"].append(uid)
    print(f"✓ {u['name']} installed.")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════════════

def save_game(ship, state):
    data = {
        "ship": {k: v for k, v in ship.items()},
        "planets_prices": {n: {"base_prices": p["base_prices"]} for n, p in state["planets"].items()},
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
        with open(SAVE_FILE, "w") as f: json.dump(data, f, indent=2)
        print(f"💾 Saved to {SAVE_FILE}")
    except OSError as e:
        print(f"⚠️  Save failed: {e}")

def load_game(planets, state):
    if not os.path.exists(SAVE_FILE): return None
    try:
        with open(SAVE_FILE) as f: data = json.load(f)
        for name, pdata in data["planets_prices"].items():
            if name in planets: planets[name]["base_prices"].update(pdata["base_prices"])
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
        print(f"⚠️  Load failed: {e}"); return None

# ═══════════════════════════════════════════════════════════════════════════════
# SONGS FILE  (created on first run if missing — gives the player a hint)
# ═══════════════════════════════════════════════════════════════════════════════

SONG_EVENT_HORIZON = {
    "shortname": "eventhor",
    "fullname":  "Event Horizon",
    "text": """\
[Intro]
They say we're drifting in the dark
A spiral sunk beyond the mark
No light escapes, no truth gets through
Just echoes of what stars once knew

This ain't the place they write in songs
No rising arc, no right from wrong
Just quiet weight, a silent hum
Where dreams go still, and futures (numb)

[Verse]
The sky's a wall of starless sleep
We orbit silence, cold and deep
No ladder climbs, no prayers reply
The universe forgot to (try)

[Verse]
This isn't hell, but not quite home
A waiting room with monochrome
Where every plan dissolves in time
And hope gets rusted, out of (line)

[Chorus]
But still I hang up fairy lights
In corners where there's barely nights
I plant my cactus in a can
And hum a song where none began
The void won't love me, this I know—
But damn it, I will (make it glow)

[Verse]
No hero arc, no breakthrough scene
No golden gate or field of green
Just coffee cold and half-paid rent
And tired hands that won't (relent)

[Verse]
They say this hole will birth the next
A black hole's child, a new context
But who will feel that newborn spark?
We're trapped in here, and it's still (dark)

[Bridge]
Some say to wait for rescue beams
But I've outlived a thousand dreams
So I just sweep this crater floor
And try to hope a little (more)

[Chorus]
But still I hang up fairy lights
In corners where there's barely nights
I plant my cactus in a can
And hum a song where none began
The void won't love me, this I know—
But damn it, I will (make it glow)

[Verse]
I rearrange the broken parts
Make space for books and open hearts
I water hope, though roots stay dry
And watch the ceiling, whisper (why?)

[Verse]
I'll never touch another sky
But I still try, and I still try
To cook a meal, to write a joke
To find a reason not to (choke)

[Chorus]
But still I hang up fairy lights
In corners where there's barely nights
I plant my cactus in a can
And hum a song where none began
The void won't love me, this I know—
But damn it, I will (make it glow)

[Outro]
So here I stay, beneath the weight
No grand escape, no twist of fate
Just quiet fights and stubborn cheer—
I'll build a home inside this (sphere)

[End]
I light a match, I breathe the grey
I make a bed where pain can lay
The black hole hums, and I reply—
"I'm here. I live. I (still) defy." """,
    "art": """\
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠖⠃⠀⠀⠀⡁⠀⠀⠀⠀⠀⠐⠆⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠁⠀⠀⠀⠘⠁⢀⠀⠀⠀⠀⢈⠓⠂⠠⡄⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠒⠁⠀⠠⡚⠁⢀⣙⣀⣈⡩⠬⢁⠀⢑⠶⠤⡆⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⢠⠀⠀⣶⠃⠗⣡⣶⣮⣿⡿⠿⠿⢿⣿⣷⣶⣤⣤⠤⠴⠦⠬⣤⣤⠄⣉⠉⠝⢲
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠁⡀⡸⠁⣰⣿⡿⠛⠋⣁⡀⠤⠤⢄⡀⠈⠛⢯⣿⣟⣾⣶⣶⣮⣭⣵⣾⣿⣟⠿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⢠⠳⡧⣻⡿⠋⢀⠒⠉⠀⠀⠀⠀⠀⠀⠉⠢⠀⠀⠙⠛⣻⣿⣿⣿⢿⣿⣿⠟⡱
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⢠⣧⠓⣾⣿⠁⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢦⣠⣾⣿⠿⣿⣿⣿⡿⣫⠏⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠂⢃⣸⣿⠇⢠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣿⠟⢿⠁⠸⡿⣿⣯⡶⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⢀⡴⢯⣾⠟⡏⢀⣠⣿⣿⣿⣟⢟⡋⠅⠘⠉⠀⠀⠀⠀⢀⠀⠁⢠⣿⣟⠃⠀⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⣻⣷⡿⢙⣩⣶⡿⠿⠛⠉⠑⢡⡁⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⣰⣿⣿⡟⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⣾⣥⣾⢫⡦⠾⠛⠙⠉⠀⠀⢀⣀⠀⠈⠙⠓⠦⠤⠤⠀⠘⠁⢀⡤⣾⡿⠏⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠔⣴⣾⣿⣿⢟⢝⠢⠃⢀⣤⢴⣾⣮⣷⣶⢿⣶⡤⣐⡀⠀⣠⣤⢶⣪⣿⣿⡿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡀⣦⣾⡿⡛⠵⠺⢈⡠⠶⠿⠥⠥⡭⠉⠉⢱⡛⠻⠿⣿⣿⣿⣿⣿⠿⠿⠿⠟⠭⠛⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⢴⠕⣋⠝⠕⠐⠀⠔⠉⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠉⠁⠁⠁⠁⠈⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⣠⠁⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""
}

def ensure_songs_file():
    """Write songs.json if it doesn't exist yet."""
    if not os.path.exists(SONGS_FILE):
        try:
            with open(SONGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"songs": [SONG_EVENT_HORIZON]}, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # silently continue — concert will just refund

# ═══════════════════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════════════════

def init_planets():
    planets = {}
    for pname, pdata in planets_template.items():
        new_prices = {}
        for good, price in pdata["base_prices"].items():
            if good in (pdata["production"], pdata["demand"]):
                new_prices[good] = price
            else:
                new_prices[good] = _clamp_base(good, price + random.randint(-10, 10))
        planets[pname] = {**pdata, "base_prices": new_prices}
    planets["Terra"]["farm_fluff"] = [
        "You sit on the porch of your cinnamon farm. The sunset paints the orchard in gold.",
        "The cinnamon trees rustle. A neighbor waves. 'Harvest was good this year.'",
        "The scent of cinnamon fills the air. No fuel calculations. No pirate attacks. Just peace.",
    ]
    return planets

def new_ship():
    return {
        "credits": 1000, "cargo": {}, "location": "Terra",
        "fuel": 500, "max_fuel": 500, "max_cargo": 100,
        "farm_bought": False, "weapons": 0,
        "broker_license": False, "passenger_slot": False,
        "passenger": None, "radar": False, "booster": False,
        "upgrades_bought": [],
    }

def new_state(planets):
    return {
        "planets": planets, "turn": 1, "month_index": 0, "year": 2201,
        "piratangst": 10, "piratbribe": 100,
        "galaxy_story_index": 0, "passenger_waiting": None,
        "festival_drops_applied": set(),
        "news_printed": False,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    ensure_songs_file()
    planets = init_planets()
    state   = new_state(planets)

    print("═"*55)
    print("  SPICE SPACE TRADER  v9")
    print("  Trade spices. Dodge pirates. Maybe buy a farm.")
    print("═"*55)

    if os.path.exists(SAVE_FILE):
        ans = input("\nSave file found. Load it? [y/n]: ").strip().lower()
        if ans == "y":
            loaded = load_game(planets, state)
            ship   = loaded if loaded else new_ship()
        else:
            ship = new_ship()
    else:
        ship = new_ship()

    while True:
        # News feed — once per planet visit
        if not state.get("news_printed"):
            print_news(ship, state)

        show_status(ship, state)
        show_market(ship, state)

        raw = input("\nChoose action: ").strip()

        # Cheat code
        if raw.startswith("!credits "):
            try: ship["credits"] += int(raw.split()[1])
            except (ValueError, IndexError): pass
            continue

        try:
            action = int(raw)
        except ValueError:
            print("Enter a number (or 'f' inside Promenade for farm)."); continue

        if action == 0:
            print(f"\nFinal credits: {ship['credits']:,}  |  Date: {date_str(state)}")
            if ship.get("farm_bought"):
                print("You retired to your cinnamon farm. You won. 🌿")
            break
        elif action == 1: do_buy(ship, state)
        elif action == 2: do_sell(ship, state)
        elif action == 3:
            result = do_travel(ship, state)
            if result == "GAME_OVER": break
        elif action == 4: show_status(ship, state)
        elif action == 5: do_price_check(ship, state)
        elif action == 6: visit_promenade(ship, state)
        elif action == 8: visit_engineering_bay(ship, state)
        elif action == 9: save_game(ship, state)
        else: print("Invalid action.")

if __name__ == "__main__":
    main()
