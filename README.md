# 🌌 Spice Space Trader — Game Specification v9

*A text-based interstellar trading game. Buy spices cheap, sell them dear, dodge pirates, and maybe retire to a cinnamon farm.*

**Current version: v9** | Python 3.x | Dependencies: none (requests optional for remote RNG)
**Run:** `python spice_trader_v9.py`
**Save file:** `spice_trader_save.json` (auto-created on save)
**Songs file:** `songs.json` (auto-created on first run)

---

## 📋 Navigation Overview

The game has two layers of menus: the **Spaceport** and the **Promenade**.

### Spaceport (main loop)
```
[1] Buy       [2] Sell      [3] Travel
[4] Status    [5] Price Check (requires Broker License)
[6] Promenade [8] Engineering Bay
[9] Save      [0] Quit
```

### Promenade (planet services)
```
[1] Cantina   [2] Infobroker   [3] Concert Hall [10cr]
[f] Farm (Terra only)          [0] Back to Spaceport
```

A **news feed** prints once per planet visit and resets when you depart. It shows:
- Active traveler waiting in the cantina (only if Passenger Quoters installed)
- Festival notice if this planet is celebrating this month
- Which good is currently being harvested galaxy-wide

---

## 📅 Calendar

The galaxy runs on a **10-month year** starting in 2201.

| # | Name  | # | Name  |
|---|-------|---|-------|
| 1 | Ianu  | 6 | Iuin  |
| 2 | Febu  | 7 | Septr |
| 3 | Mari  | 8 | Octo  |
| 4 | Aprix | 9 | Nova  |
| 5 | Maiu  | 10| Dedl  |

**Turn** is an internal counter incrementing every month. Invisible to the player, reserved for future use.

**Time advances by 1 month when:**
- You successfully travel to another planet
- You rest in the cantina ("Rest for a while" option)

---

## 🌍 Planets

Five planets, ordered by index (affects travel fuel cost — farther apart = more fuel).

| Planet      | Production    | Demand    | Neutral Goods                              |
|-------------|---------------|-----------|---------------------------------------------|
| Terra       | Cinnamon (25) | Allspice  | Cardamom, Vanilla, Clove, Paprika, Ginger  |
| Zeta-9      | Saffron (100) | Ginger    | Turmeric, Paprika, Nutmeg, Cinnamon        |
| Void Colony | Void Pepper (500) | Cardamom | Saffron, Ginger, Clove, Vanilla        |
| Agrica      | Paprika (30)  | Vanilla   | Cinnamon, Turmeric, Allspice, Cardamom, Nutmeg |
| Nexus       | Clove (35)    | Turmeric  | Void Pepper, Nutmeg, Saffron, Allspice     |

**Production price** = local cheap price shown in parentheses. Fixed, never drifts.
**Demand price** = high fixed local buy price. Fixed, never drifts.
**Neutral goods** drift each turn within their global price bounds.

Each good exists on **exactly 3 planets** (except Void Pepper which is on 2 — intentional, see economy notes).

---

## 📦 Goods & Price System

### Price Categories and Bounds

Every good has a category (Low / Mid / High) that controls its price bounds, seasonal pattern, and spread. The **mean price** drifts each turn within [min, max]. Production and Demand prices on their home planet are frozen.

| Good        | Category | Spread | Min | Mean | Max  |
|-------------|----------|--------|-----|------|------|
| Cinnamon    | Low      | ±5     | 15  | 50   | 150  |
| Turmeric    | Low      | ±5     | 18  | 60   | 180  |
| Paprika     | Low      | ±5     | 21  | 70   | 210  |
| Ginger      | Mid      | ±10    | 24  | 80   | 240  |
| Clove       | Mid      | ±10    | 27  | 90   | 270  |
| Vanilla     | Mid      | ±10    | 30  | 100  | 300  |
| Cardamom    | Mid      | ±10    | 33  | 110  | 330  |
| Allspice    | High     | ±15    | 36  | 120  | 360  |
| Saffron     | High     | ±15    | 45  | 150  | 450  |
| Nutmeg      | High     | ±15    | 42  | 140  | 420  |
| Void Pepper | High     | ±15    | 150 | 500  | 1500 |
| Mystery Crate | Low    | ±5     | 1   | 10   | 500  |

