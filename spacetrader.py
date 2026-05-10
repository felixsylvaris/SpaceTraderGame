"""
=============================================================
  SPICE SPACE TRADER v7  —  Improved Edition
=============================================================
Changes from v6:
  - requests-ready: RandomEventAPI + future SpaceTraderAPI hook
  - Proper event system (dict-driven, no fragile string parsing)
  - Fuel and cargo are now SEPARATE resources
  - Infinite recursion fixed (farm visit, cantina rest)
  - price_check() uses clean columnar formatting
  - Input validation loops everywhere
  - save_game() / load_game() via JSON
  - Distance-based travel fuel costs (planet index delta)
  - Pirate events have flee/bribe/fight options
  - Galaxy background story queue
=============================================================
"""

import random
import json
import os

# ── Optional requests (gracefully degraded if offline) ────────────────────────
try:
    import requests as _requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

SAVE_FILE = "spice_trader_save.json"

# ═══════════════════════════════════════════════════════════════════════════════
# REMOTE EVENT FEED  (requests hook — replace URL with a real endpoint later)
# ═══════════════════════════════════════════════════════════════════════════════

RANDOM_EVENT_API = "https://www.randomnumberapi.com/api/v1.0/random?min=0&max=99&count=1"

def fetch_remote_seed() -> int:
    """
    Fetches a random seed from a public API to make events less predictable.
    Falls back to local random if unavailable.
    """
    if not REQUESTS_AVAILABLE:
        return random.randint(0, 99)
    try:
        resp = _requests.get(RANDOM_EVENT_API, timeout=2)
        resp.raise_for_status()
        return resp.json()[0]
    except Exception:
        return random.randint(0, 99)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME DATA
# ═══════════════════════════════════════════════════════════════════════════════

PLANET_NAMES = ["Terra", "Zeta-9", "Void Colony", "Agrica", "Nexus"]  # order matters for distance

planets_template = {
    "Terra": {
        "production": "Cinnamon",
        "demand": "Allspice",
        "spices": ["Cinnamon", "Cardamom", "Vanilla", "Allspice", "Clove"],
        "base_prices": {
            "Cinnamon": 25,
            "Cardamom": 100,
            "Vanilla": 90,
            "Allspice": 100,
            "Clove": 70,
        },
        "farm_fluff": [
            "You sit on the porch of your cinnamon farm, sipping a warm drink. "
            "The sunset paints the orchard in gold, and the scent of spices fills the air.",
            "The cinnamon trees rustle in the breeze. A neighbor waves from across the field. "
            "'Harvest was good this year,' they say.",
            "The scent of cinnamon fills the air. You made it. No more fuel calculations, "
            "no more pirate attacks. Just peace.",
        ],
    },
    "Zeta-9": {
        "production": "Saffron",
        "demand": "Ginger",
        "spices": ["Saffron", "Turmeric", "Paprika", "Ginger", "Nutmeg"],
        "base_prices": {
            "Saffron": 100,
            "Turmeric": 50,
            "Paprika": 60,
            "Ginger": 90,
            "Nutmeg": 135,
        },
    },
    "Void Colony": {
        "production": "Void Pepper",
        "demand": "Cardamom",
        "spices": ["Void Pepper", "Saffron", "Ginger", "Cardamom", "Clove"],
        "base_prices": {
            "Void Pepper": 500,
            "Saffron": 200,
            "Ginger": 65,
            "Cardamom": 80,
            "Clove": 70,
        },
    },
    "Agrica": {
        "production": "Paprika",
        "demand": "Vanilla",
        "spices": ["Paprika", "Cinnamon", "Turmeric", "Vanilla", "Allspice"],
        "base_prices": {
            "Paprika": 30,
            "Cinnamon": 50,
            "Turmeric": 30,
            "Vanilla": 120,
            "Allspice": 80,
        },
    },
    "Nexus": {
        "production": "Clove",
        "demand": "Turmeric",
        "spices": ["Clove", "Void Pepper", "Nutmeg", "Saffron", "Turmeric"],
        "base_prices": {
            "Clove": 35,
            "Void Pepper": 750,
            "Nutmeg": 110,
            "Saffron": 175,
            "Turmeric": 40,
        },
    },
}

