# 🌌 Spice Space Trader

A text-based interstellar trading game written in Python. Buy spices cheap, sell them dear, dodge pirates, mine asteroids, and maybe retire to a cinnamon farm.

Runs entirely in the terminal. No dependencies required.

---

## What is this

You are an independent trader with a ship, 1000 credits, and a full tank of fuel. The galaxy has five planets — each producing one spice cheaply and demanding another at a premium. You fly between them, exploit price differences, upgrade your ship, and accumulate credits. The economy is alive: prices drift, stockpiles deplete, harvests happen, festivals spike demand, independent traders arbitrage while you sleep, and random events occasionally blow up someone's paprika crop.

There is no hard win condition. The soft goal is 10,000 credits to buy a cinnamon farm on Terra and retire. Most players keep going after that.

---

## How to run

```bash
python game.py
```

Python 3.x. No required dependencies. The `requests` library is optional — used only for remote RNG seeding on travel. Falls back to local random if absent.

---

## Files

| File | Purpose |
|------|---------|
| `game.py` | All game logic. Main loop, systems, menus. |
| `parameters.py` | All numbers and balance data. No logic. Edit this to tune the game. |
| `library.py` | All text content. Cantina flavour, advice, events, passengers, infobroker tables. |
| `songs.py` | Songs for the in-game concert hall. Add entries to `SONGS` list. |
| `spice_trader_save.json` | Save file. Auto-created on save. Delete to reset. |

---

## Controls

```
[1] Buy    [2] Sell    [3] Travel
[4] Status [5] Price Check (requires Broker License)
[6] Promenade
[8] Engineering Bay
[9] Save
[a] Asteroid Field (Zeta-9 and Void Colony only)
[q] Quit
[0] Back / Cancel (in all submenus)
```

Cheat code: type `!credits 5000` at the main prompt to add credits.

---

## The five planets

| Planet | Produces | Demands | Notes |
|--------|----------|---------|-------|
| Terra | Cinnamon | Allspice | Fleet HQ, Fleet Supply Depot, cinnamon farm |
| Zeta-9 | Saffron | Ginger | Shipyards, asteroid field, Mining Laser available |
| Void Colony | Void Pepper | Cardamom | Edge of the map, asteroid field, Booster upgrade |
| Agrica | Paprika | Vanilla | Jungle world, Grain Silo available |
| Nexus | Clove | Turmeric | Space station, Broker License, everyone is high |

---

## The economy in brief

Prices drift every month within hard bounds. Buy price = mean + spread. Sell price = mean − spread. Harvests flood supply annually, pushing prices down at harvest month and up toward the peak five months later. Festivals spike one good per planet per year. Stockpiles deplete from consumption and refill from production — scarcity raises prices, oversupply drops them. Independent traders arbitrage between planets in the background. Random events occasionally hit stockpiles and prices hard.

Industrial goods (Minerals, Alloys, Weapons, Soybeans, Medicine, Robots) are produced monthly rather than seasonally, and form a loose supply chain — well-stocked Minerals boost Alloy production, Alloys boost Weapons, and so on.

---

## Brainstorm / future features

See `brainstorm.md` for the parking lot. Current candidates: farmland investment, blackjack in cantina, rare one-time travel encounters, galaxy story timeline, expedition minigame on Agrica.

---

## Lore

See `LOREPEDIA.md` for in-universe planet descriptions, faction notes, and background.
