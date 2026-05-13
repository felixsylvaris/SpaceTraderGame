# =============================================================
#  SPICE SPACE TRADER — library.py
#  All text content: cantinas, advice, passengers, news templates,
#  infobroker table functions (data pulled from parameters).
#  No game logic. No numbers except display formatting widths.
# =============================================================

import random
import parameters as P

# ── CANTINAS ─────────────────────────────────────────────────

cantinas = {
    "Terra": {
        "name": "The Cinnamon Tavern",
        "drink": {
            "name": "Cinnamon Beer", "ingredient": "Cinnamon",
            "fluff": [
                "The warm beer tastes like home.",
                "Sweet, spicy — exactly what you needed after a long day of haggling.",
                "The bartender winks. 'Made from Terra's finest. You won't find this anywhere else.'",
            ],
        },
    },
    "Zeta-9": {
        "name": "The Golden Saffron",
        "drink": {
            "name": "Saffron Mead", "ingredient": "Saffron",
            "fluff": [
                "Golden and rich. It tastes like liquid sunlight.",
                "The glass might actually be lined with real gold. Or maybe that's just the lighting.",
                "You feel fancy just holding it. The bartender smirks — you're clearly not from here.",
            ],
        },
    },
    "Void Colony": {
        "name": "The Pepper's Shadow",
        "drink": {
            "name": "Void Pepper Whiskey", "ingredient": "Void Pepper",
            "fluff": [
                "Burns like a supernova going down. You see stars. Literally.",
                "Rumoured to power small starships. You feel invincible. You are not.",
                "One sip: forget your name. Two sips: forget your debts.",
            ],
        },
    },
    "Agrica": {
        "name": "The Paprika Den",
        "drink": {
            "name": "Spiced Paprika Ale", "ingredient": "Paprika",
            "fluff": [
                "Fiery and bold, just like Agrica's farmers. You cough. Worth it.",
                "The bartender slides you a glass. 'Careful — house special. Last season's best.'",
                "You feel warmer immediately. Maybe it's the ale, maybe it's the hospitality.",
            ],
        },
    },
    "Nexus": {
        "name": "The Clove & Dagger",
        "drink": {
            "name": "Clove Rum", "ingredient": "Clove",
            "fluff": [
                "Smooth but packs a punch. Nexus traders swear by it to close deals.",
                "On the house — if you tell me where you got that Void Pepper.",
                "You sip it slowly. Complex, just like every deal made in this cantina.",
            ],
        },
    },
}

# ── ADVICE POOLS ─────────────────────────────────────────────

advice_pools = {
    "game": [
        "Buy low, sell high. Simple in theory. The galaxy complicates it.",
        "Weapons are expensive. Losing cargo to pirates costs more.",
        "Not all pirates are worth the fight. Running away is also valid.",
        "Nexus bankers are all high on Void Pepper. They'll pay anything for a fix.",
        "Bad trades from the past won't block good deals in the future.",
        "Upgrading your ship opens options you couldn't imagine before.",
        "The spread is real. You buy high and sell low. Trade volume is your friend.",
    ],
    "divorced": [
        "Never date a Psionic Girl. You'll be judged by your thoughts, not your words.",
        "Some opportunities happen once in a lifetime. If you see a Space Whale, feast your eyes.",
        "Don't drink a full cargo hold of Void Whiskey in one night. The hangover isn't worth it.",
        "There is no grand destiny. Only semi-random rolls of unseen dice. We make our own.",
    ],
    "iroh": [
        "Wide horizons reveal opportunities invisible on stable routes.",
        "Life happens whether you manage it or not. But you can make it cozy and peaceful.",
        "Bad trades happen. Let go of pride and shame. Trading in anger leads to bad deals.",
        "Leave spare cargo space. Always leave room for surprise opportunities.",
        "If you have a good ship and a few credits, you're already better off than many.",
    ],
    "festival": [
        "During the Cinnamon Roll Festival on Terra in Mari, prices spike hard. "
        "They bake a thirty-metre cinnamon roll and roll it down the main street. "
        "The cleanup takes the entire month of Aprix.",

        "Zeta-9's Golden Ginger Gala in Iuin: traders dress as giant ginger roots "
        "and race hovercarts through the market district. "
        "First prize is a full barrel of Saffron Mead.",

        "The Void Vanilla Vigil on Void Colony every Octo is technically a funeral. "
        "For the harvest. They bury a vanilla pod in a zero-G ceremony and everyone weeps. "
        "Vanilla prices go insane. The bartender always cries when telling this story.",

        "Agrica's Paprika Panic Parade in Aprix: they stuff a giant tentacle monster dummy "
        "full of paprikas and beat it with plasma hammers until it explodes. "
        "Children scramble for the spice shrapnel. Very traditional.",

        "Nexus hosts the Allspice Arbitrage Fête every Dedl. Brokers in formal wear "
        "outbid each other on rare allspice futures while drinking Clove Rum. "
        "Prices crash spectacularly the following month. Everyone pretends this is surprising.",
    ],
}

# ── GALAXY BACKGROUND STORY ──────────────────────────────────
# Revealed one entry per cantina rest, in order.

galaxy_story = [
    "A broker mentions in passing: the Senate voted to dissolve the Spice Trade Commission last cycle.",
    "A rogue freighter carrying 10,000 units of Void Pepper vanished near Nexus. No trace found.",
    "A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.",
    "AGRICA DROUGHT — paprika yields expected to halve next season.",
    "The old Void Colony governor was arrested. The new one is... friendlier to black-market dealings.",
    "The jump lanes near Terra are being taxed now. Change is coming, friend.",
    "The galaxy feels different lately. The old trade routes are shifting. Nobody knows where it leads.",
]

