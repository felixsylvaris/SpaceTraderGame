"""
=============================================================
  SPICE SPACE TRADER — game.py  v13
=============================================================
  Run: python game.py
  Files: game.py / parameters.py / library.py / songs.py
=============================================================
  Changelog
=============================================================
v13
  + Galaxy Random Events system
    Two pools: blank (80%, flavour only) and impact (20%, game effect)
    Fires on planet arrival and cantina rest (both = 1 month passing)
    Impact events adjust stockpiles and prices with safety clamps
    Split ratio controlled by parameters.RND_EVENT_SPLIT
    Galaxy story system silenced (reserved for future)

v12
  + Navigation rekeyed: 0 = universal back/cancel, q = quit game
    All submenus (cantina, infobroker, engineering bay, promenade)
    now use 0 to go back instead of 9
  + Randomised game start (new game only, not on load)
    Prices and stockpiles randomised within bounds, averaged with
    parameter defaults, then clamped for legality
  + Fleet Supply Depot on Terra Promenade [s]
    Sell-only, fixed prices, no stockpile, goods vanish on sale
    Price table defined in parameters.FLEET_DEPOT_PRICES
  + songs.py replaces songs.json — SONGS list imported directly
    Removed all file I/O, json loading, and SONGS_FILE references

v11
  + Stockpiles: every planet/good has a stockpile
  + Production/Consumption/Void Pepper special
  + Local Market on every Promenade
  + Save/load updated

v10  4-file split; UPGRADE_EFFECTS in game.py; UPGRADES_DATA in parameters
v9   Promenade; spread; GOOD_DATA bounds; news feed; songs.json
v8.1 Clove 40 on Void Colony; Allspice festival high; Void Torpedo +2
v8   Calendar, goods, tax, inflation, harvest, festivals, Engineering Bay,
     upgrades, Broker License, passengers, pirates v2, cheat, save/load
v7   requests, events, fuel/cargo split, fixes, save JSON
v6   Original
=============================================================
"""

import random, json, math, os, copy
import parameters as P
import library    as L
from songs import SONGS

try:
    import requests as _requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ─── UPGRADE EFFECTS ──────────────────────────────────────────────────────────

UPGRADE_EFFECTS = {
    "kinetic_launcher":  lambda s: s.update({"weapons":        s["weapons"]  + 1}),
    "mining_laser":      lambda s: s.update({"weapons":        s["weapons"]  + 1}),
    "void_torpedo":      lambda s: s.update({"weapons":        s["weapons"]  + 2}),
    "stern_tank":        lambda s: s.update({"max_fuel":       s["max_fuel"] + 200}),
    "portside_tank":     lambda s: s.update({"max_fuel":       s["max_fuel"] + 300}),
    "cylindrical_tank":  lambda s: s.update({"max_fuel":       s["max_fuel"] + 500}),
    "small_hold":        lambda s: s.update({"max_cargo":      s["max_cargo"]+ 100}),
    "side_hold":         lambda s: s.update({"max_cargo":      s["max_cargo"]+ 100}),
    "grain_silo":        lambda s: s.update({"max_cargo":      s["max_cargo"]+ 200}),
    "broker_license":    lambda s: s.update({"broker_license": True}),
    "passenger_quoters": lambda s: s.update({"passenger_slot": True}),
    "long_range_radar":  lambda s: s.update({"radar":          True}),
    "booster":           lambda s: s.update({"booster":        True}),
}

# ─── CALENDAR ─────────────────────────────────────────────────────────────────

def month_name(idx):  return P.MONTH_NAMES[idx % P.MONTHS_PER_YEAR]
def date_str(state):  return f"{month_name(state['month_index'])} {state['year']}"

def advance_time(state, months=1):
    for _ in range(months):
        state["turn"]        += 1
        state["month_index"] += 1
        if state["month_index"] >= P.MONTHS_PER_YEAR:
            state["month_index"] = 0
            state["year"]       += 1
        _run_consumption(state)
        _run_production(state)
        _run_industrial_production(state)
        _apply_stockpile_pressure(state)
        _apply_inflation(state)
        _check_festival_drop(state)

def current_harvest_good(month_index):
    for good, entry in P.GOOD_SEASONS.items():
        if entry and entry[0] == month_index:
            return good
    return None

# ─── PRICE HELPERS ────────────────────────────────────────────────────────────

def _spread(good):
    e = P.GOOD_DATA.get(good); return P.SPREAD_AMOUNT[e[0]] if e else 5

def _price_min(good):
    e = P.GOOD_DATA.get(good); return e[1] if e else 1

def _price_max(good):
    e = P.GOOD_DATA.get(good); return e[3] if e else 9999

def _good_cat(good):
    e = P.GOOD_DATA.get(good); return e[0] if e else "low"

def _clamp_base(good, price):
    return max(_price_min(good), min(_price_max(good), price))

def _season_offset(good, month):
    e = P.GOOD_SEASONS.get(good)
    if e is None: return 0
    hm, pk = e
    return P.SEASON_PATTERNS[pk][(month - hm) % P.MONTHS_PER_YEAR]

def _festival_boost(planet_name, month):
    if planet_name not in P.PLANET_FESTIVALS: return None, 0
    good, fm, _n, bt = P.PLANET_FESTIVALS[planet_name]
    return (good, P.FESTIVAL_BOOST[bt]) if month == fm else (None, 0)

def effective_mean(state, planet, good):
    base    = state["planets"][planet]["base_prices"].get(good, 1)
    season  = _season_offset(good, state["month_index"])
    fg, fb  = _festival_boost(planet, state["month_index"])
    fest    = fb if good == fg else 0
    sp      = _spread(good)
    raw     = base + season + fest
    return max(_price_min(good) - sp, min(_price_max(good) + sp, raw))

def buy_price(state, planet, good):
    return max(1, effective_mean(state, planet, good) + _spread(good))

def sell_price(state, planet, good):
    return max(1, effective_mean(state, planet, good) - _spread(good))

# ─── STOCKPILE HELPERS ────────────────────────────────────────────────────────

def _stk_max(good):
    return P.STOCKPILE_MAX.get(_good_cat(good), 100)

def _stk_start(planet, good):
    ov = P.STOCKPILE_OVERRIDES.get((planet, good))
    return ov if ov is not None else P.STOCKPILE_START.get(_good_cat(good), 50)

def get_stk(state, planet, good):
    return state["stockpiles"].get(planet, {}).get(good, 0)

def set_stk(state, planet, good, amount):
    if planet not in state["stockpiles"]:
        state["stockpiles"][planet] = {}
    state["stockpiles"][planet][good] = max(0, min(_stk_max(good), int(amount)))