cantinas = {
    "Terra": {
        "name": "The Cinnamon Tavern",
        "drink": {
            "name": "Cinnamon Beer",
            "ingredient": "Cinnamon",
            "fluff": [
                "The warm, spicy beer fills your chest with nostalgia. It tastes like home.",
                "You take a sip. Sweet, spicy—exactly what you needed after a long day of haggling.",
                "The bartender winks. 'Made from Terra's finest. You won't find this anywhere else.'",
            ],
        },
    },
    "Zeta-9": {
        "name": "The Golden Saffron",
        "drink": {
            "name": "Saffron Mead",
            "ingredient": "Saffron",
            "fluff": [
                "Golden and rich, this mead tastes like liquid sunlight.",
                "The glass is lined with actual gold. Or maybe that's just the lighting.",
                "You feel fancy just holding it. The bartender smirks—you're clearly not from here.",
            ],
        },
    },
    "Void Colony": {
        "name": "The Pepper's Shadow",
        "drink": {
            "name": "Void Pepper Whiskey",
            "ingredient": "Void Pepper",
            "fluff": [
                "The whiskey burns like a supernova. You see stars. Maybe don't fly for a while.",
                "So strong it's rumored to power small starships. You feel invincible. (You are not.)",
                "The bartender warns you: 'One sip and you'll forget your name. Two and you'll forget your debts.'",
            ],
        },
    },
    "Agrica": {
        "name": "The Paprika Den",
        "drink": {
            "name": "Spiced Paprika Ale",
            "ingredient": "Paprika",
            "fluff": [
                "The ale is fiery and bold, just like Agrica's farmers. You cough. Worth it.",
                "The bartender slides you a glass. 'Careful, that's our house special.'",
                "You feel warmer immediately. Maybe it's the ale, maybe it's the hospitality.",
            ],
        },
    },
    "Nexus": {
        "name": "The Clove & Dagger",
        "drink": {
            "name": "Clove Rum",
            "ingredient": "Clove",
            "fluff": [
                "Smooth but packs a punch. Nexus traders swear by it to close deals.",
                "The bartender leans in. 'This one's on the house… if you tell me where you got that Void Pepper.'",
                "You sip it slowly. Complex, just like the deals made in this cantina.",
            ],
        },
    },
}

advice_pools = {
    "game": [
        "In theory it is simple: buy low, sell high. But life is more complex than that.",
        "Taking strangers on your ship can cause trouble—but all alone all the time gets boring.",
        "You can collect credits forever, but at some point there is nothing more to buy. "
        "Maybe it is time for that farm on Terra.",
        "Weapons are expensive to buy, but losing cargo to pirates costs more.",
        "Not all pirates are worth the fight. Bribery or running is also valid.",
        "Nexus bankers are all high on Void Pepper. They pay any price to get their fix.",
        "Upgrading your ship lets you seize opportunities you could not before.",
        "Bad trades from the past will not block good deals in the future.",
    ],
    "divorced": [
        "Never date a Psionic Girl. You will be judged by your thoughts, not your words.",
        "Some opportunities happen once. If you see a Space Whale, feast your eyes.",
        "If you have a cargo hold of Void Whiskey, do not drink it all in one night.",
        "You need to look into your heart to save yourself from your other self.",
        "There is no grand destiny, only semi-random rolls of unseen dice. We make our own.",
    ],
    "iroh": [
        "It is important to trade with many planets. Wide horizons reveal unseen opportunities.",
        "Life happens whether you manage it or not. But you can make it cozy and peaceful.",
        "Bad trades happen. Let go of pride and shame. Trading in anger leads to bad deals.",
        "Do not take more than your cargo can hold. Leave space for surprise opportunities.",
        "If you have a good ship and a few credits, you are better off than many. Keep going.",
        "You can accept errands from brokers, but do not let others decide your ultimate goal.",
    ],
}

