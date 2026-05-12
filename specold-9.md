# 🌌 Spice Space Trader

*A text-based interstellar trading game where players buy low, sell high, and outsmart the galaxy’s spice markets.*

---

## **📜 Core Concepts**

### **1. Overview**

- **Objective**: Accumulate credits by trading spices across planets. Buy spices where they’re cheap (production planets) and sell them where they’re in demand (for higher prices).
- **Win Condition**: No strict "win" condition—play until you’re satisfied with your credits or go bankrupt.
- **Gameplay Loop**: Buy → Travel → Sell → Repeat.

---

## **🌍 Planets**

There are **5 planets**, each with:

- **1 Production Spice**: Sold at a fixed low price (e.g., Terra produces **Cinnamon at 25 credits**).
- **1 Demand Spice**: Bought at a fixed high price (e.g., Terra demands **Allspice at 90 credits**).
- **3 Neutral Spices**: Prices fluctuate slightly (±10 credits) and are neither produced nor demanded here.


| Planet      | Production Spice  | Demand Spice | Neutral Spices               |
| ----------- | ----------------- | ------------ | ---------------------------- |
| Terra       | Cinnamon (25)     | Allspice     | Cardamom, Vanilla, Clove     |
| Zeta-9      | Saffron (200)     | Ginger       | Turmeric, Paprika, Nutmeg    |
| Void Colony | Void Pepper (500) | Cardamom     | Saffron, Ginger, Clove       |
| Agrica      | Paprika (20)      | Vanilla      | Cinnamon, Turmeric, Allspice |
| Nexus       | Clove (70)        | Turmeric     | Void Pepper, Nutmeg, Saffron |


---

## **📦 Goods (Spices)**

There are **10 spices** in the game. Each has a **base price** that varies by planet.  
**Key Spices and Their Roles**:

- **Production Spices**: Always sold at their **fixed low price** on their home planet.
- **Demand Spices**: Always bought at their **fixed high price** on their demand planet.
- **Neutral Spices**: Prices fluctuate by **+/- 0-10 credits** on each planet (except their production/demand planet).


| Spice       | Base Price Range  | Notes                     |
| ----------- | ----------------- | ------------------------- |
| Cinnamon    | 25 (Terra)        | Terra’s production.       |
| Cardamom    | 80                | Void Colony’s demand.     |
| Vanilla     | 120               | Agrica’s demand.          |
| Saffron     | 200 (Zeta-9)      | Zeta-9’s production.      |
| Turmeric    | 30                | Nexus’s demand.           |
| Void Pepper | 500 (Void Colony) | Void Colony’s production. |
| Nutmeg      | 40                | Neutral on most planets.  |
| Paprika     | 20 (Agrica)       | Agrica’s production.      |
| Ginger      | 60                | Zeta-9’s demand.          |
| Allspice    | 90                | Terra’s demand.           |
| Clove       | 70 (Nexus)        | Nexus’s production.       |


---

## **💰 Trade Mechanics**

### **Production and Demand**

- **Production Spice**:
  - Sold at a **fixed low price** on its home planet (e.g., Cinnamon is **25** on Terra).
  - Can be bought **cheaply** here and sold elsewhere for profit.
- **Demand Spice**:
  - Bought at a **fixed high price** on its demand planet (e.g., Allspice is **90** on Terra).
  - Selling here yields the **highest profit** for that spice.

### **Drifting Prices**

- **Neutral Spices**: Prices on each planet change by **+/- 0-10 credits** every time you **travel to that planet**.
  - Example: Turmeric on Agrica might be **25** one visit, then **30** the next.
  - **Production/Demand spices** never change price on their home planet.
- **Price Check Command**: Use `5. Price Check` to see current prices across all planets.

---

## **⛽ Fuel Management**

- **Fuel Costs**:
  - **Traveling**: Costs **10-30 fuel** per trip (randomized).
  - **Buying Spices**: Costs **1 fuel per unit** (e.g., buying 10 Cinnamon = -10 fuel).
  - **Selling Spices**: Refunds **1 fuel per unit** sold.
- **Running Out of Fuel**:
  - If you don’t have enough fuel to travel or buy, you’re **stranded** until you sell cargo to refuel.
- **Starting Fuel**: **1000** (enough for ~30-100 trips, depending on cargo).

---

## **🎮 Functionality**

### **Commands**


