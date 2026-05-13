"""
=============================================================
  SPICE SPACE TRADER — game.py
=============================================================
  Run this file to play: python game.py

  File structure:
    game.py        — engine, menus, game loop (this file)
    parameters.py  — all balance numbers and data tables
    library.py     — all text content and display helpers
    songs.py       — song content (source of truth for songs.json)

=============================================================
  Changelog
=============================================================

v10
  + Split into 4 files: game.py / parameters.py / library.py / songs.py
  + UPGRADE_EFFECTS dict in game.py holds apply-lambdas (logic)
  + UPGRADES_DATA in parameters.py holds name/cost/planet/desc (balance)
  + library.py infobroker tables pull data from parameters (no duplication)
  + News feed uses string templates from library.py
  + songs.py is content-only; game.py does all songs.json file handling
  + All balance constants centralised in parameters.py

v9
  + Farm → [f] key; Promenade added as [6]
  + Cantina, Infobroker, Concert Hall under Promenade
  + Price Spread: Sell/Buy columns (mean ± spread per category)
  + GOOD_DATA bounds table; prices clamped per good
  + News feed (once per planet visit)
  + songs.json concert system with graceful refund on missing file
  + Paprika corrected to low pattern; Allspice base 120 on Terra

v8.1  Clove→40 on Void Colony; Allspice festival high; Void Torpedo +2
v8    Calendar, extra goods, tax, inflation, harvest, festivals,
      Engineering Bay, upgrades, Broker License, passengers, pirates v2,
      cheat code, save/load
v7    requests hook, dict events, fuel/cargo split, recursion fixes,
      input validation, columnar prices, JSON save, distance travel
v6    Original: trade loop, cantina, farm win condition
=============================================================
"""

import random
import json
import math
import os

import parameters as P
import library    as L

try:
    import requests as _requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE EFFECTS  — logic side of upgrades (balance data lives in parameters)
# ═══════════════════════════════════════════════════════════════════════════════

UPGRADE_EFFECTS = {
    "kinetic_launcher":  lambda ship: ship.update({"weapons":        ship["weapons"]  + 1}),
    "mining_laser":      lambda ship: ship.update({"weapons":        ship["weapons"]  + 1}),
    "void_torpedo":      lambda ship: ship.update({"weapons":        ship["weapons"]  + 2}),
    "stern_tank":        lambda ship: ship.update({"max_fuel":       ship["max_fuel"] + 200}),
    "portside_tank":     lambda ship: ship.update({"max_fuel":       ship["max_fuel"] + 300}),
    "cylindrical_tank":  lambda ship: ship.update({"max_fuel":       ship["max_fuel"] + 500}),
    "small_hold":        lambda ship: ship.update({"max_cargo":      ship["max_cargo"]+ 100}),
    "side_hold":         lambda ship: ship.update({"max_cargo":      ship["max_cargo"]+ 100}),
    "grain_silo":        lambda ship: ship.update({"max_cargo":      ship["max_cargo"]+ 200}),
    "broker_license":    lambda ship: ship.update({"broker_license": True}),
    "passenger_quoters": lambda ship: ship.update({"passenger_slot": True}),
    "long_range_radar":  lambda ship: ship.update({"radar":          True}),
    "booster":           lambda ship: ship.update({"booster":        True}),
}

# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def month_name(idx):
    return P.MONTH_NAMES[idx % P.MONTHS_PER_YEAR]

def date_str(state):
    return f"{month_name(state['month_index'])} {state['year']}"

def advance_time(state, months=1):
    for _ in range(months):
        state["turn"]        += 1
        state["month_index"] += 1
        if state["month_index"] >= P.MONTHS_PER_YEAR:
            state["month_index"] = 0
            state["year"]       += 1
    _apply_inflation(state)
    _check_festival_drop(state)

def current_harvest_good(month_index):
    for good, entry in P.GOOD_SEASONS.items():
        if entry and entry[0] == month_index:
            return good
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# PRICE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _spread(good):
    entry = P.GOOD_DATA.get(good)
    return P.SPREAD_AMOUNT[entry[0]] if entry else 5

def _price_min(good):
    entry = P.GOOD_DATA.get(good)
    return entry[1] if entry else 1

