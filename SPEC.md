# Spice Space Trader — SPEC
## Full System Reference

*Written for the developer returning after a long break. Covers every system, every number, every menu. If you need to find yourself in the code, start here.*

---

## File Map

| File | Role |
|------|------|
| `game.py` | All logic. Functions, menus, game loop. Edit for new features. |
| `parameters.py` | All numbers. No functions. Edit for balance tuning. |
| `library.py` | All text content. Cantinas, advice pools, event lists, passengers, infobroker table renderers. |
| `songs.py` | `SONGS` list of dicts. Loaded directly at import. No file I/O. |
| `spice_trader_save.json` | Runtime save file. JSON. Auto-created by `save_game()`. |

---

## Calendar

10-month year starting in 2201. Month index is 0-based internally.

| Index | Name | Index | Name |
|-------|------|-------|------|
| 0 | Ianu | 5 | Iuin |
| 1 | Febu | 6 | Septr |
| 2 | Mari | 7 | Octo |
| 3 | Aprix | 8 | Nova |
| 4 | Maiu | 9 | Dedl |

**Time advances 1 month when:**
- Player successfully travels to another planet
- Player rests in the cantina (`[4]`)
- Player mines for one month (each mining operation = 1 month)

`advance_time(state)` runs the full monthly simulation pipeline in this order:
1. `_run_consumption` — deplete stockpiles
2. `_run_production` — spice harvest (harvest month only)
3. `_run_industrial_production` — industrial output (every month)
4. `_apply_stockpile_pressure` — price nudge based on stock levels
5. `_apply_inflation` — random price drift
6. `_check_festival_drop` — post-festival price hangover
7. `_spawn_asteroid_fields` — resets fields on month 0 each year
8. `_run_independent_trader` — background NPC arbitrage

---

## Planets

Five planets ordered by index. Travel fuel cost scales with index distance.

`PLANET_NAMES = ["Terra", "Zeta-9", "Void Colony", "Agrica", "Nexus"]`

Each planet in `planets_template` has:
- `production` — spice produced here cheaply (◀ SPICE marker)
- `demand` — spice demanded here at a premium (▶ DEMAND marker)
- `ind_production` — list of industrial goods produced here (◀ INDUSTRY marker)
- `goods` — full list of all goods available on this planet
- `base_prices` — starting base prices (randomised at new game start)

### Planet goods and roles

| Planet | Spice Production | Spice Demand | Industrial Production | Goods Available |
|--------|-----------------|--------------|----------------------|-----------------|
| Terra | Cinnamon | Allspice | Weapons, Robots | Cinnamon, Cardamom, Vanilla, Allspice, Clove, Paprika, Ginger, Alloys, Weapons, Robots, Medicine |
| Zeta-9 | Saffron | Ginger | Alloys | Saffron, Turmeric, Paprika, Ginger, Nutmeg, Cinnamon, Minerals, Alloys, Robots, Soybeans |
| Void Colony | Void Pepper | Cardamom | Minerals | Void Pepper, Saffron, Ginger, Cardamom, Clove, Vanilla, Minerals, Weapons, Medicine, Robots |
| Agrica | Paprika | Vanilla | Soybeans | Paprika, Cinnamon, Turmeric, Vanilla, Allspice, Cardamom, Nutmeg, Soybeans, Weapons, Robots |
| Nexus | Clove | Turmeric | Medicine | Clove, Void Pepper, Nutmeg, Saffron, Turmeric, Allspice, Alloys, Soybeans, Medicine |

---

## Goods & Prices

### Price categories

Every good has a category that controls spread, stockpile size, production/consumption rates, and seasonal pattern intensity.

| Category | Spread | Stockpile Max | Spice Production/mo | Spice Consumption/mo |
|----------|--------|---------------|--------------------|--------------------|
| low | ±5 | 500 | 64 (192 home) | 7 (14 demand) |
| mid | ±10 | 300 | 32 (96 home) | 4 (8 demand) |
| high | ±15 | 100 | 16 (48 home) | 2 (4 demand) |