### Buy Price / Sell Price

The market shows two columns: **Sell** (what you get) and **Buy** (what you pay). They are derived from the mean price:

- **Sell price** = mean − spread
- **Buy price** = mean + spread

Example: Cinnamon mean=50, spread=5 → you sell for 45, buy for 55. The traders haggle. Trade volume is your friend.

### Price Drift (Inflation)

Each turn, every neutral good on every planet drifts: 50% chance +1 to +10, 50% chance −1 to −9. Always clamped to the good's [min, max]. Production and Demand goods are immune.

---

## 🌾 Harvest Seasons

Each good has a harvest month. In the harvest month, mean price is lower; five months later is the anti-harvest peak, where prices are highest. Pattern is applied as an offset to the mean price.

| Good      | Harvest Month | Pattern |
|-----------|--------------|---------|
| Cinnamon  | 1 – Ianu     | Low     |
| Turmeric  | 2 – Febu     | Low     |
| Paprika   | 3 – Mari     | Low     |
| Ginger    | 4 – Aprix    | Mid     |
| Clove     | 5 – Maiu     | Mid     |
| Vanilla   | 6 – Iuin     | Mid     |
| Cardamom  | 7 – Septr    | Mid     |
| Allspice  | 8 – Octo     | High    |
| Saffron   | 9 – Nova     | High    |
| Nutmeg    | 10 – Dedl    | High    |
| Void Pepper | — none —   | No season (exotic drug, not farmed) |

**Seasonal offset by month offset from harvest** (index 0 = harvest month):

| Pattern | +0  | +1  | +2 | +3 | +4  | +5  | +6  | +7  | +8  | +9  |
|---------|-----|-----|----|----|-----|-----|-----|-----|-----|-----|
| Low     | 0   | 0   | +5 | +5 | +10 | +10 | +15 | +15 | +20 | +10 |
| Mid     | −20 | −15 | −5 | 0  | +5  | +10 | +20 | +15 | +10 | 0   |
| High    | −20 | −10 | 0  | +10| +20 | +30 | +40 | +50 | +30 | +20 |

There is always exactly one good being harvested each month.

---

## 🎊 Planet Festivals

Each planet has one annual festival. In the festival month, the featured good gets a one-time price spike to its base. The following month, the base drops by the same amount (hangover effect). Festival boosts: Low +50cr, Mid +75cr, High +100cr.

| Planet      | Month | Month Name | Festival Name              | Good      | Boost |
|-------------|-------|------------|----------------------------|-----------|-------|
| Terra       | 3     | Mari       | Cinnamon Roll Festival     | Cinnamon  | +50   |
| Agrica      | 4     | Aprix      | Paprika Panic Parade       | Paprika   | +50   |
| Zeta-9      | 6     | Iuin       | Golden Ginger Gala         | Ginger    | +75   |
| Void Colony | 8     | Octo       | Void Vanilla Vigil         | Vanilla   | +75   |
| Nexus       | 10    | Dedl       | Allspice Arbitrage Fête    | Allspice  | +100  |

Festival boost stacks on top of the seasonal offset and the spread.

---

## ⛽ Fuel

- Starting fuel: **500 / max 500**
- Minimum to depart: **50 fuel** (enforced — you cannot leave port below this)
- Travel cost: **10–50 fuel**, scales roughly with planet distance (index difference × 12 ± small random)
- Fuel price: **1 cr/unit** (global constant `FUEL_PRICE`, can be changed for events)
- Fuel Up and Drain Fuel are available in the **Engineering Bay** on the Spaceport

---

## 💰 Trade Mechanics

### Buying
- Pay the **buy price** (mean + spread) per unit
- Limited by credits and free cargo space

### Selling
- Receive the **sell price** (mean − spread) per unit
- **2% tax** applied on every sale, minimum 1 cr, rounded up
- Example: sell 10 × 35cr = 350cr gross, tax = 7cr, net = 343cr

### Win Condition
No hard win. Soft goal: accumulate 10,000 credits and buy the **Cinnamon Farm on Terra** (accessible via `[f]` in the Promenade). You can keep trading after purchase. The farm is purely vibes.