def _price_max(good):
    entry = P.GOOD_DATA.get(good)
    return entry[3] if entry else 9999

def _clamp_base(good, price):
    return max(_price_min(good), min(_price_max(good), price))

def _season_offset(good, current_month):
    entry = P.GOOD_SEASONS.get(good)
    if entry is None: return 0
    harvest_month, pattern_key = entry
    pattern = P.SEASON_PATTERNS[pattern_key]
    return pattern[(current_month - harvest_month) % P.MONTHS_PER_YEAR]

def _festival_boost_this_month(planet_name, current_month):
    if planet_name not in P.PLANET_FESTIVALS: return None, 0
    good, fest_month, _name, boost_type = P.PLANET_FESTIVALS[planet_name]
    if current_month == fest_month:
        return good, P.FESTIVAL_BOOST[boost_type]
    return None, 0

def effective_mean(state, planet_name, good):
    base     = state["planets"][planet_name]["base_prices"].get(good, 1)
    season   = _season_offset(good, state["month_index"])
    fg, fb   = _festival_boost_this_month(planet_name, state["month_index"])
    festival = fb if good == fg else 0
    sp       = _spread(good)
    raw      = base + season + festival
    return max(_price_min(good) - sp, min(_price_max(good) + sp, raw))

def buy_price(state, planet_name, good):
    return max(1, effective_mean(state, planet_name, good) + _spread(good))

def sell_price(state, planet_name, good):
    return max(1, effective_mean(state, planet_name, good) - _spread(good))

# ═══════════════════════════════════════════════════════════════════════════════
# INFLATION & FESTIVAL DROP
# ═══════════════════════════════════════════════════════════════════════════════

def _apply_inflation(state):
    for planet_name, planet in state["planets"].items():
        prod = planet["production"]
        dem  = planet["demand"]
        for good in list(planet["base_prices"].keys()):
            if good in (prod, dem): continue
            if random.random() < 0.5:
                delta = random.randint(1, P.INFLATION_UP_MAX)
            else:
                delta = -random.randint(1, P.INFLATION_DOWN_MAX)
            planet["base_prices"][good] = _clamp_base(
                good, planet["base_prices"][good] + delta)

def _check_festival_drop(state):
    m = state["month_index"]
    for planet_name, (good, fest_month, _name, boost_type) in P.PLANET_FESTIVALS.items():
        drop_month = (fest_month + 1) % P.MONTHS_PER_YEAR
        if m == drop_month:
            drop_key = f"{planet_name}_{good}_dropped_{state['year']}"
            if drop_key not in state["festival_drops_applied"]:
                state["festival_drops_applied"].add(drop_key)
                planet = state["planets"][planet_name]
                if good in planet["base_prices"]:
                    boost = P.FESTIVAL_BOOST[boost_type]
                    planet["base_prices"][good] = _clamp_base(
                        good, planet["base_prices"][good] - boost)

# ═══════════════════════════════════════════════════════════════════════════════
# REMOTE SEED (requests hook for travel event RNG)
# ═══════════════════════════════════════════════════════════════════════════════

def _fetch_remote_seed():
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
# GENERAL HELPERS
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

def _col(text, width):    return str(text).ljust(width)
def _cargo_used(ship):    return sum(ship["cargo"].values())
def _cargo_free(ship):    return ship["max_cargo"] - _cargo_used(ship)

def _travel_fuel_cost(origin, destination):
    i = P.PLANET_NAMES.index(origin)
    j = P.PLANET_NAMES.index(destination)
    raw = abs(i - j) * P.TRAVEL_COST_PER_HOP + random.randint(
        -P.TRAVEL_JITTER, P.TRAVEL_JITTER)
    return max(P.TRAVEL_MIN, min(P.TRAVEL_MAX, raw))

# ═══════════════════════════════════════════════════════════════════════════════
# NEWS FEED
# ═══════════════════════════════════════════════════════════════════════════════