**Buy price** = `effective_mean + spread`
**Sell price** = `effective_mean − spread`
**Effective mean** = `base_price + season_offset + festival_boost` (clamped to [min−spread, max+spread])

### All goods reference table

| Good | Category | Min | Mean | Max | Harvest Month | Notes |
|------|----------|-----|------|-----|---------------|-------|
| Cinnamon | low | 15 | 50 | 150 | Ianu (0) | |
| Turmeric | low | 18 | 60 | 180 | Febu (1) | |
| Paprika | low | 21 | 70 | 210 | Mari (2) | |
| Ginger | mid | 24 | 80 | 240 | Aprix (3) | |
| Clove | mid | 27 | 90 | 270 | Maiu (4) | |
| Vanilla | mid | 30 | 100 | 300 | Iuin (5) | |
| Cardamom | mid | 33 | 110 | 330 | Septr (6) | |
| Allspice | high | 36 | 120 | 360 | Octo (7) | |
| Saffron | high | 45 | 150 | 450 | Nova (8) | |
| Nutmeg | high | 42 | 140 | 420 | Dedl (9) | |
| Void Pepper | high | 150 | 500 | 1500 | — | Annual production Dedl, consumed monthly |
| Mystery Crate | low | 1 | 10 | 500 | — | Travel event only, wide price range |
| Minerals | low | 24 | 80 | 240 | — | Industrial, Void Colony produces |
| Soybeans | low | 18 | 60 | 180 | — | Industrial, Agrica produces |
| Alloys | mid | 36 | 120 | 360 | — | Industrial, Zeta-9 produces |
| Robots | mid | 48 | 160 | 480 | — | Industrial, Terra produces |
| Weapons | high | 60 | 200 | 600 | — | Industrial, Terra produces |
| Medicine | high | 90 | 300 | 900 | — | Industrial, Nexus produces |

### Price drift (inflation)

Every month, every good on every planet: 50% chance +1 to +10, 50% chance −1 to −9. Always clamped to `[min, max]` from GOOD_DATA.

### Harvest seasons

Spices have a harvest month (low price) and a peak month ~5 months later (high price). Seasonal offset applied to base_price when calculating effective_mean.

| Pattern | +0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 |
|---------|----|----|----|----|----|----|----|----|----|----|
| low | 0 | 0 | +5 | +5 | +10 | +10 | +15 | +15 | +20 | +10 |
| mid | −20 | −15 | −5 | 0 | +5 | +10 | +20 | +15 | +10 | 0 |
| high | −20 | −10 | 0 | +10 | +20 | +30 | +40 | +50 | +30 | +20 |

Index 0 = harvest month. So a mid-category good is cheapest at harvest and peaks 6 months later at +20.

---

## Stockpiles

Every planet/good pair has a stockpile. Max size by category: low=500, mid=300, high=100.

**Player buying** reduces local stockpile. Player cannot buy more than stock available.
**Player selling** increases local stockpile. Player cannot sell beyond max capacity.

### Stockpile pressure on prices

Applied every month after production and consumption:
- If stockpile < 20% of max → base_price +5/10/20 (by category)
- If stockpile > 80% of max → base_price −5/10/20 (by category)

### Starting stockpiles

New game only — randomised then averaged with parameter defaults:
`stockpile = (random(25%max, 75%max) + STOCKPILE_START[category]) / 2`

Default starting values (half of max): low=250, mid=150, high=50. Override specific planet/good pairs via `STOCKPILE_OVERRIDES` dict in `parameters.py`.

---

## Production

### Spice production (seasonal)

Fires once per year on each good's harvest month. Only on planets that carry the good.

- Base amount by category: low=64, mid=32, high=16
- Production planet multiplier: ×3
- If stockpile was literally 0 at time of production: ×1.5 (generous harvest)

### Void Pepper production (special)

Fires annually on month 9 (Dedl), Void Colony only. Fixed +30 units. ×1.5 if stockpile at 0.

### Void Pepper consumption (special)