# ── PASSENGERS ───────────────────────────────────────────────
# Add more entries to this list to add new passenger types.
# Fields: shortname, fullname, cantina_text, exit_text

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

# ── FARM FLUFF ───────────────────────────────────────────────
# Shown when visiting the Cinnamon Farm on Terra.

FARM_FLUFF = [
    "You sit on the porch of your cinnamon farm, sipping a warm drink. "
    "The sunset paints the orchard in gold, and the scent of spices fills the air.",
    "The cinnamon trees rustle in the breeze. A neighbor waves from across the field. "
    "'Harvest was good this year,' they say.",
    "The scent of cinnamon fills the air. You made it. No more fuel calculations, "
    "no more pirate attacks. Just peace.",
]

# ── NEWS FEED TEMPLATES ───────────────────────────────────────
# Placeholders: {shortname}, {destination}, {festival_name},
#               {planet}, {month_name}, {harvest_good}

NEWS_TRAVELER  = "  📋 Traveler waiting in the Promenade Cantina: {shortname} → {destination}"
NEWS_FESTIVAL  = "  🎊 Join the {festival_name} on {planet} this {month_name}! Let the fun begin!"
NEWS_HARVEST   = "  🌾 {harvest_good} harvest in full swing this {month_name}. Fill your hold while yields last."
NEWS_MARKET    = "  🛒 Hot Deals: {deals}. Visit Local Market at Promenade. Come fast, don't be last."

# ── CONCERT HALL ─────────────────────────────────────────────

CONCERT_NO_SHOW = (
    "The stage is empty.\n"
    "A stagehand appears and clears their throat:\n"
    "  \"The artist was stopped on the Hyperlanes by pirates.\n"
    "   We all pray for their swift recovery and near comeback.\"\n"
    "Your ticket has been refunded."
)

# ── INFOBROKER TABLES ─────────────────────────────────────────
# Data is pulled from parameters — no hardcoded duplication.

def _col(text, width):
    return str(text).ljust(width)

def _table(header_cols, rows, widths):
    """Print a simple ASCII table. header_cols and each row are tuples."""
    sep = "  +" + "+".join("-" * w for w in widths) + "+"
    def fmt_row(cells):
        return "  |" + "|".join(_col(c, w) for c, w in zip(cells, widths)) + "|"
    print(sep)
    print(fmt_row(header_cols))
    print(sep)
    for row in rows:
        print(fmt_row(row))
    print(sep)

def infobroker_goods_table():
    """Goods Directory: which planets carry each good, production/demand roles."""
    # Build planet lists dynamically from parameters
    good_planets  = {good: [] for good in P.GOOD_DATA}
    good_prod     = {}
    good_demand   = {}
    for planet_name, pdata in P.planets_template.items():
        for good in pdata["spices"]:
            if good in good_planets:
                good_planets[good].append(planet_name)
        good_prod[pdata["production"]]  = planet_name
        good_demand[pdata["demand"]]    = planet_name

    rows = []
    for good in sorted(good_planets.keys()):
        if good == "Mystery Crate": continue
        planets_str = ", ".join(good_planets[good])
        prod   = good_prod.get(good, "—")
        demand = good_demand.get(good, "—")
        rows.append((good, planets_str, prod, demand))

    print("\n── INFOBROKER: GOODS DIRECTORY ─────────────────────")
    _table(
        ("Good", "Planets", "Production", "Demand"),
        rows,
        [14, 32, 14, 14],
    )

def infobroker_harvest_table():
    """Harvest Seasons: which month each good is harvested and its pattern."""
    pattern_labels = {"low": "Low (+20 peak)", "mid": "Mid (−20 harvest, +20 peak)", "high": "High (−20 harvest, +50 peak)"}
    rows = []
    for good, entry in P.GOOD_SEASONS.items():
        if good == "Mystery Crate": continue
        if entry is None:
            rows.append((good, "—", "—", "None — no harvest cycle"))
        else:
            harvest_idx, pattern_key = entry
            mo_num  = harvest_idx + 1
            mo_name = P.MONTH_NAMES[harvest_idx]
            rows.append((good, str(mo_num), mo_name, pattern_labels[pattern_key]))

    print("\n── INFOBROKER: HARVEST SEASONS ─────────────────────")
    _table(
        ("Good", "Mo#", "Month", "Season Pattern"),
        rows,
        [14, 4, 7, 28],
    )

def infobroker_festival_table():
    """Festival Calendar: planet, month, festival name, featured good."""
    rows = []
    for planet_name in P.PLANET_NAMES:
        if planet_name not in P.PLANET_FESTIVALS: continue
        good, fest_month_idx, fest_name, boost_type = P.PLANET_FESTIVALS[planet_name]
        mo_num  = fest_month_idx + 1
        mo_name = P.MONTH_NAMES[fest_month_idx]
        boost   = P.FESTIVAL_BOOST[boost_type]
        rows.append((planet_name, str(mo_num), mo_name, fest_name, good, f"+{boost}cr"))

    print("\n── INFOBROKER: FESTIVAL CALENDAR ───────────────────")
    _table(
        ("Planet", "Mo#", "Month", "Festival", "Good", "Boost"),
        rows,
        [13, 4, 7, 26, 12, 7],
    )
    print("  Prices spike in festival month. Drop by same amount the month after.")

def random_advice():
    """Return a (pool_name, advice_string) tuple."""
    pool = random.choice(list(advice_pools.keys()))
    return pool, random.choice(advice_pools[pool])

def random_galaxy_news(index):
    """Return next galaxy story entry, or None if exhausted."""
    if index < len(galaxy_story):
        return galaxy_story[index]
    return None