def print_news(ship, state):
    loc   = ship["location"]
    m     = state["month_index"]
    lines = []

    if ship.get("passenger_slot"):
        pw = state.get("passenger_waiting")
        if pw:
            lines.append(L.NEWS_TRAVELER.format(
                shortname=pw["shortname"], destination=pw["destination"]))

    if loc in P.PLANET_FESTIVALS:
        good, fest_month, fest_name, _ = P.PLANET_FESTIVALS[loc]
        if m == fest_month:
            lines.append(L.NEWS_FESTIVAL.format(
                festival_name=fest_name, planet=loc, month_name=month_name(m)))

    harvest_good = current_harvest_good(m)
    if harvest_good:
        lines.append(L.NEWS_HARVEST.format(
            harvest_good=harvest_good, month_name=month_name(m)))

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
        extras.append(
            f"Passenger: {p['shortname']} → {p['destination']}" if p
            else "Passenger slot (empty)")
    if extras: print(f"  Upgrades : {', '.join(extras)}")
    if ship["location"] == P.FARM_PLANET and ship.get("farm_bought"):
        print(f"  🌿 You own a cinnamon farm on {P.FARM_PLANET}.")
    print("═"*52)

def show_market(ship, state):
    planet_name = ship["location"]
    planet      = state["planets"][planet_name]
    m           = state["month_index"]

    fest_good, fest_boost = _festival_boost_this_month(planet_name, m)
    if fest_good:
        fest_name = P.PLANET_FESTIVALS[planet_name][2]
        print(f"\n  🎊 {fest_name.upper()} this month! {fest_good} +{fest_boost}cr")

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
        print(f"  [{i}] {good:<18} {buy_price(state, planet_name, good):>6} cr/unit")
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
        print(f"  [{i}] {good:<18} {qty:>4} units @ {sell_price(state, planet_name, good):>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose good: ", 0, len(cargo_items))
    if choice == 0: return
    good, available = cargo_items[choice-1]
    sp     = sell_price(state, planet_name, good)
    amount = _get_int(f"How many {good}? (max {available}): ", 1, available)
    gross  = amount * sp
    tax    = max(P.SALE_TAX_MIN, math.ceil(gross * P.SALE_TAX_RATE))
    net    = gross - tax
    ship["credits"] += net
    ship["cargo"][good] -= amount
    if ship["cargo"][good] <= 0: del ship["cargo"][good]
    print(f"✓ Sold {amount}× {good} for {gross:,} cr.  Tax: {tax} cr.  Net: {net:,} cr.")

# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL
# ═══════════════════════════════════════════════════════════════════════════════

def do_travel(ship, state):
    if ship["fuel"] < P.MIN_FUEL_TO_DEPART:
        print(f"Need ≥{P.MIN_FUEL_TO_DEPART} fuel to depart. Refuel in Engineering Bay.")
        return
    other = [p for p in P.PLANET_NAMES if p != ship["location"]]
    print("\n── TRAVEL ───────────────────────────────────────────")
    for i, planet in enumerate(other, 1):
        print(f"  [{i}] {planet:<16}  ~{_travel_fuel_cost(ship['location'], planet)} fuel")
    print("  [0] Cancel")
    choice = _get_int("Destination: ", 0, len(other))
    if choice == 0: return
    destination = other[choice-1]
    fuel_cost   = _travel_fuel_cost(ship["location"], destination)
    if ship["fuel"] - fuel_cost < P.MIN_FUEL_TO_DEPART:
        print(f"Not enough fuel. Need {fuel_cost}+{P.MIN_FUEL_TO_DEPART} reserve.")
        return

    random.seed(_fetch_remote_seed())
    ship["fuel"]          -= fuel_cost
    ship["location"]       = destination
    state["news_printed"]  = False
    advance_time(state)
    print(f"\n🚀 Jumped to {destination}. Fuel used: {fuel_cost}. Date: {date_str(state)}")

    planet = state["planets"][destination]
    for good in planet["base_prices"]:
        if good not in (planet["production"], planet["demand"]):
            planet["base_prices"][good] = _clamp_base(
                good, planet["base_prices"][good] + random.randint(-5, 5))
    random.seed()

    pirate_chance = (P.PIRATE_RADAR_CHANCE if ship.get("radar")
                     else P.PIRATE_BASE_CHANCE)
    if random.random() < pirate_chance:
        alive = _pirate_encounter(ship, state)
        if not alive: return "GAME_OVER"
    else:
        roll = random.random(); cum = 0.0
        probs = P.TRAVEL_EVENT_PROBS
        for key, prob in probs.items():
            cum += prob
            if roll < cum:
                _travel_event(key, ship, state, destination); break

    _check_passenger_delivery(ship, state)
    _maybe_spawn_passenger(ship, state)

