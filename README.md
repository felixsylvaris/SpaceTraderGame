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
- Add a **black market planet** with illegal trades.
- Add **loans/credits** for leveraged trading.
- Add **ship upgrades** (more cargo space, better fuel efficiency).
- Add **factions** (e.g., trade guilds that offer bonuses for specific spices).
- Add **cantine** and buy local drink, does nothing gets tipsy
- Add **gossip** 2 pools of stories, 1 is flavour trash about Void Pappers
- Add **galaxy side story** galaxy has a storyline in background it picks 1 story from top in order, we can hear only 1 on each visit so it progresses slowly
- Add **cantina stranger** personal quest, we smuggle droids, there will be battlestation, rebel base, and princess. 
  