---

## ⚔️ Pirate Encounters

**Base encounter chance:** 25% per jump. Reduced to 10% with Long Range Radar installed.

Each encounter increases `piratangst` by 1. Piratangst affects fight difficulty and bribe cost escalation. Starts at 10.

### Options

| Option       | Effect |
|--------------|--------|
| **Fight**    | Compare your weapons vs pirate power `max(1, angst // 20)`. Costs +2 angst. Win → bounty `100 × angst` + 3 more angst. Lose → drop half cargo. Tie → standoff, pirate leaves. |
| **Flee**     | Costs fuel: `20 × angst` (or `5 × angst` with Booster). Capped so you keep minimum 50 fuel. |
| **Bribe**    | Pay `piratbribe` credits (starts 100, +100 per use, persists across sessions). −3 angst on success. |
| **Drop Cargo** | Lose half of each cargo type (rounded up, min 1). −2 angst. |
| **Bluff**    | Auto-pass if total cargo ≤ 10. Otherwise 50% pass / 50% fail (+2 angst, option locked for this encounter). |
| **Surrender** | GAME OVER. Prompted with confirmation. |

Pirate bribe amount is a **runtime variable** saved to file — it escalates throughout the whole playthrough.

---

## 🚀 Travel Events

After a successful jump (non-pirate roll):

| Chance | Event |
|--------|-------|
| 12%    | Spice Festival at destination — all prices ×1.1 |
| 10%    | Fuel Leak — lose 15–35 fuel |
| 8%     | Mystery Cargo — gain 5× Mystery Crate if space available |

---

## 🛸 Ship Upgrades (Engineering Bay → Upgrades)

All upgrades are one-time purchases. Some are planet-exclusive. All stack where applicable.

| Upgrade              | Cost  | Location     | Effect |
|----------------------|-------|--------------|--------|
| Kinetic Launcher     | 2000  | Any          | Weapon +1 |
| Mining Laser         | 1000  | Zeta-9       | Weapon +1 |
| Void Torpedo         | 5000  | Void Colony  | Weapon +2 |
| Stern Tank           | 1000  | Any          | Max fuel +200 |
| Portside Tank        | 2000  | Any          | Max fuel +300 |
| Cylindrical Tank     | 3000  | Any          | Max fuel +500 |
| Small Hold           | 1000  | Any          | Max cargo +100 |
| Side Hold            | 2000  | Terra        | Max cargo +100 |
| Grain Silo           | 3000  | Agrica       | Max cargo +200 |
| Galactic Broker License | 1000 | Nexus     | Unlock Price Check |
| Passenger Quoters    | 1000  | Any          | Unlock passenger slot |
| Long Range Radar     | 3000  | Terra        | Pirate chance −15% |
| Booster              | 1000  | Void Colony  | Flee fuel cost ×0.25 (5× instead of 20×) |

Maximum weapon power achievable: 4 (Kinetic +1, Mining Laser +1, Void Torpedo +2).
Pirate power formula: `max(1, angst // 20)` — weapon investment pays off over time.

---

## 🧍 Passengers

Requires **Passenger Quoters** upgrade installed.

- **20% chance** per planet arrival or cantina rest that a passenger spawns (one at a time)
- Passenger visible in Cantina as option `[3]` (only shown if Quoters installed)
- One slot. Taking a new passenger replaces the current one
- Deliver to their destination planet for **+300 credits**

**Current passenger roster:**

| Shortname  | Full Name                  | Notes |
|------------|----------------------------|-------|
| Whitemaine | Whitemaine, Pride Mercenary | Lion-like mercenary searching for his lost cub. Hates hyperlines. Pays fast. |

Roster is a list — more can be added in `PASSENGER_ROSTER` without code changes.

---

## 🏛️ Promenade

Accessed via `[6]` from the Spaceport. Houses planet-side services.

### Cantina

Every planet has a unique cantina with a local drink, bartender advice, and traveler services.