def _travel_event(key, ship, state, dest):
    if key == "festival":
        planet = state["planets"][dest]
        for good in planet["base_prices"]:
            planet["base_prices"][good] = int(planet["base_prices"][good] * 1.1)
        print(f"🎉 SPICE FESTIVAL on {dest}! All prices +10%.")
    elif key == "fuel_leak":
        lost = random.randint(P.FUEL_LEAK_MIN, P.FUEL_LEAK_MAX)
        ship["fuel"] = max(0, ship["fuel"] - lost)
        print(f"🔧 FUEL LEAK mid-jump. Lost {lost} fuel.")
    elif key == "mystery_cargo":
        free = _cargo_free(ship)
        amt  = P.MYSTERY_CARGO_AMOUNT
        if free >= amt:
            ship["cargo"]["Mystery Crate"] = ship["cargo"].get("Mystery Crate", 0) + amt
            print(f"📦 Drifting cargo pod attached. +{amt} Mystery Crate.")
        else:
            print("📦 Drifting cargo pod — no room. It drifts on.")

# ═══════════════════════════════════════════════════════════════════════════════
# PIRATES
# ═══════════════════════════════════════════════════════════════════════════════

def _pirate_encounter(ship, state):
    state["piratangst"] += 1
    angst      = state["piratangst"]
    bribe_cost = state["piratbribe"]
    flee_mult  = (P.PIRATE_FLEE_MULT_BOOST if ship.get("booster")
                  else P.PIRATE_FLEE_MULT)
    flee_cost  = max(0, min(flee_mult * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))

    print("\n" + "⚠"*50)
    print(f"  PIRATE INTERCEPT!  (Angst level: {angst})")
    print("⚠"*50)
    print(f"\n  [1] Fight       (your weapons: {ship['weapons']})")
    print(f"  [2] Flee        (costs {flee_cost} fuel)")
    print(f"  [3] Bribe       ({bribe_cost} cr — rises each use)")
    print(f"  [4] Drop Cargo  (lose half of each good, min 1)")
    print(f"  [5] Bluff       (auto-pass if total cargo ≤10)")
    print(f"  [6] Surrender   (WARNING: ends your game)")
    return _pirate_resolve(ship, state, _get_int("Choose: ", 1, 6), exclude=None)

def _pirate_resolve(ship, state, choice, exclude):
    angst      = state["piratangst"]
    flee_mult  = (P.PIRATE_FLEE_MULT_BOOST if ship.get("booster")
                  else P.PIRATE_FLEE_MULT)
    flee_cost  = max(0, min(flee_mult * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))

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
            bounty = P.PIRATE_BOUNTY_PER_ANGST * angst
            ship["credits"] += bounty
            state["piratangst"] += 3
            print(f"  Pirate scum obliterated! Bounty collected: {bounty:,} cr.")
        return True

    elif choice == 2:
        if ship["fuel"] - flee_cost < P.MIN_FUEL_TO_DEPART:
            print(f"  Not enough fuel to flee (need {flee_cost}). Choose again.")
            return _pirate_retry(ship, state, exclude=2)
        ship["fuel"] -= flee_cost
        print(f"  You gun the engines and escape! Fuel burned: {flee_cost}.")
        return True

    elif choice == 3:
        if ship["credits"] < state["piratbribe"]:
            loss = ship["credits"]; ship["credits"] = 0
            print(f"  Can't afford bribe. They strip your last {loss} cr.")
        else:
            ship["credits"] -= state["piratbribe"]
            state["piratangst"] = max(0, state["piratangst"] - 3)
            print(f"  You pay {state['piratbribe']} cr. They wave you through.")
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
            print("\n  You're stripped of everything.")
            print("  Six months later you're mining blockchain hashes in a Zeta-9 server farm.")
            print("  The smell of saffron is the last thing you remember of freedom.")
            print("\n  ─── GAME OVER ───")
            return False
        else:
            print("  You reconsider.")
            return _pirate_encounter(ship, state)
    return True