# Galaxy background story — revealed one entry per cantina rest, in order
galaxy_story = [
    "A broker mentions in passing: the Senate voted to dissolve the Spice Trade Commission last cycle.",
    "Rumour has it a rogue freighter carrying 10,000 units of Void Pepper vanished near Nexus.",
    "The bartender lowers their voice: 'They say a Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.'",
    "A trader slaps down a news tablet: AGRICA DROUGHT—paprika yields expected to halve next season.",
    "Someone at the bar whispers: 'The old Void Colony governor was arrested. New one's... friendlier to black-market deals.'",
    "A weathered pilot says: 'I heard the jump lanes near Terra are being taxed now. Change is coming, friend.'",
    "The galaxy feels different lately. The old trade routes are shifting. Nobody knows where it leads.",
]


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL EVENTS  (dict-driven — no fragile string parsing)
# ═══════════════════════════════════════════════════════════════════════════════

def event_pirate_attack(ship, planets, destination):
    """
    Pirate encounter with three choices: fight, flee, bribe.
    Returns a result string.
    """
    print("\n⚠️  PIRATE INTERCEPT! A raider locks on to your ship.")
    print("  [1] Fight back")
    print("  [2] Dump cargo and flee")
    print("  [3] Pay the bribe (100 credits)")
    choice = _get_int("Choose: ", 1, 3)
    if choice == 1:
        if random.random() < 0.55:
            print("You drive them off! But your hull took a hit — lose 50 fuel.")
            ship["fuel"] = max(0, ship["fuel"] - 50)
            return "Fought off pirates (hull damage)"
        else:
            loss = min(ship["credits"] // 3, 300)
            ship["credits"] -= loss
            print(f"They board you. You lose {loss} credits in the struggle.")
            return f"Lost fight, lost {loss} credits"
    elif choice == 2:
        if ship["cargo"]:
            dumped = random.choice(list(ship["cargo"].keys()))
            lost = min(ship["cargo"][dumped], random.randint(5, 15))
            ship["cargo"][dumped] -= lost
            if ship["cargo"][dumped] <= 0:
                del ship["cargo"][dumped]
            print(f"You jettison {lost} units of {dumped} and escape into the dark.")
            return f"Fled, dumped {lost} {dumped}"
        else:
            print("Nothing to dump — you gun it and barely escape.")
            ship["fuel"] = max(0, ship["fuel"] - 30)
            return "Fled empty-handed"
    else:
        if ship["credits"] >= 100:
            ship["credits"] -= 100
            print("The pirate takes the 100-credit 'toll' and waves you through. Charming.")
            return "Bribed pirates (100 credits)"
        else:
            loss = ship["credits"]
            ship["credits"] = 0
            print(f"You can't afford the bribe! They take everything ({loss} credits).")
            return f"Stripped — lost all {loss} credits"


def event_spice_festival(ship, planets, destination):
    planet = planets[destination]
    for spice in planet["base_prices"]:
        planet["base_prices"][spice] = int(planet["base_prices"][spice] * 1.1)
    print(f"🎉 SPICE FESTIVAL on {destination}! All prices +10% today.")
    return "Spice festival — prices boosted"


def event_fuel_leak(ship, planets, destination):
    lost = random.randint(15, 35)
    ship["fuel"] = max(0, ship["fuel"] - lost)
    print(f"🔧 FUEL LEAK detected mid-jump. Lost {lost} fuel.")
    return f"Fuel leak — lost {lost} fuel"


def event_mystery_cargo(ship, planets, destination):
    if ship["max_cargo"] - sum(ship["cargo"].values()) >= 5:
        ship["cargo"]["Mystery Crate"] = ship["cargo"].get("Mystery Crate", 0) + 5
        print("📦 A drifting cargo pod attaches to your hull. You haul it aboard.")
        print("   Contents unknown. Could be worth something. Could be trouble.")
        return "Found mystery cargo (+5 Mystery Crate)"
    else:
        print("📦 A drifting cargo pod attaches to your hull — but you have no room. It drifts on.")
        return "Mystery cargo — no room"


TRAVEL_EVENTS = [
    (0.18, event_pirate_attack),
    (0.12, event_spice_festival),
    (0.10, event_fuel_leak),
    (0.08, event_mystery_cargo),
]


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE / LOAD
# ═══════════════════════════════════════════════════════════════════════════════

def save_game(ship, planets, galaxy_story_index):
    data = {
        "ship": ship,
        "planets": {
            name: {"base_prices": pdata["base_prices"]}
            for name, pdata in planets.items()
        },
        "galaxy_story_index": galaxy_story_index,
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"💾 Game saved to {SAVE_FILE}")
    except OSError as e:
        print(f"⚠️  Could not save: {e}")


def load_game(planets, galaxy_story_index):
    if not os.path.exists(SAVE_FILE):
        return None, galaxy_story_index
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        # Restore drifted prices into live planets dict
        for name, pdata in data["planets"].items():
            if name in planets:
                planets[name]["base_prices"].update(pdata["base_prices"])
        print(f"📂 Save file loaded from {SAVE_FILE}")
        return data["ship"], data.get("galaxy_story_index", 0)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Could not load save: {e}")
        return None, galaxy_story_index


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_int(prompt: str, lo: int = None, hi: int = None) -> int:
    """Loop until we get a valid integer in [lo, hi]."""
    while True:
        try:
            val = int(input(prompt))
            if lo is not None and val < lo:
                print(f"  Please enter a number ≥ {lo}.")
                continue
            if hi is not None and val > hi:
                print(f"  Please enter a number ≤ {hi}.")
                continue
            return val
        except ValueError:
            print("  Please enter a number.")


def _cargo_used(ship):
    return sum(ship["cargo"].values())


def _cargo_free(ship):
    return ship["max_cargo"] - _cargo_used(ship)


def _col(text, width):
    """Left-align text in a fixed-width column."""
    return str(text).ljust(width)


def _travel_fuel_cost(origin: str, destination: str) -> int:
    """
    Fuel cost scales with 'distance' (planet list index delta).
    Minimum 10, maximum 50.
    """
    i = PLANET_NAMES.index(origin)
    j = PLANET_NAMES.index(destination)
    dist = abs(i - j)
    base = dist * 12
    jitter = random.randint(-5, 5)
    return max(10, min(50, base + jitter))


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def show_status(ship):
    print("\n" + "═" * 45)
    print("  STATUS")
    print("═" * 45)
    print(f"  Location : {ship['location']}")
    print(f"  Credits  : {ship['credits']:,}")
    print(f"  Fuel     : {ship['fuel']} / {ship['max_fuel']}")
    print(f"  Cargo    : {_cargo_used(ship)} / {ship['max_cargo']} units")
    if ship["cargo"]:
        for spice, qty in ship["cargo"].items():
            print(f"             • {spice}: {qty}")
    else:
        print("             (empty)")
    if ship["location"] == "Terra" and ship["farm_bought"]:
        print("  🌿 You own a cinnamon farm here.")
    print("═" * 45)


def show_market(ship, planets):
    planet = planets[ship["location"]]
    print(f"\n── MARKET: {ship['location']} ──────────────────────────")
    print(f"  {'Spice':<18} {'Price':>6}  {'Role'}")
    print(f"  {'─'*18} {'─'*6}  {'─'*12}")
    for spice in planet["spices"]:
        price = planet["base_prices"][spice]
        role = ""
        if spice == planet["production"]:
            role = "◀ PRODUCTION"
        elif spice == planet["demand"]:
            role = "▶ DEMAND"
        print(f"  {spice:<18} {price:>6}  {role}")
    print()
    print("  [1] Buy   [2] Sell   [3] Travel   [4] Status")
    print("  [5] Price Check   [6] Farm / Buy Farm   [7] Cantina")
    print("  [8] Save   [0] Quit")


# ═══════════════════════════════════════════════════════════════════════════════
# TRADE
# ═══════════════════════════════════════════════════════════════════════════════

def buy_spice(ship, planets):
    planet = planets[ship["location"]]
    if _cargo_free(ship) == 0:
        print("Cargo hold is full!")
        return
    print("\n── BUY SPICES ──────────────────────────────────────")
    spices = planet["spices"]
    for i, spice in enumerate(spices, 1):
        print(f"  [{i}] {spice:<18} {planet['base_prices'][spice]:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose spice: ", 0, len(spices))
    if choice == 0:
        return
    spice = spices[choice - 1]
    price = planet["base_prices"][spice]
    max_buy = min(
        ship["credits"] // price,
        _cargo_free(ship),
    )
    if max_buy <= 0:
        print("Not enough credits or cargo space!")
        return
    print(f"  Max you can buy: {max_buy} units  (costs {max_buy * price:,} cr)")
    amount = _get_int(f"How many units of {spice}? (0 to cancel, max {max_buy}): ", 0, max_buy)
    if amount == 0:
        return
    cost = amount * price
    ship["credits"] -= cost
    ship["cargo"][spice] = ship["cargo"].get(spice, 0) + amount
    print(f"✓ Bought {amount}× {spice} for {cost:,} credits.")


def sell_spice(ship, planets):
    if not ship["cargo"]:
        print("Your cargo hold is empty!")
        return
    planet = planets[ship["location"]]
    cargo_items = list(ship["cargo"].items())
    print("\n── SELL SPICES ──────────────────────────────────────")
    for i, (spice, qty) in enumerate(cargo_items, 1):
        sell_price = planet["base_prices"].get(spice, 1)
        print(f"  [{i}] {spice:<18} {qty:>4} units @ {sell_price:>6} cr/unit")
    print("  [0] Cancel")
    choice = _get_int("Choose spice to sell: ", 0, len(cargo_items))
    if choice == 0:
        return
    spice, available = cargo_items[choice - 1]
    sell_price = planet["base_prices"].get(spice, 1)
    amount = _get_int(f"How many units of {spice}? (max {available}): ", 1, available)
    earnings = amount * sell_price
    ship["credits"] += earnings
    ship["cargo"][spice] -= amount
    if ship["cargo"][spice] <= 0:
        del ship["cargo"][spice]
    print(f"✓ Sold {amount}× {spice} for {earnings:,} credits.")


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL
# ═══════════════════════════════════════════════════════════════════════════════

def travel(ship, planets):
    other_planets = [p for p in PLANET_NAMES if p != ship["location"]]
    print("\n── TRAVEL ───────────────────────────────────────────")
    for i, planet in enumerate(other_planets, 1):
        cost = _travel_fuel_cost(ship["location"], planet)
        print(f"  [{i}] {planet:<16}  ~{cost} fuel")
    print("  [0] Cancel")
    choice = _get_int("Choose destination: ", 0, len(other_planets))
    if choice == 0:
        return

    destination = other_planets[choice - 1]
    fuel_cost = _travel_fuel_cost(ship["location"], destination)

    if fuel_cost > ship["fuel"]:
        print(f"Not enough fuel! Need {fuel_cost}, have {ship['fuel']}. Sell cargo to refuel.")
        return

    # Fetch remote seed for event roll (requests hook)
    seed = fetch_remote_seed()
    random.seed(seed)

    ship["fuel"] -= fuel_cost
    ship["location"] = destination
    print(f"\n🚀 Jumped to {destination}. Fuel used: {fuel_cost}. Remaining: {ship['fuel']}")

    # Drift neutral prices on arrival
    planet = planets[destination]
    for spice in planet["base_prices"]:
        if spice != planet["production"] and spice != planet["demand"]:
            planet["base_prices"][spice] = max(
                1, planet["base_prices"][spice] + random.randint(-10, 10)
            )

    # Roll travel events
    roll = random.random()
    cumulative = 0.0
    for probability, event_fn in TRAVEL_EVENTS:
        cumulative += probability
        if roll < cumulative:
            event_fn(ship, planets, destination)
            break

    # Re-seed with system random for the rest of the session
    random.seed()


# ═══════════════════════════════════════════════════════════════════════════════
# PRICE CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def price_check(planets):
    W_PLANET = 14
    W_SPICE = 16
    W_PRICE = 7
    W_ROLE = 12
    header = (
        f"  {_col('Planet', W_PLANET)} {_col('Spice', W_SPICE)} "
        f"{_col('Price', W_PRICE)} {_col('Role', W_ROLE)}"
    )
    sep = "  " + "─" * (W_PLANET + W_SPICE + W_PRICE + W_ROLE + 3)
    print("\n── PRICE CHECK ──────────────────────────────────────")
    print(header)
    print(sep)
    for planet_name in PLANET_NAMES:
        planet = planets[planet_name]
        for spice in planet["spices"]:
            price = planet["base_prices"][spice]
            role = ""
            if spice == planet["production"]:
                role = "PRODUCTION"
            elif spice == planet["demand"]:
                role = "DEMAND"
            print(
                f"  {_col(planet_name, W_PLANET)} {_col(spice, W_SPICE)} "
                f"{_col(price, W_PRICE)} {_col(role, W_ROLE)}"
            )
        print(sep)


# ═══════════════════════════════════════════════════════════════════════════════
# FARM
# ═══════════════════════════════════════════════════════════════════════════════

def visit_farm(ship, planets):
    """Visit the cinnamon farm — iterative, no recursion."""
    while True:
        print("\n" + "=" * 50)
        print(random.choice(planets["Terra"]["farm_fluff"]))
        print("=" * 50)
        print("\n  [1] Stay a little longer")
        print("  [2] Return to the stars")
        choice = input("Choose: ").strip()
        if choice == "2":
            print("\nYou leave the farm, ready to face the galaxy again... or not.")
            break
        elif choice == "1":
            continue  # loop shows another fluff
        else:
            print("You doze off on the porch. Time passes.")


# ═══════════════════════════════════════════════════════════════════════════════
# CANTINA
# ═══════════════════════════════════════════════════════════════════════════════

def visit_cantina(ship, planets, galaxy_story_index):
    """Cantina menu — iterative, no recursion. Returns updated story index."""
    cantina = cantinas[ship["location"]]
    while True:
        print(f"\n── {cantina['name'].upper()} ({ship['location']}) ────────────────────")
        print("  [1] I need a drink")
        print("  [2] Ask for advice")
        print("  [3] Rest for a moment")
        print("  [9] Back to spaceport")
        choice = input("Choose: ").strip()

        if choice == "1":
            drink = cantina["drink"]
            ingredient_price = planets[ship["location"]]["base_prices"].get(drink["ingredient"], 10)
            drink_cost = max(1, int(ingredient_price * 0.5))
            if ship["credits"] < drink_cost:
                print(f"You can't afford a {drink['name']} ({drink_cost} cr). Maybe sell something first.")
            else:
                ship["credits"] -= drink_cost
                print(f"\nYou buy a {drink['name']} for {drink_cost} credits.")
                print(random.choice(drink["fluff"]))

        elif choice == "2":
            pool_name = random.choice(list(advice_pools.keys()))
            advice = random.choice(advice_pools[pool_name])
            print(f"\n[Bartender — {pool_name.upper()}]: {advice}")

        elif choice == "3":
            print("\n" + "─" * 50)
            print(
                "You spend a month in the cantina. The days blur together.\n"
                "Traders come and go. Their stories of profit and loss echo around you.\n"
                "You wonder if life is just a constant train of orders and tasks.\n"
            )
            # Advance galaxy background story
            if galaxy_story_index < len(galaxy_story):
                print(f"[GALAXY NEWS]: {galaxy_story[galaxy_story_index]}")
                galaxy_story_index += 1
            else:
                print("[GALAXY NEWS]: The galaxy turns, quietly, as it always has.")
            print("─" * 50)
            input("\n[Press Enter to return to the cantina...]")

        elif choice == "9":
            break
        else:
            print("Invalid choice.")

    return galaxy_story_index


# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def init_planets():
    planets = {}
    for planet_name, planet_data in planets_template.items():
        new_prices = {}
        for spice, price in planet_data["base_prices"].items():
            if spice == planet_data["production"] or spice == planet_data["demand"]:
                new_prices[spice] = price
            else:
                new_prices[spice] = max(1, price + random.randint(-10, 10))
        planets[planet_name] = {**planet_data, "base_prices": new_prices}
    return planets


def new_ship():
    return {
        "credits": 1000,
        "cargo": {},
        "location": "Terra",
        "fuel": 500,
        "max_fuel": 500,
        "max_cargo": 100,
        "farm_bought": False,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    planets = init_planets()
    galaxy_story_index = 0

    print("═" * 55)
    print("  SPICE SPACE TRADER  v7")
    print("  Trade spices. Dodge pirates. Maybe buy a farm.")
    print("═" * 55)

    if os.path.exists(SAVE_FILE):
        ans = input("\nSave file found. Load it? [y/n]: ").strip().lower()
        if ans == "y":
            loaded_ship, galaxy_story_index = load_game(planets, galaxy_story_index)
            ship = loaded_ship if loaded_ship else new_ship()
        else:
            ship = new_ship()
    else:
        ship = new_ship()

    print("\nCommands: [1] Buy  [2] Sell  [3] Travel  [4] Status  [5] Prices  [6] Farm  [7] Cantina  [8] Save  [0] Quit")

    while True:
        show_status(ship)
        show_market(ship, planets)

        action = _get_int("\nChoose action: ", 0, 8)

        if action == 0:
            print(f"\nGame over. Final credits: {ship['credits']:,}")
            if ship["farm_bought"]:
                print("You retired to your cinnamon farm. You won. 🌿")
            break

        elif action == 1:
            buy_spice(ship, planets)

        elif action == 2:
            sell_spice(ship, planets)

        elif action == 3:
            travel(ship, planets)

        elif action == 4:
            show_status(ship)

        elif action == 5:
            price_check(planets)

        elif action == 6:
            if ship["location"] != "Terra":
                print("The farm is on Terra. Travel there first.")
            elif not ship["farm_bought"]:
                print(f"\nBuy a cinnamon farm on Terra for 10,000 credits?")
                print(f"Your credits: {ship['credits']:,}")
                if ship["credits"] >= 10000:
                    confirm = input("Confirm [y/n]: ").strip().lower()
                    if confirm == "y":
                        ship["credits"] -= 10000
                        ship["farm_bought"] = True
                        print("\n🌿 Congratulations! You now own a cinnamon farm on Terra.")
                else:
                    print(f"You need {10000 - ship['credits']:,} more credits.")
            else:
                visit_farm(ship, planets)

        elif action == 7:
            galaxy_story_index = visit_cantina(ship, planets, galaxy_story_index)

        elif action == 8:
            save_game(ship, planets, galaxy_story_index)


if __name__ == "__main__":
    main()