| Planet      | Cantina Name        | Drink               | Ingredient  |
|-------------|---------------------|---------------------|-------------|
| Terra       | The Cinnamon Tavern | Cinnamon Beer       | Cinnamon    |
| Zeta-9      | The Golden Saffron  | Saffron Mead        | Saffron     |
| Void Colony | The Pepper's Shadow | Void Pepper Whiskey | Void Pepper |
| Agrica      | The Paprika Den     | Spiced Paprika Ale  | Paprika     |
| Nexus       | The Clove & Dagger  | Clove Rum           | Clove       |

Drink cost = 50% of the ingredient's current sell price, min 1cr.

**Advice pools:** Game tips, Divorced Uncle wisdom, Uncle Iroh wisdom, Festival lore. One random line from a random pool per visit.

**Rest for a while:** Advances 1 month and 1 turn. Reveals the next entry in the galaxy background story queue (7 entries, plays once each in order). May spawn a new passenger.

### Infobroker

Free. Three reference tables:
- **Goods Directory** — which planets carry each good, which is production/demand
- **Harvest Seasons** — harvest month and pattern for each good
- **Festival Calendar** — planet, month, festival name, and featured good

Future: will display intel, timeline hints, harvesting missions once galaxy timeline exists.

### Concert Hall

Costs 10 credits. Attempts to load `songs.json`. If the file exists and has songs, plays a random one (title, lyrics, optional ASCII art). If the file is missing or empty, the 10cr is refunded and a message explains the artist was stopped by pirates.

`songs.json` is auto-created on first run with one song: *Event Horizon*.

**Song format** (for adding more manually):
```json
{
  "songs": [
    {
      "shortname": "eventhor",
      "fullname": "Event Horizon",
      "text": "...",
      "art": "..."
    }
  ]
}
```
Add more objects to the `songs` array. The game picks one at random each visit.

### Cinnamon Farm (Terra only)

Available via `[f]` inside the Promenade when on Terra.
- Purchase cost: **10,000 credits**
- Effect: unlocks farm visit with flavour text. No mechanical impact.
- You can still trade after purchase. Retirement is optional.

---

## 🔧 Engineering Bay

Accessed via `[8]` from the Spaceport (not the Promenade). Ship maintenance.

### Fuel Up
Options: +100 / +200 / +500 / +1000 / fill to max. Cost: `amount × FUEL_PRICE` (currently 1 cr/unit).

### Drain Fuel
Options: drain 100 / 200 / 500 / 1000 / 90% of current. Gain credits. Cannot drain below 50 (departure minimum).

### Upgrades
See upgrades table above. Each upgrade purchasable once. Planet-locked upgrades only appear when at the correct planet.

---

## 💾 Save System

- Saves to `spice_trader_save.json`
- Persists: ship state, all planet prices, calendar, piratangst, piratbribe, galaxy story index, passenger waiting, festival drop history
- Loads automatically on startup if file exists (prompts to confirm)

---

## 🛠️ Technical Notes

- Python 3.x, no required dependencies
- `requests` library optional — used only for remote RNG seed on travel events; falls back to local random if absent
- `FUEL_PRICE = 1` is a global constant — change this for economic events (OPEC crisis etc.)
- `MIN_FUEL_TO_DEPART = 50` is enforced at both travel and drain
- Cheat code: type `!credits N` at the action prompt to add N credits silently
- Price Check (`[5]`) requires Galactic Broker License (bought at Nexus for 1000cr)

---

## 📝 Ideas Parking Lot (future versions)

- **Stockpiles**: each planet has a finite stock of each good. Buying depletes it, selling fills it. Void Pepper produces ~10/year at Void Colony, Nexus consumes ~2/month — creates natural supply pressure without code intervention
- **Price Spread visible to Broker**: Broker License could show stockpile levels in Price Check
- **Pirate Trade Deal**: cantina event — sketchy contact offers Void Peppers for credits, no tax
- **Mystery Crate resolves**: could contain Void Pepper when found near Void Colony space
- **Infobroker future tier**: pay for intel about galaxy events, harvesting missions (pay now, get stock restock in 6 months)
- **Galaxy Timeline**: background story that advances, Infobroker leaks early hints
- **data.py extraction**: move all dicts (advice_pools, cantinas, planets_template, UPGRADES, PASSENGER_ROSTER, PLANET_FESTIVALS) into a separate file — pure content, no logic. Recommended when content editing becomes more frequent than feature adding
- **Multi-file structure** (future): main.py / state.py / systems/ / data/ — split when file exceeds comfortable scrolling
- **Black market planet**: illegal trades, high risk/reward
- **Factions**: trade guilds offering bonuses for specific goods
- **Spice spoilage**: random cargo loss during travel
- **Loans**: leveraged trading with interest
- **Cantina stranger quest**: smuggle droids, battlestation, rebel base, princess
- **Gossip pool**: flavour stories about Void Pepper and galaxy events
- **More passengers**: roster already structured as a list, just add entries