def _pirate_retry(ship, state, exclude):
    angst     = state["piratangst"]
    flee_mult = P.PIRATE_FLEE_MULT_BOOST if ship.get("booster") else P.PIRATE_FLEE_MULT
    flee_cost = max(0, min(flee_mult * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))
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
# PASSENGERS
# ═══════════════════════════════════════════════════════════════════════════════

def _maybe_spawn_passenger(ship, state):
    if not ship.get("passenger_slot"): return
    if state.get("passenger_waiting"):  return
    if random.random() < P.PASSENGER_SPAWN_CHANCE:
        p = random.choice(L.PASSENGER_ROSTER).copy()
        p["destination"] = random.choice(
            [pl for pl in P.PLANET_NAMES if pl != ship["location"]])
        state["passenger_waiting"] = p

def _check_passenger_delivery(ship, state):
    p = ship.get("passenger")
    if p and p["destination"] == ship["location"]:
        print("\n" + "─"*50)
        print(p["exit_text"])
        ship["credits"] += P.PASSENGER_DELIVERY_PAY
        print(f"  +{P.PASSENGER_DELIVERY_PAY} credits received.")
        print("─"*50)
        ship["passenger"] = None

# ═══════════════════════════════════════════════════════════════════════════════
# PRICE CHECK
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
    for pn in P.PLANET_NAMES:
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
        print(random.choice(L.FARM_FLUFF))
        print("="*50)
        print("  [1] Stay a little longer   [2] Return to the stars")
        if input("Choose: ").strip() == "2":
            print("You leave the farm, ready to face the galaxy again."); break

# ═══════════════════════════════════════════════════════════════════════════════
# CANTINA
# ═══════════════════════════════════════════════════════════════════════════════

def visit_cantina(ship, state):
    cantina = L.cantinas[ship["location"]]
    while True:
        pw          = state.get("passenger_waiting")
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
            dc    = max(1, int(sell_price(state, ship["location"], drink["ingredient"]) * 0.5))
            if ship["credits"] < dc:
                print(f"  Can't afford a {drink['name']} ({dc} cr).")
            else:
                ship["credits"] -= dc
                print(f"\n  You buy a {drink['name']} for {dc} cr.")
                print(f"  {random.choice(drink['fluff'])}")

        elif choice == "2":
            pool_name, advice = L.random_advice()
            print(f"\n  [Bartender — {pool_name.upper()}]: {advice}")

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
                    print(f"  (Replacing {ship['passenger']['shortname']} — they stay here.)")
                if input("  Take them aboard? [y/n]: ").strip().lower() == "y":
                    ship["passenger"] = pw
                    state["passenger_waiting"] = None
                    print(f"  {pw['shortname']} boards your ship.")

        elif choice == "4":
            print("\n" + "─"*50)
            print("  You spend a month in the cantina. The days blur together.")
            news = L.random_galaxy_news(state["galaxy_story_index"])
            if news:
                print(f"\n  [GALAXY NEWS]: {news}")
                state["galaxy_story_index"] += 1
            else:
                print("  The galaxy turns, quietly.")
            print("─"*50)
            input("  [Enter to continue...]")
            advance_time(state)
            _maybe_spawn_passenger(ship, state)
            print(f"  Date is now: {date_str(state)}")

        elif choice == "9":
            break
        else:
            print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# INFOBROKER
# ═══════════════════════════════════════════════════════════════════════════════

def visit_infobroker(ship, state):
    while True:
        print("\n── INFOBROKER ───────────────────────────────────────")
        print("  [1] Goods Directory")
        print("  [2] Harvest Seasons")
        print("  [3] Festival Calendar")
        print("  [9] Back to Promenade")
        choice = input("Choose: ").strip()
        if choice == "1":   L.infobroker_goods_table()
        elif choice == "2": L.infobroker_harvest_table()
        elif choice == "3": L.infobroker_festival_table()
        elif choice == "9": break
        else: print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# CONCERT HALL
# ═══════════════════════════════════════════════════════════════════════════════