def _stk_ratio(state, planet, good):
    mx = _stk_max(good)
    return get_stk(state, planet, good) / mx if mx else 0.0

# ─── STOCKPILE PRESSURE ───────────────────────────────────────────────────────

def _apply_stockpile_pressure(state):
    for pname, planet in state["planets"].items():
        for good in planet["base_prices"]:
            ratio    = _stk_ratio(state, pname, good)
            pressure = P.STOCKPILE_PRESSURE[_good_cat(good)]
            cur      = planet["base_prices"][good]
            if ratio < P.STOCKPILE_LOW_THRESHOLD:
                planet["base_prices"][good] = _clamp_base(good, cur + pressure)
            elif ratio > P.STOCKPILE_HIGH_THRESHOLD:
                planet["base_prices"][good] = _clamp_base(good, cur - pressure)

# ─── PRODUCTION ───────────────────────────────────────────────────────────────

def _run_production(state):
    """Seasonal harvest production — spices only."""
    m = state["month_index"]
    for good, entry in P.GOOD_SEASONS.items():
        if entry is None: continue                      # no season = skip (covers industrials too)
        hm, _ = entry
        if m != hm: continue
        cat  = _good_cat(good)
        base = P.PRODUCTION_BASE[cat]
        for pname, planet in state["planets"].items():
            if good not in planet["base_prices"]: continue
            cur = get_stk(state, pname, good)
            amt = base
            if planet["production"] == good:
                amt = int(amt * P.PRODUCTION_HOME_MULT)
            if cur == 0:
                amt = int(amt * P.PRODUCTION_ZERO_MULT)
            set_stk(state, pname, good, cur + amt)

    # Void Pepper special
    if m == P.VOID_PEPPER_PRODUCTION_MONTH:
        cur = get_stk(state, "Void Colony", "Void Pepper")
        amt = P.VOID_PEPPER_PRODUCTION_AMOUNT
        if cur == 0:
            amt = int(amt * P.PRODUCTION_ZERO_MULT)
        set_stk(state, "Void Colony", "Void Pepper", cur + amt)

def _run_industrial_production(state):
    """Monthly industrial production — fires every turn."""
    # Build bonus multipliers: target_planet → target_good → multiplier (multiplicative stacking)
    bonuses = {}
    for trig_planet, trig_good, threshold, tgt_planet, tgt_good, mult in P.INDUSTRIAL_BONUS_RULES:
        if _stk_ratio(state, trig_planet, trig_good) >= threshold:
            bonuses.setdefault(tgt_planet, {}).setdefault(tgt_good, 1.0)
            bonuses[tgt_planet][tgt_good] *= mult

    for good, base_amt in P.INDUSTRIAL_PRODUCTION.items():
        for pname, planet in state["planets"].items():
            if good not in planet["ind_production"]: continue
            if good not in planet["base_prices"]:    continue
            amt  = base_amt
            mult = bonuses.get(pname, {}).get(good, 1.0)
            amt  = int(amt * mult)
            cur  = get_stk(state, pname, good)
            set_stk(state, pname, good, cur + amt)

# ─── CONSUMPTION ──────────────────────────────────────────────────────────────