---

## 📜 Changelog Summary

| Version | Key Changes |
|---------|-------------|
| v9 | Promenade menu, Infobroker, Concert Hall, farm to [f], price spread (Sell/Buy columns), GOOD_DATA bounds table, news feed, songs.json system |
| v8.1 | Clove on Void Colony 40cr, Allspice festival high, Void Torpedo +2 weapons |
| v8 | Calendar, extra goods (3 planets each), 2% tax, inflation, harvest seasons, festivals, Engineering Bay, full upgrade system, Broker License gate, passengers, pirate encounter overhaul, cheat code, save/load |
| v7 | requests hook, dict-driven events, fuel/cargo split, recursion fixes, input validation, columnar price check, JSON save, distance-based travel |
| v6 | Original: basic trade loop, cantina, farm win condition |

---
Recent upgrader 

### V12

# If you quit you cant get back
Rekey 0 as universal go back key. If there is conflick we will look for some other keys. 
make "q" literally quit game key.
Since 0 back ->0 quite game, could be sad trader without the save. 
Sometimes 9 key is go back, so make it 0

# Randomize game start
Keep starting price/stockpile table in parameters for edit. 
But at game start (only once with new game) perform randomize price and stockpile action. 
For each planet and each good:
stockpile is  (random(25% stockpile, 75% stockpile)+parameter stockpile)/2 
Price is (random(minimal price, 2x default price)+parameter price)/2
With price and stockpile we need to do legality check, like stockpile cant be negative, or about max stockpile. Price needs to be in 30%,300% default price. 
The idea is that we have random element then add starting parameter from the table. And then we take mean of that. So there will be randomness, but also default setup matters. 


# Fleet Supply Depo
On Terra Promenade new location dropped. Fleet Supply Depo keybind "s". In is only there, unique location. 
It buys everything on fixed prices, has no stockpile, if it buys it disappears from game. 
The prices are min price + buy spread(from vendors) +5c. So we can buy goods on lowest price possible in galaxy, ship it here and get some profit. 
Cinamone is special, since it is produced on Terra so we only need to lorry it from farmland. Somone has to do it. So depo price 21 (max vendor buy is 20) 
If galaxy ever floods in spice, we can dump it into fleet. 
The fleeddepo price table should be an object in parameters. Maybe i will alter it later. 
Cinnamon	21
Turmeric	28
Paprika	31
Ginger	39
Clove	42
Vanilla	45
Cardamom	48
Allspice	56
Saffron	65
Nutmeg	62
Void Pepper	170
Only sell to depo. We cant buy from depo. 

# Songs.json and songs.py
This project is too small for us two. 
Remove reference to songs.json and creation, and all trace for it, and check, and try. 
songs.py remain, and is refernced and is place where song is load. 





### V11
# Balance
Festival price inpact. Recode it to [low 25, mid 35, high 50] so much lower from present values 50-100. Festivals are good, too good for now. 

### Stockpiles
Planets and markets get stockpiles of good. Size of stockpile depends on price class. 
Low price = 500 mid price =300 high price =100
The starting game value is half for everyone. But make it some list in parameters, maybe will hand mod it for some spicy opprotunities. So 250/500 150/300 50/100

## Player interaction with stockpile
When we buy on planet we take away from local stockpile. There need to be a blockade limit that we cant buy more than there is. There is already info of max buy, so there will be min(money/price, cargo empty, stockpile) 
When Player sell it adds to local stockpile, with similar logic, we cant sell to exeed local stockpile limit. 