Monthly, fixed per planet: Void Colony −2, Nexus −4.

### Spice consumption (monthly)

Every planet that carries a good consumes it monthly:
- Base rate by category: low=7, mid=4, high=2
- Demand planet: ×2
- Stockpile ≥ 80%: ×2 (stacks with demand — max ×4)
- Stockpile < 20%: ÷2 (floor 1) — scarcity slows consumption

### Industrial production (monthly)

Fires every month. Single production planet per good. No home multiplier.

| Good | Production Planet | Monthly Output |
|------|------------------|----------------|
| Minerals | Void Colony | +8 |
| Soybeans | Agrica | +8 |
| Alloys | Zeta-9 | +4 |
| Robots | Terra | +4 |
| Weapons | Terra | +2 |
| Medicine | Nexus | +2 |

**Cross-good bonus rules** — checked monthly, multiplicative stacking:

| Trigger Planet | Trigger Good | Threshold | Target Planet | Target Good | Multiplier |
|---------------|--------------|-----------|---------------|-------------|------------|
| Void Colony | Minerals | ≥50% full | Zeta-9 | Alloys | ×2 |
| Zeta-9 | Alloys | ≥50% full | Terra | Weapons | ×2 |
| Terra | Weapons | ≥50% full | Agrica | Soybeans | ×2 |
| Terra | Robots | ≥50% full | Agrica | Soybeans | ×2 |
| Terra | Robots | ≥50% full | Void Colony | Minerals | ×2 |
| Terra | Robots | ≥50% full | Zeta-9 | Alloys | ×2 |

### Industrial consumption (monthly)

Per good, every planet that carries it:

| Good | Monthly Consumption |
|------|-------------------|
| Minerals | 4 |
| Soybeans | 4 |
| Alloys | 2 |
| Robots | 2 |
| Weapons | 2 |
| Medicine | 2 |

Same scarcity/abundance multipliers as spices: <20% stock → ÷2 (floor 1), >80% stock → ×2.

---

## Festivals

One festival per planet per year. In the festival month the featured good gets a base_price spike. The following month the base_price drops by the same amount (hangover). Stacks on top of seasonal offsets.

| Planet | Month | Festival Name | Good | Boost |
|--------|-------|---------------|------|-------|
| Terra | Mari (2) | Cinnamon Roll Festival | Cinnamon | +25 |
| Agrica | Aprix (3) | Paprika Panic Parade | Paprika | +25 |
| Zeta-9 | Iuin (5) | Golden Ginger Gala | Ginger | +35 |
| Void Colony | Octo (7) | Void Vanilla Vigil | Vanilla | +35 |
| Nexus | Dedl (9) | Allspice Arbitrage Fête | Allspice | +50 |

---

## Travel

**Fuel cost** = `abs(planet_index_diff) × 12 ± random(−5, +5)`, clamped to [10, 50].
**Minimum fuel to depart** = 50. Cannot travel or drain below this.
**Fuel price** = 1 cr/unit. Buy/sell in Engineering Bay.

### Non-pirate travel events

Rolled after each jump. Only one fires per jump.

| Chance | Event |
|--------|-------|
| 12% | Spice Festival at destination — all prices ×1.1 |
| 10% | Fuel Leak — lose 15–35 fuel |
| 8% | Mystery Cargo — gain 5× Mystery Crate if cargo space available |

---

## Pirates

**Base encounter chance** = 25% per jump. 10% with Long Range Radar.

`piratangst` starts at 10 and increases with each encounter and fight. Affects pirate power and flee fuel cost. Persists across sessions via save.

**Pirate power** = `max(1, angst // 20)` — becomes a real threat after ~20+ angst.

| Option | Effect |
|--------|--------|
| Fight | Compare weapons vs pirate power. Win → bounty (100 × angst cr) +5 angst. Lose → drop half cargo +2 angst. Tie → standoff. |
| Flee | Costs `20 × angst` fuel (5× with Booster). Must keep ≥50 fuel reserve. |
| Bribe | Pay `piratbribe` credits (starts 100, +100 each use, saved). −3 angst on success. |
| Drop Cargo | Lose half of each cargo type rounded up. −2 angst. If cargo empty, lose up to 200 cr. |
| Bluff | Auto-pass if total cargo ≤10. Otherwise 50/50. Fail = +2 angst, option locked. |
| Surrender | GAME OVER (with confirmation). |