def _run_consumption(state):
    for pname, planet in state["planets"].items():
        for good in list(planet["base_prices"].keys()):
            if good == "Void Pepper": continue

            # Per-good industrial consumption rate overrides category default
            if good in P.INDUSTRIAL_CONSUMPTION:
                base_amt = P.INDUSTRIAL_CONSUMPTION[good]
            else:
                base_amt = P.CONSUMPTION_BASE[_good_cat(good)]

            ratio = _stk_ratio(state, pname, good)

            # Scarcity halving (floor 1) and abundance doubling
            if ratio < P.STOCKPILE_LOW_THRESHOLD:
                base_amt = max(1, base_amt // 2)
            elif ratio >= P.STOCKPILE_HIGH_THRESHOLD:
                base_amt = base_amt * 2

            # Demand planet doubles consumption for spice goods only
            if good not in P.INDUSTRIAL_CONSUMPTION and planet["demand"] == good:
                base_amt = int(base_amt * P.CONSUMPTION_DEMAND_MULT)

            set_stk(state, pname, good, max(0, get_stk(state, pname, good) - base_amt))

    for pname, consume in P.VOID_PEPPER_CONSUMPTION.items():
        set_stk(state, pname, "Void Pepper",
                max(0, get_stk(state, pname, "Void Pepper") - consume))

# ─── INFLATION & FESTIVAL DROP ────────────────────────────────────────────────

def _apply_inflation(state):
    for planet in state["planets"].values():
        for good in list(planet["base_prices"].keys()):
            if random.random() < 0.5:
                delta = random.randint(1, P.INFLATION_UP_MAX)
            else:
                delta = -random.randint(1, P.INFLATION_DOWN_MAX)
            planet["base_prices"][good] = _clamp_base(
                good, planet["base_prices"][good] + delta)

def _check_festival_drop(state):
    m = state["month_index"]
    for pname, (good, fm, _n, bt) in P.PLANET_FESTIVALS.items():
        dm = (fm + 1) % P.MONTHS_PER_YEAR
        if m == dm:
            key = f"{pname}_{good}_dropped_{state['year']}"
            if key not in state["festival_drops_applied"]:
                state["festival_drops_applied"].add(key)
                planet = state["planets"][pname]
                if good in planet["base_prices"]:
                    planet["base_prices"][good] = _clamp_base(
                        good, planet["base_prices"][good] - P.FESTIVAL_BOOST[bt])

# ─── RANDOM EVENTS ────────────────────────────────────────────────────────────

def _fire_random_event(state):
    """Roll and apply one random event. Called on travel arrival and cantina rest."""
    if random.random() < P.RND_EVENT_SPLIT:
        # Impact event
        evt = random.choice(L.event_rnd_impact)
        print(f"\n  🌐 BREAKING: {evt['text']}")
        for planet, good, stk_delta, price_delta in evt["effects"]:
            # Guard: planet and good must exist in state
            if planet not in state["planets"]: continue
            if good not in state["planets"][planet]["base_prices"]: continue
            # Apply stockpile delta — set_stk already clamps to [0, max]
            if stk_delta != 0:
                cur_stk = get_stk(state, planet, good)
                set_stk(state, planet, good, cur_stk + stk_delta)
            # Apply price delta — _clamp_base keeps within [min_price, max_price]
            if price_delta != 0:
                cur_price = state["planets"][planet]["base_prices"][good]
                state["planets"][planet]["base_prices"][good] = _clamp_base(
                    good, cur_price + price_delta)
    else:
        # Blank event — flavour only
        evt_text = random.choice(L.event_rnd_blank)
        print(f"\n  📰 {evt_text}")

# ─── LOCAL MARKET ─────────────────────────────────────────────────────────────

def _roll_local_market(state, planet):
    pool  = [g for g in P.GOOD_DATA if g not in P.LOCAL_MARKET_EXCLUDE]
    slots = []
    for _ in range(P.LOCAL_MARKET_SLOTS):
        good  = random.choice(pool)
        cat   = _good_cat(good)
        base  = sell_price(state, planet, good)
        sp    = P.SPREAD_AMOUNT[cat]
        var   = P.LOCAL_MARKET_VARIANCE[cat]
        price = max(1, base + sp + random.randint(-var, var))
        slots.append({"good": good, "price": price,
                      "quantity": P.LOCAL_MARKET_QTY[cat], "sold": False})
    return slots

def _market_news_line(slots):
    return ", ".join(f"{s['good']}: {s['price']}cr ×{s['quantity']}"
                     for s in slots if not s["sold"])

# ─── REMOTE SEED ──────────────────────────────────────────────────────────────

def _remote_seed():
    if not REQUESTS_AVAILABLE: return random.randint(0, 99)
    try:
        r = _requests.get(
            "https://www.randomnumberapi.com/api/v1.0/random?min=0&max=99&count=1",
            timeout=2)
        r.raise_for_status(); return r.json()[0]
    except Exception:
        return random.randint(0, 99)

# ─── GENERAL HELPERS ──────────────────────────────────────────────────────────

def _get_int(prompt, lo=None, hi=None):
    while True:
        raw = input(prompt).strip().lower()
        if raw == "q":
            return "QUIT"
        try:
            v = int(raw)
            if lo is not None and v < lo: print(f"  ≥ {lo} please."); continue
            if hi is not None and v > hi: print(f"  ≤ {hi} please."); continue
            return v
        except ValueError:
            print("  Enter a number (or q to quit).")

def _col(t, w):         return str(t).ljust(w)
def _cargo_used(ship):  return sum(ship["cargo"].values())
def _cargo_free(ship):  return ship["max_cargo"] - _cargo_used(ship)

def _fuel_cost(origin, dest):
    i = P.PLANET_NAMES.index(origin)
    j = P.PLANET_NAMES.index(dest)
    return max(P.TRAVEL_MIN,
               min(P.TRAVEL_MAX,
                   abs(i-j) * P.TRAVEL_COST_PER_HOP
                   + random.randint(-P.TRAVEL_JITTER, P.TRAVEL_JITTER)))

# ─── NEWS FEED ────────────────────────────────────────────────────────────────

def print_news(ship, state):
    loc, m = ship["location"], state["month_index"]
    lines  = []

    if ship.get("passenger_slot"):
        pw = state.get("passenger_waiting")
        if pw:
            lines.append(L.NEWS_TRAVELER.format(
                shortname=pw["shortname"], destination=pw["destination"]))

    if loc in P.PLANET_FESTIVALS:
        good, fm, fname, _ = P.PLANET_FESTIVALS[loc]
        if m == fm:
            lines.append(L.NEWS_FESTIVAL.format(
                festival_name=fname, planet=loc, month_name=month_name(m)))

    hg = current_harvest_good(m)
    if hg:
        lines.append(L.NEWS_HARVEST.format(
            harvest_good=hg, month_name=month_name(m)))

    slots  = state.get("local_market", {}).get(loc, [])
    active = [s for s in slots if not s["sold"]]
    if active:
        lines.append(L.NEWS_MARKET.format(deals=_market_news_line(active)))

    if lines:
        print("\n" + "─"*50)
        for ln in lines: print(ln)
        print("─"*50)
    state["news_printed"] = True

# ─── DISPLAY ──────────────────────────────────────────────────────────────────

def show_status(ship, state):
    print("\n" + "═"*52)
    print(f"  STATUS  —  {date_str(state)}  (turn {state['turn']})")
    print("═"*52)
    print(f"  Location : {ship['location']}")
    print(f"  Credits  : {ship['credits']:,}")
    print(f"  Fuel     : {ship['fuel']} / {ship['max_fuel']}")
    print(f"  Cargo    : {_cargo_used(ship)} / {ship['max_cargo']} units")
    if ship["cargo"]:
        for g, q in ship["cargo"].items(): print(f"             • {g}: {q}")
    else:
        print("             (empty)")
    print(f"  Weapons  : {ship['weapons']}")
    ext = []
    if ship.get("broker_license"): ext.append("Broker License")
    if ship.get("radar"):          ext.append("Radar")
    if ship.get("booster"):        ext.append("Booster")
    if ship.get("passenger_slot"):
        p = ship.get("passenger")
        ext.append(f"Passenger: {p['shortname']} → {p['destination']}"
                   if p else "Passenger slot (empty)")
    if ext: print(f"  Upgrades : {', '.join(ext)}")
    if ship["location"] == P.FARM_PLANET and ship.get("farm_bought"):
        print(f"  🌿 You own a cinnamon farm on {P.FARM_PLANET}.")
    print("═"*52)

def show_market(ship, state):
    loc    = ship["location"]
    planet = state["planets"][loc]
    m      = state["month_index"]

    fg, fb = _festival_boost(loc, m)
    if fg:
        print(f"\n  🎊 {P.PLANET_FESTIVALS[loc][2].upper()} this month! {fg} +{fb}cr")

    print(f"\n── MARKET: {loc} ──────────────────────────────────────")
    print(f"  {'Good':<18} {'Sell':>6} {'Buy':>6} {'Stock':>6}  {'Role'}")
    print(f"  {'─'*18} {'─'*6} {'─'*6} {'─'*6}  {'─'*12}")
    for good in planet["goods"]:
        sp    = sell_price(state, loc, good)
        bp    = buy_price(state, loc, good)
        stock = get_stk(state, loc, good)
        if good == planet["production"]:
            role = "◀ SPICE"
        elif good in planet["ind_production"]:
            role = "◀ INDUSTRY"
        elif good == planet["demand"]:
            role = "▶ DEMAND"
        else:
            role = ""
        print(f"  {good:<18} {sp:>6} {bp:>6} {stock:>6}  {role}")
    print()
    print("  [1] Buy   [2] Sell   [3] Travel")
    print("  [4] Status   [5] Price Check   [6] Promenade")
    print("  [8] Engineering Bay   [9] Save   [q] Quit")

# ─── TRADE ────────────────────────────────────────────────────────────────────

def do_buy(ship, state):
    loc    = ship["location"]
    planet = state["planets"][loc]
    if _cargo_free(ship) == 0:
        print("Cargo hold is full!"); return
    goods = planet["goods"]
    print("\n── BUY ──────────────────────────────────────────────")
    for i, good in enumerate(goods, 1):
        bp    = buy_price(state, loc, good)
        stock = get_stk(state, loc, good)
        print(f"  [{i}] {good:<18} {bp:>6} cr/unit  (stock: {stock})")
    print("  [0] Cancel")
    ch = _get_int("Choose good: ", 0, len(goods))
    if ch == "QUIT": return "QUIT"
    if ch == 0: return
    good  = goods[ch-1]
    bp    = buy_price(state, loc, good)
    stock = get_stk(state, loc, good)
    max_b = min(ship["credits"] // bp, _cargo_free(ship), stock)
    if max_b <= 0:
        print(f"  {'Out of stock here.' if stock == 0 else 'Not enough credits or space.'}"); return
    amt = _get_int(f"How many {good}? (0 cancel, max {max_b}): ", 0, max_b)
    if amt == "QUIT": return "QUIT"
    if amt == 0: return
    ship["credits"] -= amt * bp
    ship["cargo"][good] = ship["cargo"].get(good, 0) + amt
    set_stk(state, loc, good, stock - amt)
    print(f"✓ Bought {amt}× {good} for {amt*bp:,} cr.  Stock now: {get_stk(state, loc, good)}")

def do_sell(ship, state):
    if not ship["cargo"]:
        print("Cargo hold is empty!"); return
    loc         = ship["location"]
    cargo_items = list(ship["cargo"].items())
    print("\n── SELL ─────────────────────────────────────────────")
    for i, (good, qty) in enumerate(cargo_items, 1):
        sp   = sell_price(state, loc, good)
        room = _stk_max(good) - get_stk(state, loc, good)
        print(f"  [{i}] {good:<18} {qty:>4} @ {sp:>6} cr  (market room: {room})")
    print("  [0] Cancel")
    ch = _get_int("Choose good: ", 0, len(cargo_items))
    if ch == "QUIT": return "QUIT"
    if ch == 0: return
    good, available = cargo_items[ch-1]
    sp    = sell_price(state, loc, good)
    stock = get_stk(state, loc, good)
    room  = _stk_max(good) - stock
    if room <= 0:
        print(f"  {good} market is full here. Try another planet."); return
    max_s = min(available, room)
    amt   = _get_int(f"How many {good}? (max {max_s}): ", 1, max_s)
    if amt == "QUIT": return "QUIT"
    gross = amt * sp
    tax   = max(P.SALE_TAX_MIN, math.ceil(gross * P.SALE_TAX_RATE))
    net   = gross - tax
    ship["credits"] += net
    ship["cargo"][good] -= amt
    if ship["cargo"][good] <= 0: del ship["cargo"][good]
    set_stk(state, loc, good, stock + amt)
    print(f"✓ Sold {amt}× {good} for {gross:,} cr.  Tax: {tax}.  Net: {net:,} cr.")

# ─── TRAVEL ───────────────────────────────────────────────────────────────────

def do_travel(ship, state):
    if ship["fuel"] < P.MIN_FUEL_TO_DEPART:
        print(f"Need ≥{P.MIN_FUEL_TO_DEPART} fuel. Refuel in Engineering Bay."); return
    other = [p for p in P.PLANET_NAMES if p != ship["location"]]
    print("\n── TRAVEL ───────────────────────────────────────────")
    for i, p in enumerate(other, 1):
        print(f"  [{i}] {p:<16}  ~{_fuel_cost(ship['location'], p)} fuel")
    print("  [0] Cancel")
    ch = _get_int("Destination: ", 0, len(other))
    if ch == "QUIT": return "QUIT"
    if ch == 0: return
    dest = other[ch-1]
    fc   = _fuel_cost(ship["location"], dest)
    if ship["fuel"] - fc < P.MIN_FUEL_TO_DEPART:
        print(f"Not enough fuel. Need {fc}+{P.MIN_FUEL_TO_DEPART} reserve."); return

    random.seed(_remote_seed())
    ship["fuel"]         -= fc
    ship["location"]      = dest
    state["news_printed"] = False
    advance_time(state)
    print(f"\n🚀 Jumped to {dest}. Fuel used: {fc}. Date: {date_str(state)}")

    # Roll fresh local market for destination
    state["local_market"][dest] = _roll_local_market(state, dest)

    # Small arrival price jitter
    for good in state["planets"][dest]["base_prices"]:
        state["planets"][dest]["base_prices"][good] = _clamp_base(
            good, state["planets"][dest]["base_prices"][good] + random.randint(-3, 3))
    random.seed()

    pc = P.PIRATE_RADAR_CHANCE if ship.get("radar") else P.PIRATE_BASE_CHANCE
    if random.random() < pc:
        alive = _pirate_encounter(ship, state)
        if not alive: return "GAME_OVER"
    else:
        roll = random.random(); cum = 0.0
        for key, prob in P.TRAVEL_EVENT_PROBS.items():
            cum += prob
            if roll < cum:
                _travel_event(key, ship, state, dest); break

    _deliver_passenger(ship, state)
    _spawn_passenger(ship, state)
    _fire_random_event(state)

def _travel_event(key, ship, state, dest):
    if key == "festival":
        for good in state["planets"][dest]["base_prices"]:
            state["planets"][dest]["base_prices"][good] = int(
                state["planets"][dest]["base_prices"][good] * 1.1)
        print(f"🎉 SPICE FESTIVAL on {dest}! All prices +10%.")
    elif key == "fuel_leak":
        lost = random.randint(P.FUEL_LEAK_MIN, P.FUEL_LEAK_MAX)
        ship["fuel"] = max(0, ship["fuel"] - lost)
        print(f"🔧 FUEL LEAK mid-jump. Lost {lost} fuel.")
    elif key == "mystery_cargo":
        amt = P.MYSTERY_CARGO_AMOUNT
        if _cargo_free(ship) >= amt:
            ship["cargo"]["Mystery Crate"] = ship["cargo"].get("Mystery Crate", 0) + amt
            print(f"📦 Drifting pod attached. +{amt} Mystery Crate.")
        else:
            print("📦 Drifting pod — no room. It drifts on.")

# ─── PIRATES ──────────────────────────────────────────────────────────────────

def _pirate_encounter(ship, state):
    state["piratangst"] += 1
    angst = state["piratangst"]
    fm    = P.PIRATE_FLEE_MULT_BOOST if ship.get("booster") else P.PIRATE_FLEE_MULT
    fc    = max(0, min(fm * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))
    print("\n" + "⚠"*50)
    print(f"  PIRATE INTERCEPT!  (Angst: {angst})")
    print("⚠"*50)
    print(f"\n  [1] Fight ({ship['weapons']} weapons)  [2] Flee ({fc} fuel)")
    print(f"  [3] Bribe ({state['piratbribe']} cr)    [4] Drop Cargo")
    print(f"  [5] Bluff (auto if cargo≤10)   [6] Surrender (GAME OVER)")
    return _pr(ship, state, _get_int("Choose: ", 1, 6), excl=None)

def _pr(ship, state, choice, excl):
    if choice == "QUIT":
        # Can't quit mid-pirate — force a choice
        print("  You can't run from pirates like that. Pick an option.")
        return _pirate_encounter(ship, state)

    angst = state["piratangst"]
    fm    = P.PIRATE_FLEE_MULT_BOOST if ship.get("booster") else P.PIRATE_FLEE_MULT
    fc    = max(0, min(fm * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))

    if choice == 1:
        pp = max(1, angst // 20)
        state["piratangst"] += 2
        print(f"\n  Pirate power: {pp}  vs  Your weapons: {ship['weapons']}")
        if ship["weapons"] < pp:
            _drop_half(ship); print("  Outgunned! Lost half cargo.")
        elif ship["weapons"] == pp:
            print("  Standoff. Pirate backs off. You're 'The Porcupine'.")
        else:
            b = P.PIRATE_BOUNTY_PER_ANGST * angst
            ship["credits"] += b; state["piratangst"] += 3
            print(f"  Pirate obliterated! Bounty: {b:,} cr.")
        return True
    elif choice == 2:
        if ship["fuel"] - fc < P.MIN_FUEL_TO_DEPART:
            print(f"  Not enough fuel to flee (need {fc})."); return _pr_retry(ship, state, 2)
        ship["fuel"] -= fc; print(f"  Escaped! Fuel burned: {fc}."); return True
    elif choice == 3:
        if ship["credits"] < state["piratbribe"]:
            loss = ship["credits"]; ship["credits"] = 0
            print(f"  Can't afford bribe. Lost {loss} cr.")
        else:
            ship["credits"] -= state["piratbribe"]
            state["piratangst"] = max(0, state["piratangst"] - 3)
            print(f"  Paid {state['piratbribe']} cr. They wave you through.")
        state["piratbribe"] += 100
        print(f"  Next bribe: {state['piratbribe']} cr."); return True
    elif choice == 4:
        if not ship["cargo"]:
            loss = min(200, ship["credits"]); ship["credits"] -= loss
            print(f"  Nothing to drop. They take {loss} cr.")
        else:
            _drop_half(ship); state["piratangst"] = max(0, state["piratangst"] - 2)
            print("  Jettisoned half cargo. Pirates leave.")
        return True
    elif choice == 5:
        total = sum(ship["cargo"].values())
        if total <= 10:
            print("  'Nothing here.' Auto-pass.")
        elif random.random() < 0.5:
            print("  Legendary bluff. Pirate warps off.")
        else:
            print("  Bluff failed. Bluff burned for this encounter.")
            state["piratangst"] += 2
            return _pr_retry(ship, state, 5)
        return True
    elif choice == 6:
        if input("\n  Sure? Sold as crypto miner on Zeta-9. [yes/no]: ").strip().lower() == "yes":
            print("\n  Stripped. Six months later: blockchain miner on Zeta-9.")
            print("  The smell of saffron is your last memory of freedom.")
            print("\n  ─── GAME OVER ───"); return False
        print("  You reconsider."); return _pirate_encounter(ship, state)
    return True

def _pr_retry(ship, state, excl):
    angst = state["piratangst"]
    fm    = P.PIRATE_FLEE_MULT_BOOST if ship.get("booster") else P.PIRATE_FLEE_MULT
    fc    = max(0, min(fm * angst, ship["fuel"] - P.MIN_FUEL_TO_DEPART))
    opts  = []
    if excl != 1: opts.append(("1", f"Fight ({ship['weapons']} weapons)"))
    if excl != 2: opts.append(("2", f"Flee ({fc} fuel)"))
    if excl != 3: opts.append(("3", f"Bribe ({state['piratbribe']} cr)"))
    if excl != 4: opts.append(("4", "Drop Cargo"))
    if excl != 5: opts.append(("5", "Bluff"))
    opts.append(("6", "Surrender (GAME OVER)"))
    print()
    for k, l in opts: print(f"  [{k}] {l}")
    valid = [k for k, _ in opts]
    while True:
        raw = input("Choose: ").strip()
        if raw in valid: return _pr(ship, state, int(raw), excl=excl)
        print(f"  Choose from: {', '.join(valid)}")

def _drop_half(ship):
    for g in list(ship["cargo"].keys()):
        d = max(1, math.ceil(ship["cargo"][g] / 2))
        ship["cargo"][g] -= d
        if ship["cargo"][g] <= 0: del ship["cargo"][g]
        print(f"  Dropped {d}× {g}.")

# ─── PASSENGERS ───────────────────────────────────────────────────────────────

def _spawn_passenger(ship, state):
    if not ship.get("passenger_slot") or state.get("passenger_waiting"): return
    if random.random() < P.PASSENGER_SPAWN_CHANCE:
        p = random.choice(L.PASSENGER_ROSTER).copy()
        p["destination"] = random.choice(
            [pl for pl in P.PLANET_NAMES if pl != ship["location"]])
        state["passenger_waiting"] = p

def _deliver_passenger(ship, state):
    p = ship.get("passenger")
    if p and p["destination"] == ship["location"]:
        print("\n" + "─"*50)
        print(p["exit_text"])
        ship["credits"] += P.PASSENGER_DELIVERY_PAY
        print(f"  +{P.PASSENGER_DELIVERY_PAY} credits received.")
        print("─"*50)
        ship["passenger"] = None

# ─── PRICE CHECK ──────────────────────────────────────────────────────────────

def do_price_check(ship, state):
    if not ship.get("broker_license"):
        print("\n  Need Galactic Broker License. Buy at Nexus for 1000 cr."); return
    W = [14, 16, 7, 7, 7, 7, 12]
    sep = "  " + "─"*(sum(W)+6)
    print("\n── PRICE CHECK (ALL PLANETS) ────────────────────────")
    print(f"  {_col('Planet',W[0])} {_col('Good',W[1])} "
          f"{_col('Base',W[2])} {_col('Sell',W[3])} {_col('Buy',W[4])} "
          f"{_col('Stock',W[5])} {_col('Role',W[6])}")
    print(sep)
    for pn in P.PLANET_NAMES:
        planet = state["planets"][pn]
        for good in planet["goods"]:
            if good == planet["production"]:
                role = "SPICE"
            elif good in planet["ind_production"]:
                role = "INDUSTRY"
            elif good == planet["demand"]:
                role = "DEMAND"
            else:
                role = ""
            print(f"  {_col(pn,W[0])} {_col(good,W[1])} "
                  f"{_col(planet['base_prices'][good],W[2])} "
                  f"{_col(sell_price(state,pn,good),W[3])} "
                  f"{_col(buy_price(state,pn,good),W[4])} "
                  f"{_col(get_stk(state,pn,good),W[5])} "
                  f"{_col(role,W[6])}")
        print(sep)

# ─── LOCAL MARKET ─────────────────────────────────────────────────────────────

def visit_local_market(ship, state):
    loc    = ship["location"]
    slots  = state["local_market"].get(loc, [])
    while True:
        active = [s for s in slots if not s["sold"]]
        print(f"\n── LOCAL MARKET  —  {loc} ──────────────────────────")
        if not active:
            print("  All traders have left. Check back next visit.")
            input("  [Enter to return...]"); return
        for i, s in enumerate(active, 1):
            print(f"  [{i}] {s['good']:<18} {s['price']:>6} cr/unit  ×{s['quantity']}")
        print("  [0] Back")
        ch = _get_int("Choose trader: ", 0, len(active))
        if ch == "QUIT": return "QUIT"
        if ch == 0: return
        slot = active[ch-1]
        good, bp, qty = slot["good"], slot["price"], slot["quantity"]
        if _cargo_free(ship) == 0:
            print("  Cargo hold is full!"); continue
        max_b = min(ship["credits"] // bp, _cargo_free(ship), qty)
        if max_b <= 0:
            print("  Not enough credits or cargo space."); continue
        print(f"\n  {good} at {bp} cr/unit. Max: {max_b}")
        amt = _get_int(f"  How many? (0 = leave trader, max {max_b}): ", 0, max_b)
        if amt == "QUIT": return "QUIT"
        if amt == 0:
            print("  The trader shifts nervously but stays."); continue
        slot["sold"] = True
        ship["credits"] -= amt * bp
        ship["cargo"][good] = ship["cargo"].get(good, 0) + amt
        print(f"✓ Bought {amt}× {good} for {amt*bp:,} cr.")
        print("  Trader pockets credits and vanishes into the crowd.")

# ─── FLEET SUPPLY DEPOT ───────────────────────────────────────────────────────

def visit_fleet_depot(ship, state):
    """Terra-only. Sell-only at fixed prices. Goods vanish — no stockpile."""
    cargo_items = [(g, q) for g, q in ship["cargo"].items()
                   if g in P.FLEET_DEPOT_PRICES]
    while True:
        cargo_items = [(g, q) for g, q in ship["cargo"].items()
                       if g in P.FLEET_DEPOT_PRICES]
        print(f"\n── FLEET SUPPLY DEPOT  —  Terra ────────────────────")
        print(f"  Fixed buy prices. No haggling. Goods absorbed into fleet supply.")
        print()
        if not cargo_items:
            print("  You have nothing the fleet wants right now.")
            input("  [Enter to return...]"); return
        print(f"  {'Good':<18} {'Have':>5} {'Price':>7}  {'Value':>8}")
        print(f"  {'─'*18} {'─'*5} {'─'*7}  {'─'*8}")
        for i, (good, qty) in enumerate(cargo_items, 1):
            price = P.FLEET_DEPOT_PRICES[good]
            print(f"  [{i}] {good:<18} {qty:>5} {price:>7}cr  {qty*price:>7,}cr")
        print("  [0] Back")
        ch = _get_int("Choose good to sell: ", 0, len(cargo_items))
        if ch == "QUIT": return "QUIT"
        if ch == 0: return
        good, available = cargo_items[ch-1]
        price = P.FLEET_DEPOT_PRICES[good]
        amt = _get_int(f"  How many {good}? (max {available}): ", 1, available)
        if amt == "QUIT": return "QUIT"
        gross = amt * price
        tax   = max(P.SALE_TAX_MIN, math.ceil(gross * P.SALE_TAX_RATE))
        net   = gross - tax
        ship["credits"] += net
        ship["cargo"][good] -= amt
        if ship["cargo"][good] <= 0: del ship["cargo"][good]
        print(f"✓ Sold {amt}× {good} to Fleet for {gross:,} cr.  Tax: {tax}.  Net: {net:,} cr.")
        print("  A quartermaster stamps your manifest and the crates disappear.")

# ─── FARM ─────────────────────────────────────────────────────────────────────

def visit_farm(ship, state):
    while True:
        print("\n" + "="*50)
        print(random.choice(L.FARM_FLUFF))
        print("="*50)
        print("  [1] Stay a little longer   [0] Return to the stars")
        ch = input("Choose: ").strip().lower()
        if ch == "0" or ch == "q":
            print("You leave the farm, ready for the galaxy again."); break

# ─── CANTINA ──────────────────────────────────────────────────────────────────

def visit_cantina(ship, state):
    cantina = L.cantinas[ship["location"]]
    while True:
        pw  = state.get("passenger_waiting")
        hq  = ship.get("passenger_slot", False)
        print(f"\n── {cantina['name'].upper()} ({ship['location']}) ───────────────────")
        print("  [1] Drink   [2] Advice")
        if hq: print(f"  [3] Traveler — {pw['shortname']+' → '+pw['destination'] if pw else '(none)'}")
        print("  [4] Rest (1 month)   [0] Back")
        ch = input("Choose: ").strip().lower()

        if ch == "q": return "QUIT"
        elif ch == "1":
            drink = cantina["drink"]
            dc    = max(1, int(sell_price(state, ship["location"],
                                          drink["ingredient"]) * 0.5))
            if ship["credits"] < dc:
                print(f"  Can't afford {drink['name']} ({dc} cr).")
            else:
                ship["credits"] -= dc
                print(f"\n  {drink['name']} — {dc} cr.")
                print(f"  {random.choice(drink['fluff'])}")
        elif ch == "2":
            pn, adv = L.random_advice()
            print(f"\n  [Bartender — {pn.upper()}]: {adv}")
        elif ch == "3":
            if not hq: print("  Invalid.")
            elif not pw: print("  Nobody looking for a ride.")
            else:
                print(f"\n  {pw['fullname']}\n  {pw['cantina_text']}")
                print(f"  Destination: {pw['destination']}")
                if ship.get("passenger"):
                    print(f"  (Replacing {ship['passenger']['shortname']} — they stay here.)")
                if input("  Take them aboard? [y/n]: ").strip().lower() == "y":
                    ship["passenger"] = pw
                    state["passenger_waiting"] = None
                    print(f"  {pw['shortname']} boards.")
        elif ch == "4":
            print("\n" + "─"*50)
            print("  A month blurs by in the cantina.")
            _fire_random_event(state)
            print("─"*50)
            input("  [Enter...]")
            advance_time(state)
            _spawn_passenger(ship, state)
            print(f"  Date: {date_str(state)}")
        elif ch == "0":
            break
        else:
            print("  Invalid choice.")

# ─── INFOBROKER ───────────────────────────────────────────────────────────────

def visit_infobroker(ship, state):
    while True:
        print("\n── INFOBROKER ───────────────────────────────────────")
        print("  [1] Goods   [2] Harvest   [3] Festivals   [0] Back")
        ch = input("Choose: ").strip().lower()
        if ch == "q": return "QUIT"
        if ch == "1":   L.infobroker_goods_table()
        elif ch == "2": L.infobroker_harvest_table()
        elif ch == "3": L.infobroker_festival_table()
        elif ch == "0": break
        else: print("  Invalid.")

# ─── CONCERT ──────────────────────────────────────────────────────────────────

def visit_concert(ship, state):
    t = P.CONCERT_TICKET
    if ship["credits"] < t:
        print(f"\n  Ticket: {t} cr. Too broke right now."); return
    ship["credits"] -= t
    print(f"\n  You pay {t} cr and take your seat...")

    if not SONGS:
        ship["credits"] += t
        print("\n" + L.CONCERT_NO_SHOW)
        return

    song = random.choice(SONGS)
    print("\n" + "★"*52)
    print(f"  NOW PLAYING: {song.get('fullname', song.get('shortname', '?'))}")
    print("★"*52 + "\n")
    print(song.get("text", "(no lyrics)"))
    if song.get("art"): print(); print(song["art"])
    print("\n" + "★"*52)

# ─── PROMENADE ────────────────────────────────────────────────────────────────

def visit_promenade(ship, state):
    loc = ship["location"]
    while True:
        print(f"\n── PROMENADE  —  {loc} ──────────────────────────────")
        print(f"  [1] Cantina   [2] Infobroker")
        print(f"  [3] Concert [{P.CONCERT_TICKET} cr]   [4] Local Market")
        if loc == P.FARM_PLANET:
            lbl = "Visit Farm" if ship.get("farm_bought") else f"Buy Farm [{P.FARM_COST:,} cr]"
            print(f"  [f] {lbl}")
            print(f"  [s] Fleet Supply Depot")
        print("  [0] Back to Spaceport")
        ch = input("Choose: ").strip().lower()

        if ch == "q": return "QUIT"
        elif ch == "1":
            r = visit_cantina(ship, state)
            if r == "QUIT": return "QUIT"
        elif ch == "2":
            r = visit_infobroker(ship, state)
            if r == "QUIT": return "QUIT"
        elif ch == "3": visit_concert(ship, state)
        elif ch == "4":
            r = visit_local_market(ship, state)
            if r == "QUIT": return "QUIT"
        elif ch == "f" and loc == P.FARM_PLANET:
            if not ship.get("farm_bought"):
                print(f"\n  Buy cinnamon farm for {P.FARM_COST:,} cr? (Have {ship['credits']:,})")
                if ship["credits"] >= P.FARM_COST:
                    if input("  Confirm [y/n]: ").strip().lower() == "y":
                        ship["credits"] -= P.FARM_COST
                        ship["farm_bought"] = True
                        print("  🌿 You now own a cinnamon farm on Terra.")
                else:
                    print(f"  Need {P.FARM_COST - ship['credits']:,} more credits.")
            else:
                visit_farm(ship, state)
        elif ch == "s" and loc == P.FLEET_DEPOT_PLANET:
            r = visit_fleet_depot(ship, state)
            if r == "QUIT": return "QUIT"
        elif ch == "0": break
        else: print("  Invalid.")

# ─── ENGINEERING BAY ──────────────────────────────────────────────────────────

def visit_engineering_bay(ship, state):
    while True:
        print("\n── ENGINEERING BAY ──────────────────────────────────")
        print(f"  Fuel: {ship['fuel']}/{ship['max_fuel']}  Credits: {ship['credits']:,}")
        print("  [1] Fuel Up   [2] Drain   [3] Upgrades   [0] Back")
        ch = input("Choose: ").strip().lower()
        if ch == "q": return "QUIT"
        if ch == "1":   _fuel_up(ship)
        elif ch == "2": _drain_fuel(ship)
        elif ch == "3": _upgrades_menu(ship, state)
        elif ch == "0": break
        else: print("  Invalid.")

def _fuel_up(ship):
    space = ship["max_fuel"] - ship["fuel"]
    if space <= 0: print("  Tank full."); return
    seen = set(); disp = []
    for n in [100, 200, 500, 1000, space]:
        a = min(n, space)
        if a > 0 and a not in seen: seen.add(a); disp.append(a)
    for i, a in enumerate(disp, 1):
        print(f"  [{i}] +{'FULL' if a==space else a} fuel → {a*P.FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(disp))
    if c == "QUIT" or c == 0: return
    a = disp[c-1]; cost = a * P.FUEL_PRICE
    if ship["credits"] < cost:
        print(f"  Need {cost:,}, have {ship['credits']:,}."); return
    ship["credits"] -= cost
    ship["fuel"] = min(ship["max_fuel"], ship["fuel"] + a)
    print(f"✓ +{a} fuel. Tank: {ship['fuel']}/{ship['max_fuel']}")

def _drain_fuel(ship):
    dr = ship["fuel"] - P.MIN_FUEL_TO_DEPART
    if dr <= 0: print(f"  Must keep ≥{P.MIN_FUEL_TO_DEPART} fuel."); return
    opts = sorted(set(min(n, dr) for n in [100, 200, 500, 1000, int(ship["fuel"]*0.9)]
                      if 0 < min(n, dr) <= dr))
    for i, a in enumerate(opts, 1):
        print(f"  [{i}] Drain {'90%' if a==int(ship['fuel']*0.9) else a} → +{a*P.FUEL_PRICE:,} cr")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(opts))
    if c == "QUIT" or c == 0: return
    a = opts[c-1]
    ship["fuel"] -= a; ship["credits"] += a * P.FUEL_PRICE
    print(f"✓ Drained {a}. Tank: {ship['fuel']}/{ship['max_fuel']}. +{a*P.FUEL_PRICE:,} cr.")

def _upgrades_menu(ship, state):
    loc = ship["location"]
    avail = [(uid, P.UPGRADES_DATA[uid]) for uid in P.UPGRADES_DATA
             if (P.UPGRADES_DATA[uid]["planet"] is None
                 or P.UPGRADES_DATA[uid]["planet"] == loc)
             and uid not in ship["upgrades_bought"]]
    print(f"\n── UPGRADES ({loc}) ────────────────────────────────")
    if not avail: print("  Nothing available (or all purchased)."); return
    for i, (uid, u) in enumerate(avail, 1):
        tag = f" [{u['planet']} only]" if u["planet"] else ""
        print(f"  [{i}] {u['name']}  —  {u['cost']:,} cr{tag}\n       {u['desc']}")
    print("  [0] Cancel")
    c = _get_int("Choose: ", 0, len(avail))
    if c == "QUIT" or c == 0: return
    uid, u = avail[c-1]
    if ship["credits"] < u["cost"]:
        print(f"  Need {u['cost']:,}, have {ship['credits']:,}."); return
    ship["credits"] -= u["cost"]
    UPGRADE_EFFECTS[uid](ship)
    ship["upgrades_bought"].append(uid)
    print(f"✓ {u['name']} installed.")

# ─── SAVE / LOAD ──────────────────────────────────────────────────────────────

def save_game(ship, state):
    data = {
        "ship":                   dict(ship),
        "planets_prices":         {n: {"base_prices": p["base_prices"]}
                                   for n, p in state["planets"].items()},
        "stockpiles":             state["stockpiles"],
        "local_market":           state.get("local_market", {}),
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
        for name, pd in data["planets_prices"].items():
            if name in planets:
                planets[name]["base_prices"].update(pd["base_prices"])
        state["stockpiles"]             = data.get("stockpiles", state["stockpiles"])
        state["local_market"]           = data.get("local_market", {})
        state["turn"]                   = data.get("turn", 1)
        state["month_index"]            = data.get("month_index", 0)
        state["year"]                   = data.get("year", P.START_YEAR)
        state["piratangst"]             = data.get("piratangst", P.PIRATE_START_ANGST)
        state["piratbribe"]             = data.get("piratbribe", P.PIRATE_START_BRIBE)
        state["galaxy_story_index"]     = data.get("galaxy_story_index", 0)
        state["passenger_waiting"]      = data.get("passenger_waiting")
        state["festival_drops_applied"] = set(data.get("festival_drops_applied", []))
        print(f"📂 Loaded from {P.SAVE_FILE}")
        return data["ship"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Load failed: {e}"); return None

# ─── INIT ─────────────────────────────────────────────────────────────────────

def _randomise_start_price(good, param_price):
    """Return a randomised starting price, averaged with the parameter value."""
    mn   = _price_min(good)
    mx   = _price_max(good)
    dfl  = P.GOOD_DATA[good][2]  # mean/default from GOOD_DATA
    rand_val = random.uniform(mn, dfl * P.RAND_PRICE_HIGH_MULT)
    raw  = (rand_val + param_price) / 2
    # Clamp to [30%, 300%] of default, then clamp to absolute [min, max]
    lo   = max(mn, dfl * P.RAND_PRICE_MIN_FRAC)
    hi   = min(mx, dfl * P.RAND_PRICE_MAX_FRAC)
    return int(max(lo, min(hi, raw)))

def _randomise_start_stk(good, param_stk):
    """Return a randomised starting stockpile, averaged with the parameter value."""
    mx       = _stk_max(good)
    rand_val = random.uniform(mx * P.RAND_STK_LOW_FRAC, mx * P.RAND_STK_HIGH_FRAC)
    raw      = (rand_val + param_stk) / 2
    return int(max(0, min(mx, raw)))

def init_planets(randomise=False):
    planets = {}
    for pname, pdata in P.planets_template.items():
        new_prices = {}
        for good, price in pdata["base_prices"].items():
            if randomise:
                new_prices[good] = _randomise_start_price(good, price)
            else:
                new_prices[good] = _clamp_base(good, price + random.randint(-10, 10))
        planets[pname] = {**pdata, "base_prices": new_prices}
    return planets

def init_stockpiles(planets, randomise=False):
    stk = {}
    for pname, planet in planets.items():
        stk[pname] = {}
        for good in planet["base_prices"]:
            param_stk = _stk_start(pname, good)
            if randomise:
                stk[pname][good] = _randomise_start_stk(good, param_stk)
            else:
                stk[pname][good] = param_stk
    return stk

def new_ship():
    return copy.deepcopy(P.SHIP_START)

def new_state(planets, randomise=False):
    return {
        "planets":                planets,
        "stockpiles":             init_stockpiles(planets, randomise=randomise),
        "local_market":           {},
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

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═"*55)
    print("  SPICE SPACE TRADER  v12")
    print("  Trade spices. Dodge pirates. Maybe buy a farm.")
    print("═"*55)

    if os.path.exists(P.SAVE_FILE):
        if input("\nSave file found. Load it? [y/n]: ").strip().lower() == "y":
            # Load: init planets normally (no randomise), then overwrite from save
            planets = init_planets(randomise=False)
            state   = new_state(planets, randomise=False)
            loaded  = load_game(planets, state)
            ship    = loaded if loaded else new_ship()
            is_new_game = (loaded is None)
        else:
            is_new_game = True
    else:
        is_new_game = True

    if is_new_game:
        planets = init_planets(randomise=True)
        state   = new_state(planets, randomise=True)
        ship    = new_ship()

    # Roll local market for starting planet
    loc = ship["location"]
    if loc not in state["local_market"]:
        state["local_market"][loc] = _roll_local_market(state, loc)

    while True:
        if not state.get("news_printed"):
            print_news(ship, state)

        show_status(ship, state)
        show_market(ship, state)

        raw = input("\nChoose action: ").strip().lower()

        # Cheat code — handle before anything else
        if raw.startswith("!credits "):
            try: ship["credits"] += int(raw.split()[1])
            except (ValueError, IndexError): pass
            continue

        # Quit key
        if raw == "q":
            print(f"\nFinal credits: {ship['credits']:,}  |  {date_str(state)}")
            if ship.get("farm_bought"):
                print("You retired to your cinnamon farm. You won. 🌿")
            break

        try:
            action = int(raw)
        except ValueError:
            print("  Enter a number, or q to quit."); continue

        if action == 0:
            print("  Nothing to go back to here. Use [q] to quit.")
        elif action == 1:
            r = do_buy(ship, state)
            if r == "QUIT": break
        elif action == 2:
            r = do_sell(ship, state)
            if r == "QUIT": break
        elif action == 3:
            r = do_travel(ship, state)
            if r == "GAME_OVER": break
            if r == "QUIT": break
        elif action == 4: show_status(ship, state)
        elif action == 5: do_price_check(ship, state)
        elif action == 6:
            r = visit_promenade(ship, state)
            if r == "QUIT": break
        elif action == 8:
            r = visit_engineering_bay(ship, state)
            if r == "QUIT": break
        elif action == 9: save_game(ship, state)
        else: print("  Invalid action.")

    # Offer save on quit
    print()
    if input("Save before leaving? [y/n]: ").strip().lower() == "y":
        save_game(ship, state)
    print("Fair winds, trader.")

if __name__ == "__main__":
    main()