## Stockpile impact on prices
During monthly price adjustment after random walk and other festival, harvest impact, we check for stockpile. 
If present stockpile<20% of max, the price rise by 5,10,20. 
If stockpile>80% the price drops by 5/10/20 depending on good price class. 
So if palnet is starving for cinamone it will pay more. And if has too much it will drop price. 
There are still max price ,and absolute min price. 

## Production
There need to be a production cycle, ideally before price adjustment. 
Production happens during harvest on all planets where good exist. 
Production happens in quantity of 16/32/64. But if planet has production of good it produces x3 times more. 
If local Stockpile is literally 0 when we start computacion, we produce x1.5 goods. So if we drain planet completly there will be generous harvest. 
We simulate independent farmers here and random traders. 

## Consumption
If good exist on planet market it is consumed after production phase. 
The consumption rate is equal to 2/4/7. 
If Planet has Demand on that good it consumes x2 og good. 
If stockpile is at least 80% full the consumption happens at x2 rate. It stacks with default demand, so we can x4 consumption if demand consumption is overflowing. 

### Void pappers
Produce 30 Void pappers on Void Colony in 10th month. and we consume 2 on void colony and 4 on Nexus. 

## Local Market (Flash Deals): 
On each Promenade create "Local Market" location. It will contain special 1 stor deals. 
Each time we visit planet there will be rolled 3 different goods in local market. And the price will be default price +sell price +/- (5,10,15 from price category). Local market only sells. 
When we enter planet the News Feed will generete line "Hot Deals: Good: Price, x5"  So it will print local deals for us. Byt only once per visit. 
We can only buy from local market. 
The quntity is 5/10/20. So small quantities. We can get void peppers that way. 
When we buy we have one shot, one opportunity, even when we buy 1 amount the trade is removed from list, and no longer visible. Trader just decides to go elsewhere. 
The good on local market dont have to be planet goods. Just intependent trader as us, doing his best. 

---

## Galaxy Random Events Blank and Impact
So far we have random newsfeed events:
```

atmospheric_events = [
    "A rogue freighter with 10,000 units of Void Pepper vanished near Nexus. No trace.",  
    "A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years.",  
    "The old Void Colony governor was arrested. The new one is friendlier to black-market deals.",  
    "The jump lanes near Terra are being taxed now. Change is coming.",  
    "The galaxy feels different lately. The old routes are shifting.",  
    "A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle.",  
    "Rumors spread of a hidden cache of Mystery Crates on Agrica.",  
    "A poet in the cantina recites a ballad about the lost spice fleets of Dedl.",  
    "The stars seem brighter tonight. Maybe it's the Void Pepper.",  
    "A traveler claims to have seen a ghost ship near the edge of the system."  
]  

```

Bu they do NOTHING. Time to change it.   
We add parameter rnd_event_split=0.2  
We add the list   
event_rnd_blank  
event_rnd_impact  
blank has atmospheric events which do nothinglike: Notorious card player Cheating Jack arrested for cheating in cardgame. or Fleet Supply HQ request citizens to donate their spice good. Come to your military before military comes to you. or "Join Terra Fleet. Travel the Galaxy. Encounter new alliens. Maybe Kill them. Healthplan Provides cybernetic prostetic. Sign up NOW!"

So here comes the list of blank events, they do nothing, just show up 80% by default. Can sit in library. 