---

## Ship Upgrades

Bought once. Planet-exclusive upgrades only available at that planet. All persist to save.

| Upgrade | Cost | Planet | Effect |
|---------|------|--------|--------|
| Kinetic Launcher | 2,000 | Any | Weapons +1 |
| Mining Laser | 1,000 | Zeta-9 | Weapons +1. Required for asteroid mining. |
| Void Torpedo | 5,000 | Void Colony | Weapons +2. Illegal elsewhere. |
| Stern Tank | 1,000 | Any | Max fuel +200 |
| Portside Tank | 2,000 | Any | Max fuel +300 |
| Cylindrical Tank | 3,000 | Any | Max fuel +500 |
| Small Hold | 1,000 | Any | Max cargo +100 |
| Side Hold | 2,000 | Terra | Max cargo +100 |
| Grain Silo | 3,000 | Agrica | Max cargo +200 |
| Galactic Broker License | 1,000 | Nexus | Unlocks Price Check `[5]` |
| Passenger Quoters | 1,000 | Any | Unlocks passenger slot |
| Long Range Radar | 3,000 | Terra | Pirate chance 25% → 10% |
| Booster | 1,000 | Void Colony | Flee fuel cost ×0.25 (5× instead of 20×) |
| Mining Drones | 10,000 | Zeta-9 | Mine entire asteroid field in 1 month |

Max weapons achievable = 4 (Kinetic +1, Mining Laser +1, Void Torpedo +2).

---

## Tax

2% of gross sale value, minimum 1 cr, rounded up. Applied to all sales including Fleet Supply Depot. Formula: `tax = max(1, ceil(gross × 0.02))`.

---

## Promenade

Accessed via `[6]` from the spaceport. Planet-side services.

### Cantina

Every planet has a unique cantina. Options:
- `[1]` **Drink** — costs 50% of the ingredient's current sell price. Flavour text only.
- `[2]` **Advice** — random line from advice pools (game tips / divorced uncle / Uncle Iroh / festival lore).
- `[3]` **Traveler** — only visible with Passenger Quoters installed. Accept or decline current waiting passenger.
- `[4]` **Rest** — advance 1 month, fire a random event, possibly spawn a passenger.

| Planet | Cantina | Drink | Ingredient |
|--------|---------|-------|------------|
| Terra | The Cinnamon Tavern | Cinnamon Beer | Cinnamon |
| Zeta-9 | The Golden Saffron | Saffron Mead | Saffron |
| Void Colony | The Pepper's Shadow | Void Pepper Whiskey | Void Pepper |
| Agrica | The Paprika Den | Spiced Paprika Ale | Paprika |
| Nexus | The Clove & Dagger | Clove Rum | Clove |

### Infobroker

Free reference tables:
- `[1]` Goods Directory — which planets carry each good, production/demand roles
- `[2]` Harvest Seasons — harvest month and price pattern for each spice
- `[3]` Festival Calendar — planet, month, festival name, featured good, boost amount

### Concert Hall

Costs 10 cr. Picks a random song from `SONGS` list in `songs.py` and prints title, lyrics, optional ASCII art. If `SONGS` is empty, refunds ticket and shows "artist stopped by pirates" message.

To add songs: append a dict to `SONGS` in `songs.py` with keys `shortname`, `fullname`, `text`, and optionally `art`.

### Local Market

5 random goods rolled fresh on each planet arrival. Independent traders selling from outside the local stockpile system — quantities are small, prices slightly above sell price, one purchase collapses the slot.

| Category | Quantity | Price variance |
|----------|----------|---------------|
| low | ×20 | ±5 |
| mid | ×10 | ±10 |
| high | ×5 | ±15 |