| Command | Action      | Details                                                        |
| ------- | ----------- | -------------------------------------------------------------- |
| 1       | Buy Spice   | Buy spices from the current planet’s market.                   |
| 2       | Sell Spice  | Sell spices from your cargo to the current planet.             |
| 3       | Travel      | Move to another planet (costs fuel). Prices update on arrival. |
| 4       | Status      | Check your credits, fuel, cargo, and location.                 |
| 5       | Price Check | View all spices’ buy/sell prices across all planets.           |
| 0       | Quit        | End the game and see your final credits.                       |


### **Game Loop**

1. **Check Prices** (`5`) to find profitable routes.
2. **Buy** (`1`) spices where they’re cheap (e.g., Cinnamon on Terra).
3. **Travel** (`3`) to a planet where the spice is in demand or priced higher.
4. **Sell** (`2`) for profit.
5. Repeat!

---

## **💡 Example Trade Routes**


| Buy Spice @ Planet        | Sell Spice @ Planet | Example Profit/Unit |
| ------------------------- | ------------------- | ------------------- |
| Cinnamon @ Terra          | Agrica              | ~30-40 credits      |
| Void Pepper @ Void Colony | Nexus               | ~250 credits        |
| Allspice @ Agrica         | Terra               | ~45 credits         |
| Turmeric @ Agrica         | Nexus               | ~15-25 credits      |


---
### 🌿 Cinnamon Farm (Win Condition)

- **Cost**: 10,000 credits (purchased on **Terra**).
- **Effect**:
  - Unlocks the ability to **visit your farm** on Terra.
  - Enjoy **peaceful fluff text** about your new life as a cinnamon farmer.
  - No gameplay impact—just **pure, honest vibes**.
- **How to Use**:
  - Buy the farm from Terra’s menu (`6. Buy Cinnamon Farm`).
  - After purchasing, select `6. Visit Cinnamon Farm` to relax.
- **Lore**: *"You won. The end."*
- **Note**: You can still trade after buying the farm—retirement is optional!
---
### 🍺 Cantina System
Every planet has a **unique cantina** where you can:
- **Buy a local drink** (costs 1-5x the ingredient’s price, e.g., Void Pepper Whiskey = 250 credits).
- **Ask for advice** (random tips from 3 pools: *Game Advice*, *Divorced Uncle Wisdom*, *Uncle Iroh Wisdom*).
- **Rest for a moment** (fluff text + time skip).

#### **Drinks by Planet**
   Planet       | Cantina Name       | Drink               | Cost (Base) |
 |--------------|--------------------|---------------------|-------------|
 | Terra        | The Cinnamon Tavern | Cinnamon Beer       | 13          |
 | Zeta-9       | The Golden Saffron  | Saffron Mead        | 50          |
 | Void Colony  | The Pepper’s Shadow | Void Pepper Whiskey | 250         |
 | Agrica       | The Paprika Den     | Spiced Paprika Ale  | 15          |
 | Nexus        | The Clove & Dagger  | Clove Rum           | 18          |

#### **Advice Pools**
- **Game Advice**: Practical trading tips.
- **Divorced Uncle**: Weird, philosophical, or cautionary tales.
- **Uncle Iroh**: Wise, cozy, or trading-focused wisdom.

---


## **🔧 Technical Notes**

- **Python Version**: 3.x
- **Dependencies**: None (pure Python).
- **How to Run**: Save the script as `spice_trader.py` and run with `python spice_trader.py`.
- **Customization**:
  - Edit `planets_template` in the code to change spices, prices, or planets.
  - Adjust `ship["max_cargo"]` or `ship["fuel"]` to change difficulty.

---

## **📝 Changelog (Ideas for Future Versions)**

- Add **spice spoilage** (random loss of cargo during travel).
- Add **WorkShop** Allows to buy upgrades, cargo, fueltank, weapons
- Add a **black market planet** with illegal trades.
- Add **loans/credits** for leveraged trading.
- Add **ship upgrades** (more cargo space, better fuel efficiency).
- Add **factions** (e.g., trade guilds that offer bonuses for specific spices).
- Add **cantine** and buy local drink, does nothing gets tipsy
- Add **gossip** 2 pools of stories, 1 is flavour trash about Void Pappers
- Add **galaxy side story** galaxy has a storyline in background it picks 1 story from top in order, we can hear only 1 on each visit so it progresses slowly
- Add **cantina stranger** personal quest, we smuggle droids, there will be battlestation, rebel base, and princess.

---
## Past Patch Notes


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

**Changes from v6:**
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
  