```
"Terran scientis claim that Void Peppers are remains of ancient Space Whale. Should we protect extinct  specie?",
"Corporation Pandora on Agrica claims to bioengineer local bugs to produce Void Peppers in small quantity. Side effect is making bugs smarter. So far all speciments run away into the jungle" 
"A Space Whale was spotted near Zeta-9. Hasn't happened in thirty years."
"The old Void Colony governor was arrested. The new one is friendlier to black-market deals."
"The jump lanes near Terra are being taxed now. Change is coming."
"The galaxy feels different lately. The old routes are shifting."
"A broker mentions: the Senate voted to dissolve the Spice Trade Commission last cycle."
"Rumors spread of a hidden cache of Mystery Crates on Agrica."
"A poet in the cantina recites a ballad about the lost spice fleets of Dedl."
"The stars seem brighter tonight. Maybe it's the Void Pepper."
"A traveler claims to have seen a ghost ship near the edge of the system."
"Famout player Cheating Jack arrested in Promenade's Cantina, he was cheating in card game."
"Join Terra Fleet. Travel the Galaxy. Encounter new alliens. Maybe Kill them. Healthplan Provides cybernetic prostetic. Sign up NOW!",
"Fleet Supply HQ request citizens to donate their spice good. Come to your military before military comes to you",
"Tired of nonsence News? Buy subscribtion for Infobroker news on Promenade. No fake news. Just value.",
"Another expediction lost in the jungle on Agrica, during exploration of ancient ruins, What a loss.",
"Experimental Hyperdrive Cruise Ship >>Hindenburg<< lost without trace on first comercial flight. Oh the Humanity!",
"Senat votes the bill to limit use of AI in administrative decision making. But all artificial advisor suggest against it.",
"Excentric Googolplexier Melon Tusk tells more about his plan to trade in Cinamone Futures. >> Why move the spice around, when you could earn money by trading rights to maybe existing cinamone?<< he is asking the real questoin." 

```

Now the impact news. They should consist of tanname, fluff text, and script. But the script probably needs to be stored elsewhere, and tagname is the link. For now we can keep it in libary and parameters. Maybe will get file events later. the gagname could look like evri001 (event randdom impact 001) 
You generally need to make protection stockpile needs to be in brackets 0, stockpile for good price class. And Price need to be between min and max. 

"AGRICA DROUGHT — paprika yields expected to halve next season."

(Effect: Agrica’s Paprika stockpile -200, Paprika and Agrica price +20, need stockpile 0 protection, and price below max protectoin)


"Pirates attacked Void Colony! Stockpiles ransacked!"

(Effect: Void Colony’s Void Pepper stockpile -50, Clove stockpile -100, VC Void pper price +100, Clowe Price +50)


"Void Pepper smugglers caught on Nexus! Market flooded."

(Effect: Nexus’s Void Pepper stockpile +50, Void Pepper price on Nexus -100)


"Saffron harvest on Zeta-9 exceeds expectations!"

(Effect: Zeta-9’s Saffron stockpile +50, Saffron price on Zeta-9 -50)

"TERRA CINAMONE ORCHAND WILDFIRE - local farmers watch blazes consuming cinamone trees. It smells wonderful. But at waht cost?"
(Effect: Terra cinamone stockpil -200, Price +30, stockpile 0 protection, price max protection)

"AGRICA Farmers learned to harvest cinamone substitute from local berries. But will it compte with real thing?"
(Effect: Agrica cinamone stockpile +200, Price -30, minimal price protection, max stockpile protection) 

*NEXUS Popular pop star claims Saffron is Aphrodisiac. Demand sours in result."
(Effect Nexus Saffron Stockpile -50, price +50, protection) 

" Zeta 9, biggest importer of Tummeric goes backrupt. Who will fill the niche?"
(Effect Zeta 9, Tumeric stockpile -200, Price +30) 


---

# v13

# Industrial Goods

*New Goods:* 
- Minerals
- Alloys
- Weapons
- Soybeans
- Medicine
- Robots   


Industrial Goods have no harvest, are produced every month.
Industrial goods stockpiles 100small, 300 mid, 500 large
Industrial goods price spread 5/10/15
Price range 30% defaut min. 300% defaut max. 


## Parameter table 

Good ; Planets (P-production here) ; Stockpile ; Price ; Price Class

Minerals; Void Colony (P), Zeta9 ; 500; 80c low
Alloys; Zeta9 (P), Terra, Nexus; 300; 120c mid
Weapons; Terra(P), Void Colony, Agri; 100; 200c High
Soybeans; Agri(P), Zeta9, Nexus; 500, 60c Low
Medicine; Nexus(P), Void Colony, Terra, 100, 300c High
Robots; Terra(P), Void Colony, Zeta9, Agri, 300, 160c High

Parameter default table: Price in table is default price. Stockpile in table is half max stockpile. 

#### Starting Game Set Up
Stockpile is (Random(25%,75%)of max stockpile + table stockpile)/2
Price is (Random(min, 200% default) + parameter table)/2
Logic: We take random state of good add parameter table value and avg from that. So i can mod starting state a little, but also there is some randomness. 