def visit_concert(ship, state):
    ticket = P.CONCERT_TICKET
    if ship["credits"] < ticket:
        print(f"\n  Ticket costs {ticket} cr. You're too broke for culture right now.")
        return
    ship["credits"] -= ticket
    print(f"\n  You pay {ticket} cr and take your seat...")

    try:
        with open(P.SONGS_FILE, encoding="utf-8") as f:
            songs_data = json.load(f)
        songs = songs_data.get("songs", [])
        if not songs:
            raise ValueError("empty song list")
        song = random.choice(songs)
        print("\n" + "★"*52)
        print(f"  NOW PLAYING: {song.get('fullname', song.get('shortname', 'Unknown'))}")
        print("★"*52 + "\n")
        print(song.get("text", "(no lyrics)"))
        if song.get("art"):
            print()
            print(song["art"])
        print("\n" + "★"*52)

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        ship["credits"] += ticket
        print("\n" + L.CONCERT_NO_SHOW)

# ═══════════════════════════════════════════════════════════════════════════════
# PROMENADE
# ═══════════════════════════════════════════════════════════════════════════════

def visit_promenade(ship, state):
    loc = ship["location"]
    while True:
        print(f"\n── PROMENADE  —  {loc} ──────────────────────────────")
        print("  [1] Cantina")
        print("  [2] Infobroker")
        print(f"  [3] Concert Hall  [{P.CONCERT_TICKET} cr]")
        if loc == P.FARM_PLANET:
            label = "Visit Your Cinnamon Farm" if ship.get("farm_bought") else f"Buy Cinnamon Farm  [{P.FARM_COST:,} cr]"
            print(f"  [f] {label}")
        print("  [0] Back to Spaceport")
        choice = input("Choose: ").strip().lower()

        if choice == "1":
            visit_cantina(ship, state)
        elif choice == "2":
            visit_infobroker(ship, state)
        elif choice == "3":
            visit_concert(ship, state)
        elif choice == "f" and loc == P.FARM_PLANET:
            if not ship.get("farm_bought"):
                print(f"\n  Buy a cinnamon farm for {P.FARM_COST:,} cr? (You have {ship['credits']:,})")
                if ship["credits"] >= P.FARM_COST:
                    if input("  Confirm [y/n]: ").strip().lower() == "y":
                        ship["credits"] -= P.FARM_COST
                        ship["farm_bought"] = True
                        print("  🌿 You now own a cinnamon farm on Terra.")
                else:
                    print(f"  Need {P.FARM_COST - ship['credits']:,} more credits.")
            else:
                visit_farm(ship, state)
        elif choice == "0":
            break
        else:
            print("  Invalid choice.")

# ═══════════════════════════════════════════════════════════════════════════════
# ENGINEERING BAY
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
        else: print("  Invalid choice.")