Once bought, that trader slot disappears ("pockets credits and vanishes"). Slots don't restock during the same visit.

### Cinnamon Farm (Terra only)

Key `[f]` on Terra Promenade. Purchase for 10,000 cr. Flavour-only. Considered the soft win condition. Game continues after purchase.

### Fleet Supply Depot (Terra only)

Key `[s]` on Terra Promenade. Sell-only. Fixed prices. No stockpile — goods sold here vanish from the game. Intended as a floor dump valve when the galaxy is flooded.

| Good | Depot Price | Notes |
|------|------------|-------|
| Cinnamon | 21 | Produced on Terra |
| Turmeric | 28 | |
| Paprika | 31 | |
| Ginger | 39 | |
| Clove | 42 | |
| Vanilla | 45 | |
| Cardamom | 48 | |
| Allspice | 56 | |
| Saffron | 65 | |
| Nutmeg | 62 | |
| Void Pepper | 170 | |
| Minerals | 34 | |
| Soybeans | 28 | |
| Alloys | 51 | |
| Medicine | 110 | |
| Weapons | 76 | Produced on Terra (+1 margin) |
| Robots | 59 | Produced on Terra (+1 margin) |

Price formula: `min_price + spread + 5` for most goods. `min_price + spread + 1` for Weapons and Robots (manufactured next door on Terra).

---

## Passengers

Requires Passenger Quoters upgrade. One slot. 20% spawn chance per planet arrival or cantina rest.

Waiting passenger shown in Cantina under `[3]` and in the news feed. Accept to board. Deliver to their destination for +300 cr. Taking a new passenger replaces the current one (old passenger stays at current planet).

Passenger roster lives in `library.py` as `PASSENGER_ROSTER`. Add more dicts with keys: `shortname`, `fullname`, `cantina_text`, `exit_text`.

Current passengers: Whitemaine (Pride Mercenary, hates hyperlines).

---

## Asteroid Mining

Available at Zeta-9 and Void Colony via `[a]` from the spaceport.

**Requires Mining Laser** upgrade. Without it, flavour message about staring at rocks.

Fields spawn on month 0 (Ianu) each year with a random size of 10–100 units. Reset every year regardless of how much was mined — unclaimed ore disappears.

### Mining menu

- `[1]` Mine a little — 1 month passes, extract `min(10, field, cargo_free)` Minerals
- `[2]` Mine for several months — choose number of months, each extracts 10 Minerals
- `[3]` Mine it all — loops until field empty or cargo full, 1 month per 10 Minerals

Each month of mining prints a random flavour thought from `MINING_THOUGHTS` in `library.py`.

**Mining Drones upgrade** (10,000 cr, Zeta-9 only): Mine it all option completes in 1 month regardless of field size.

Market screen shows current field remaining when at a mining planet.

---

## Random Events

Fire on two triggers: planet arrival (after travel) and cantina rest. Both represent 1 month passing.

**20% chance** → Impact event (real game effect)
**80% chance** → Blank event (flavour only)

Impact events modify stockpiles and base_prices on specific planets with safety clamps (stockpile stays in [0, max], price stays in [min, max]). Defined as a list of `(planet, good, stockpile_delta, price_delta)` tuples.

Blank events are random strings from `event_rnd_blank` in `library.py`. Add freely.
Impact events are dicts in `event_rnd_impact` in `library.py` with keys `tag`, `text`, `effects`.

Display: impact events use 🌐 prefix. Blank events use 📰 prefix.

### Current impact events

| Tag | Headline | Effect |
|-----|----------|--------|
| evri001 | Agrica drought | Agrica Paprika stk −200, price +20 |
| evri002 | Pirates raid Void Colony | VC Void Pepper stk −50 price +100, Clove stk −100 price +50 |
| evri003 | Smugglers caught on Nexus | Nexus Void Pepper stk +50, price −100 |
| evri004 | Zeta-9 Saffron bumper crop | Zeta-9 Saffron stk +50, price −50 |
| evri005 | Terra cinnamon orchard wildfire | Terra Cinnamon stk −200, price +30 |
| evri006 | Agrica cinnamon berry substitute | Agrica Cinnamon stk +200, price −30 |
| evri007 | Nexus pop star saffron claim | Nexus Saffron stk −50, price +50 |
| evri008 | Zeta-9 turmeric importer bankrupt | Zeta-9 Turmeric stk −200, price +30 |