## Consumption
If good exists on planet is is consumed. 
-1 Medicine, Weapons
-2 Alloys
-4 Minerals, Soybeans

If stockpile below 20% consumption /2 up, but at least 1. 
If stockpile above 80% consumption *2. 

### Price stockpile influence
If price is 20% stockpile or below, price change UP by 5/10/20 a month depending on price class. 
If price is 80% or above, price change DOWN by  5/10/20 a month. 


## Production
Medicine +2 Only Nexus  
Weapons +2 Only Terra  
Soybeans +8 Only Agri  
Minerals +8 Only Void Colony  
Alloys +4 Only Zeta 9  
Robots +4 Only  Terra  

+ If minerals stockpile > 50%, production of alloys *2
+ If alloys  stockpile > 50%, production of weapons *2
+ If weapons  stockpile > 50%, production of soybeans *2 (kill more bugs to chopchop forrest)
+ If robots stockpile>50%, production of soybeans *2
+ If robots stockpile>50%, production of minerals *2
+ If robots stockpile>50%, production of alloys *2

---

# Terra, Fleet Supply Depo and industrial good
Terra, Fleet Supply Depo now accepts industrial goods them goods:
Minerals
Alloys
Weapons
Soybeans
Medicine
Robots
The logic is same. Only buy from player, price is min price+spread+5. Check if supply price is +5 over min sell price potencial. 
In Case of robots, and gubs it is just +1 over min, since we just lorry from factory to depo, production on Terra. 


# Independent Trader

Independent traders happens late in month cycle. It happens late in the cycle after price and stockpile adjustment. There is parameter ind_tr_chance=0.3 which means chance to trigger intedepend trader. Independent Trader scans all pairs of planets. Each time there is 30% to skip. Could also pick half pairs from pool of planets (that could be quicker). For each planet it checks which good has highest difference on planets. It compares mean prices and dont care about sell/buy. And for that good it performs a trade according to the stockpile. it goes like (high price) 10/20/40 (low price). So Cinamone is 40units void peppers is 10. This need to be in parameters.  Independent trader cant negative stockpile, or overstockpile. Of course trader takes from low price planet, and moves to high price planet. Trader will take max possible from low price, even if at end journey there is no space.
Independent trader operation couse price rise by +5 on low side, and price drop on high side (destination) by -5. 

# Mining Operation 
To Mine we need Mining Laser installed, we can get one in engineering bay on Zeta 9. 
On first month each year asteroid fields spawn in Zeta 9 and Void Colony. In quantity 10-100 each. It rerolls each year, if we dont mine it, someone else do. 
We can acces asteroid fields from spaceport in Zeta 9 and Void Colony under key "a". For each respective asteroid field. 
So we can embark to mine from spacepor. There is a menu:
1 Mine a little (1 mont passes, we mine 10 minerals from field)
2 Mine for several months. (will ask us how long we want to mine, each month is 10 minerals, we need cargo hold) 
3 Mine it all (we keep mining untill field is depleted, 1 leftover ore is still full mont, we will only mine untill we have space in cargo hold.)  
0- Back to Spaceport  

### New equipment: Mining Drones
In Engineering Bay on Zeta 9, only there, there are Mining Drones 10000c. They allow to mine it all in 1 month, no matter the field. They will mine it all fast and clean. We still need place in cargo. 
Mining drones do not fight. 

* Game Should tell us that we need mining laser from Zeta 9 to mine. Otherwise it is just staring at rocks. *

### Comments. 
Generete a list of 10 thoughts during mining. Each time we mine, no matter 1 or many months a fluff text appears. Sample thoughts:
"It is aint much, but is honest work."
"Cant wait to feel the gravity."
"It is probably better than underground mines."
"I own the means of production, but it is stil hard labour."
"I hope market dont crush before i am done."
"Should take more beer for this journey."
"This is work for drones."
"That is a lot of work, but will it be useful, or had any exchange value?"
"A fellow miner passes by, at least we can talk over radio."
"If i took any longer, i will start getting hallucinations from the void."

---