def _fuel_up(ship):
    space = ship["max_fuel"] - ship["fuel"]
    if space <= 0: print("  Tank is full."); return
    print(f"\n  Fuel: {P.FUEL_PRICE} cr/unit. Space available: {space}")
    seen = set(); disp = []
    for n in [100, 200, 500, 1000, space]:
        amt = min(n, space)
        if amt > 0 and amt not in seen:
            seen.add(amt); disp.append(amt)
    for i, amt in enumerate(disp, 1):
        label = "FULL" if amt == space else str(amt)
        print(f"  [{i}] +{label} fuel  →  {amt * P.FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(disp))
    if c == 0: return
    amt  = disp[c-1]
    cost = amt * P.FUEL_PRICE
    if ship["credits"] < cost:
        print(f"  Not enough credits. Need {cost:,}, have {ship['credits']:,}."); return
    ship["credits"] -= cost
    ship["fuel"]     = min(ship["max_fuel"], ship["fuel"] + amt)
    print(f"✓ Fuelled +{amt}. Tank: {ship['fuel']}/{ship['max_fuel']}")

def _drain_fuel(ship):
    drainable = ship["fuel"] - P.MIN_FUEL_TO_DEPART
    if drainable <= 0:
        print(f"  Must keep ≥{P.MIN_FUEL_TO_DEPART} fuel. Nothing to drain."); return
    print(f"\n  Drainable: {drainable} units → up to {drainable * P.FUEL_PRICE:,} cr")
    opts = sorted(set(
        min(n, drainable) for n in [100, 200, 500, 1000, int(ship["fuel"] * 0.9)]
        if 0 < min(n, drainable) <= drainable))
    for i, amt in enumerate(opts, 1):
        label = "90%" if amt == int(ship["fuel"] * 0.9) else str(amt)
        print(f"  [{i}] Drain {label}  →  +{amt * P.FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(opts))
    if c == 0: return
    amt = opts[c-1]
    ship["fuel"]    -= amt
    ship["credits"] += amt * P.FUEL_PRICE
    print(f"✓ Drained {amt} fuel. Gained {amt * P.FUEL_PRICE:,} cr. Tank: {ship['fuel']}/{ship['max_fuel']}")

def _upgrades_menu(ship, state):
    loc = ship["location"]
    available = [
        (uid, P.UPGRADES_DATA[uid]) for uid in P.UPGRADES_DATA
        if (P.UPGRADES_DATA[uid]["planet"] is None or P.UPGRADES_DATA[uid]["planet"] == loc)
        and uid not in ship["upgrades_bought"]
    ]
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
    UPGRADE_EFFECTS[uid](ship)
    ship["upgrades_bought"].append(uid)
    print(f"✓ {u['name']} installed.")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════════════

def save_game(ship, state):
    data = {
        "ship": dict(ship),
        "planets_prices": {
            n: {"base_prices": p["base_prices"]}
            for n, p in state["planets"].items()},
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
        with open(P.SAVE_FILE, "w") as f: json.dump(data, f, indent=2)
        print(f"💾 Saved to {P.SAVE_FILE}")
    except OSError as e:
        print(f"⚠️  Save failed: {e}")

def load_game(planets, state):
    if not os.path.exists(P.SAVE_FILE): return None
    try:
        with open(P.SAVE_FILE) as f: data = json.load(f)
        for name, pdata in data["planets_prices"].items():
            if name in planets:
                planets[name]["base_prices"].update(pdata["base_prices"])
        state["turn"]               = data.get("turn", 1)
        state["month_index"]        = data.get("month_index", 0)
        state["year"]               = data.get("year", P.START_YEAR)
        state["piratangst"]         = data.get("piratangst", P.PIRATE_START_ANGST)
        state["piratbribe"]         = data.get("piratbribe", P.PIRATE_START_BRIBE)
        state["galaxy_story_index"] = data.get("galaxy_story_index", 0)
        state["passenger_waiting"]  = data.get("passenger_waiting")
        state["festival_drops_applied"] = set(data.get("festival_drops_applied", []))
        print(f"📂 Loaded from {P.SAVE_FILE}")
        return data["ship"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Load failed: {e}"); return None

# ═══════════════════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════════════════

def init_planets():
    planets = {}
    for pname, pdata in P.planets_template.items():
        new_prices = {}
        for good, price in pdata["base_prices"].items():
            if good in (pdata["production"], pdata["demand"]):
                new_prices[good] = price
            else:
                new_prices[good] = _clamp_base(good, price + random.randint(-10, 10))
        planets[pname] = {**pdata, "base_prices": new_prices}
    return planets

def new_ship():
    import copy
    return copy.deepcopy(P.SHIP_START)

def new_state(planets):
    return {
        "planets":                planets,
        "turn":                   1,
        "month_index":            0,
        "year":                   P.START_YEAR,
        "piratangst":             P.PIRATE_START_ANGST,
        "piratbribe":             P.PIRATE_START_BRIBE,
        "galaxy_story_index":     0,
        "passenger_waiting":      None,
        "festival_drops_applied": set(),
        "news_printed":           False,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    planets = init_planets()
    state   = new_state(planets)

    print("═"*55)
    print("  SPICE SPACE TRADER  v10")
    print("  Trade spices. Dodge pirates. Maybe buy a farm.")
    print("═"*55)

    if os.path.exists(P.SAVE_FILE):
        if input("\nSave file found. Load it? [y/n]: ").strip().lower() == "y":
            loaded = load_game(planets, state)
            ship   = loaded if loaded else new_ship()
        else:
            ship = new_ship()
    else:
        ship = new_ship()

    while True:
        if not state.get("news_printed"):
            print_news(ship, state)

        show_status(ship, state)
        show_market(ship, state)

        raw = input("\nChoose action: ").strip()

        if raw.startswith("!credits "):
            try: ship["credits"] += int(raw.split()[1])
            except (ValueError, IndexError): pass
            continue

        try:
            action = int(raw)
        except ValueError:
            print("  Enter a number."); continue

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
        else: print("  Invalid action.")

if __name__ == "__main__":
    main()