---

## Independent Trader (background NPC)

Fires at end of each month cycle (last step in `advance_time`).

- 30% chance to activate at all (`IND_TR_CHANCE`)
- Generates all 10 unique planet pairs from 5 planets
- Each pair: 30% chance to skip (`IND_TR_SKIP_CHANCE`)
- For each evaluated pair: find the good present on both planets with the highest base_price difference
- Move stock from low-price to high-price planet: `min(volume, available_stock, room_at_dest)` units
- Nudge prices: source +5, destination −5 (clamped to good's [min, max])

Volume by category: low=40, mid=20, high=10.

Cannot negative a stockpile. Cannot overfill a destination. Operates on base_prices directly, not effective_mean — ignores spread and season.

---

## News Feed

Prints once per planet visit (resets on departure). Shows:
- Waiting passenger (if Passenger Quoters installed and someone is waiting)
- Festival notice (if current planet is celebrating this month)
- Harvest notice (whichever good is being harvested this month)
- Local Market hot deals (active slots, prices, quantities)

---

## Save System

Saves to `spice_trader_save.json`. Persists: full ship state, all planet base_prices, stockpiles, local market slots, asteroid field sizes, calendar, piratangst, piratbribe, galaxy story index, waiting passenger, festival drop history.

On load: planet structure comes from `planets_template` in parameters (carries goods lists, ind_production etc.), then base_prices are overwritten from the save file. Industrial goods appear correctly on load even if the save predates them — missing stockpile entries default to 0.

Prompted on startup if save file exists. Prompted again on quit. Cheat: delete `spice_trader_save.json` to reset.

---

## Galaxy Story System

`galaxy_story` list and `random_galaxy_news()` function exist in `library.py` and `galaxy_story_index` is tracked in state and save file. Currently **not triggered** — reserved for future scripted narrative system. The random event system (blank/impact) runs instead. When galaxy story gets built, it will take priority over random events when a story entry exists for the current turn.

---

## Starting a New Game

Prices and stockpiles are randomised once on new game (not on load):

- **Price**: `(random(min_price, 2×default_price) + parameter_default) / 2`, clamped to `[30%×default, 300%×default]` and always within `[min, max]`
- **Stockpile**: `(random(25%×max, 75%×max) + STOCKPILE_START[category]) / 2`, clamped to `[0, max]`

This creates varied starting conditions while keeping the parameter table as a meaningful anchor.

---

## Adding Content — Quick Reference

| What | Where |
|------|-------|
| New song | Add dict to `SONGS` in `songs.py` |
| New blank event | Append string to `event_rnd_blank` in `library.py` |
| New impact event | Append dict to `event_rnd_impact` in `library.py` |
| New passenger | Append dict to `PASSENGER_ROSTER` in `library.py` |
| New mining thought | Append string to `MINING_THOUGHTS` in `library.py` |
| New advice line | Append to appropriate pool in `advice_pools` in `library.py` |
| New upgrade | Add to `UPGRADES_DATA` in `parameters.py`, add effect lambda to `UPGRADE_EFFECTS` in `game.py`, add field to `SHIP_START` in `parameters.py` |
| New good | Add to `GOOD_DATA`, `GOOD_SEASONS`, each planet's `goods` and `base_prices` in `parameters.py`; add to `INDUSTRIAL_PRODUCTION`/`INDUSTRIAL_CONSUMPTION` if industrial |
| New planet | Add to `PLANET_NAMES` and `planets_template` in `parameters.py`; add cantina entry to `library.py` |
| Tune balance | Edit values in `parameters.py` — no logic changes needed |

## Recent Changes
Added Blackjack in Cantina. 
---
