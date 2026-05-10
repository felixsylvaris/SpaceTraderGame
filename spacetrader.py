import random

# --- Game Setup: Planets with Production, Demand, and Neutral Spices ---
# UPDATED PRICES: More chaos, more profit opportunities!
planets_template = {
    "Terra": {
        "production": "Cinnamon",
        "demand": "Allspice",
        "spices": ["Cinnamon", "Cardamom", "Vanilla", "Allspice", "Clove"],
        "base_prices": {
            "Cinnamon": 25,    # Production price (fixed)
            "Cardamom": 100,   # Updated
            "Vanilla": 90,     # Updated
            "Allspice": 100,   # Demand price (fixed) - Updated
            "Clove": 70
        },
        # Farm-specific fluff text for when the player visits
        "farm_fluff": [
            "You sit on the porch of your cinnamon farm, sipping a warm drink. The sunset paints the orchard in gold, and the scent of spices fills the air. The trade routes, pirates, and hustle feel like a lifetime ago.",
            "The cinnamon trees rustle in the breeze. A neighbor waves from across the field. 'Harvest was good this year,' they say. You nod. It was.",
            "The scent of cinnamon fills the air. You made it. No more fuel calculations, no more pirate attacks. Just peace.",
            "Your farmhand brings you a fresh cinnamon roll. You take a bite. It’s perfect. You’ve won the game.",
            "The stars blink above your farm. Somewhere out there, traders are still hustling. Not you. You’re home."
        ]
    },
    "Zeta-9": {
        "production": "Saffron",
        "demand": "Ginger",
        "spices": ["Saffron", "Turmeric", "Paprika", "Ginger", "Nutmeg"],
        "base_prices": {
            "Saffron": 100,    # Production price (fixed) - Updated
            "Turmeric": 50,    # Updated
            "Paprika": 60,     # Updated
            "Ginger": 90,      # Demand price (fixed) - Updated
            "Nutmeg": 135      # Updated
        }
    },
    "Void Colony": {
        "production": "Void Pepper",
        "demand": "Cardamom",
        "spices": ["Void Pepper", "Saffron", "Ginger", "Cardamom", "Clove"],
        "base_prices": {
            "Void Pepper": 500,  # Production price (fixed)
            "Saffron": 200,
            "Ginger": 65,       # Updated
            "Cardamom": 80,     # Demand price (fixed)
            "Clove": 70
        }
    },
    "Agrica": {
        "production": "Paprika",
        "demand": "Vanilla",
        "spices": ["Paprika", "Cinnamon", "Turmeric", "Vanilla", "Allspice"],
        "base_prices": {
            "Paprika": 30,      # Production price (fixed) - Updated
            "Cinnamon": 50,
            "Turmeric": 30,
            "Vanilla": 120,     # Demand price (fixed)
            "Allspice": 80      # Updated
        }
    },
    "Nexus": {
        "production": "Clove",
        "demand": "Turmeric",
        "spices": ["Clove", "Void Pepper", "Nutmeg", "Saffron", "Turmeric"],
        "base_prices": {
            "Clove": 35,        # Production price (fixed) - Updated
            "Void Pepper": 750, # Note: Nexus doesn't produce Void Pepper, but this is its base price here
            "Nutmeg": 110,      # Updated
            "Saffron": 175,     # Updated
            "Turmeric": 40      # Demand price (fixed) - Updated
        }
    }
}

# Initialize planets with random +/- 0-10 for non-production/demand prices
planets = {}
for planet_name, planet_data in planets_template.items():
    new_prices = {}
    for spice, price in planet_data["base_prices"].items():
        if spice == planet_data["production"] or spice == planet_data["demand"]:
            new_prices[spice] = price  # Keep production/demand prices fixed
        else:
            new_prices[spice] = max(1, price + random.randint(-10, 10))  # +/- 0-10, min 1
    planets[planet_name] = {
        **planet_data,
        "base_prices": new_prices
    }

# --- Ship Setup ---
ship = {
    "credits": 1000,
    "cargo": {},
    "location": "Terra",
    "fuel": 1000,
    "max_cargo": 100,  # Max units of spices you can carry
    "farm_bought": False  # Global flag: Has the player bought the cinnamon farm?
}

# --- Helper Functions ---
def show_status():
    print(f"\n=== STATUS ===")
    print(f"Location: {ship['location']}")
    print(f"Credits: {ship['credits']}")
    print(f"Fuel: {ship['fuel']}")
    print(f"Cargo: {ship['cargo']} (Capacity: {ship['max_cargo'] - sum(ship['cargo'].values())} left)")
    # Show farm status if on Terra
    if ship['location'] == "Terra" and ship['farm_bought']:
        print("You own a cinnamon farm here. Home sweet home.")

def show_market():
    planet = planets[ship["location"]]
    print(f"\n=== MARKET: {ship['location']} ===")
    print(f"Production: {planet['production']} (sold at {planet['base_prices'][planet['production']]} credits)")
    print(f"Demand: {planet['demand']} (bought at {planet['base_prices'][planet['demand']]} credits)")
    print("\nAvailable Spices:")
    for spice in planet["spices"]:
        price = planet["base_prices"][spice]
        role = ""
        if spice == planet["production"]:
            role = " (PRODUCTION)"
        elif spice == planet["demand"]:
            role = " (DEMAND)"
        print(f"- {spice}: {price} credits{role}")

    # Add farm option to Terra's menu
    if ship['location'] == "Terra":
        if not ship['farm_bought']:
            print("\n6. Buy Cinnamon Farm (10,000 credits)")
        else:
            print("\n6. Visit Cinnamon Farm")

def buy_spice():
    planet = planets[ship["location"]]
    print("\nAvailable Spices to Buy:")
    for i, spice in enumerate(planet["spices"], 1):
        price = planet["base_prices"][spice]
        print(f"{i}. {spice} ({price} credits/unit)")
    try:
        choice = int(input("Choose spice to buy (or 0 to cancel): "))
        if choice == 0:
            return
        spice = planet["spices"][choice-1]
        price = planet["base_prices"][spice]
        max_buy = min(
            ship["credits"] // price,
            ship["max_cargo"] - sum(ship["cargo"].values()),
            ship["fuel"]  # 1 fuel per unit
        )
        if max_buy <= 0:
            print("Not enough credits, cargo space, or fuel!")
            return
        amount = int(input(f"How many units of {spice}? (Max: {max_buy}): "))
        if amount <= 0 or amount > max_buy:
            print("Invalid amount.")
            return
        cost = amount * price
        ship["credits"] -= cost
        ship["cargo"][spice] = ship["cargo"].get(spice, 0) + amount
        ship["fuel"] -= amount
        print(f"Bought {amount} {spice} for {cost} credits.")
    except (ValueError, IndexError):
        print("Invalid choice.")

def sell_spice():
    if not ship["cargo"]:
        print("Your cargo hold is empty!")
        return
    planet = planets[ship["location"]]
    print("\nYour Cargo:")
    for i, (spice, amount) in enumerate(ship["cargo"].items(), 1):
        if spice in planet["base_prices"]:
            sell_price = planet["base_prices"][spice]
        else:
            sell_price = 1  # Default to 1 if spice not on this planet
        print(f"{i}. {spice} ({amount} units) - {sell_price} credits/unit")
    try:
        choice = int(input("Choose spice to sell (or 0 to cancel): "))
        if choice == 0:
            return
        spice = list(ship["cargo"].keys())[choice-1]
        amount = int(input(f"How many units of {spice}? (Max: {ship['cargo'][spice]}): "))
        if amount <= 0 or amount > ship["cargo"][spice]:
            print("Invalid amount.")
            return
        if spice in planet["base_prices"]:
            sell_price = planet["base_prices"][spice]
        else:
            sell_price = 1
        earnings = amount * sell_price
        ship["credits"] += earnings
        ship["cargo"][spice] -= amount
        if ship["cargo"][spice] == 0:
            del ship["cargo"][spice]
        ship["fuel"] += amount  # Refuel when selling
        print(f"Sold {amount} {spice} for {earnings} credits.")
    except (ValueError, IndexError):
        print("Invalid choice.")

def travel():
    print("\nAvailable Planets:")
    for i, planet in enumerate(planets.keys(), 1):
        print(f"{i}. {planet}")
    try:
        choice = int(input("Choose destination (or 0 to cancel): "))
        if choice == 0:
            return
        destination = list(planets.keys())[choice-1]
        fuel_cost = random.randint(10, 30)
        if fuel_cost > ship["fuel"]:
            print("Not enough fuel!")
            return
        ship["fuel"] -= fuel_cost
        ship["location"] = destination

        # Dynamic pricing: Adjust all prices on this planet by +/- 0-10 when arriving
        for spice in planets[destination]["base_prices"]:
            if spice != planets[destination]["production"] and spice != planets[destination]["demand"]:
                planets[destination]["base_prices"][spice] = max(
                    1,
                    planets[destination]["base_prices"][spice] + random.randint(-10, 10)
                )

        print(f"Traveled to {destination}. Fuel used: {fuel_cost}")
        # Random event
        if random.random() < 0.2:
            event = random.choice([
                f"Pirate attack! Lose {min(100, ship['credits']//2)} credits.",
                f"Spice festival! All spices +10% value on {destination}!",
                "Fuel leak! Lose 20 fuel."
            ])
            print(f"\n!!! EVENT: {event}")
            if "Pirate" in event:
                ship["credits"] -= min(100, ship["credits"] // 2)
            elif "Fuel leak" in event:
                ship["fuel"] = max(0, ship["fuel"] - 20)
            elif "Spice festival" in event:
                for spice in planets[destination]["base_prices"]:
                    planets[destination]["base_prices"][spice] = int(
                        planets[destination]["base_prices"][spice] * 1.1
                    )
    except (ValueError, IndexError):
        print("Invalid choice.")

def price_check():
    print("\n=== PRICE CHECK ===")
    print("Planet\t\tSpice\t\tBuy/Sell Price\tRole")
    print("------\t\t------\t\t--------------\t----")
    for planet_name, planet in planets.items():
        for spice in planet["spices"]:
            price = planet["base_prices"][spice]
            role = ""
            if spice == planet["production"]:
                role = "PRODUCTION"
            elif spice == planet["demand"]:
                role = "DEMAND"
            print(f"{planet_name}\t\t{spice}\t\t{price}\t\t{role}")

def visit_farm():
    """Function to handle visiting the cinnamon farm on Terra."""
    print("\n" + "="*50)
    print(random.choice(planets["Terra"]["farm_fluff"]))
    print("="*50)
    print("\n[1] Stay a little longer")
    print("[2] Return to the stars")
    choice = input("Choose: ")
    if choice == "1":
        # Recursively call to stay longer (more fluff!)
        visit_farm()
    elif choice == "2":
        print("\nYou leave the farm, ready to face the galaxy again... or not.")
    else:
        print("You doze off on the porch. Time passes.")

# --- Game Loop ---
print("=== SPICE SPACE TRADER v5 ===")
print("Trade spices across the galaxy. Buy low, sell high, and watch out for pirates!")
print("Commands: 1. Buy, 2. Sell, 3. Travel, 4. Status, 5. Price Check, 0. Quit")

while True:
    show_status()
    show_market()
    try:
        action = int(input("\nChoose action: "))
        if action == 0:
            print("Game over. Final credits:", ship["credits"])
            if ship["farm_bought"]:
                print("You retired to your cinnamon farm. You won.")
            break
        elif action == 1:
            buy_spice()
        elif action == 2:
            sell_spice()
        elif action == 3:
            travel()
        elif action == 4:
            show_status()
        elif action == 5:
            price_check()
        elif action == 6 and ship['location'] == "Terra":
            # Handle farm purchase or visit
            if not ship['farm_bought']:
                if ship['credits'] >= 10000:
                    ship['credits'] -= 10000
                    ship['farm_bought'] = True
                    print("\nCongratulations! You now own a cinnamon farm on Terra.")
                    print("You can visit it anytime by selecting 'Visit Cinnamon Farm' when on Terra.")
                else:
                    print("\nYou need 10,000 credits to buy the farm.")
            else:
                visit_farm()
        else:
            print("Invalid action.")
    except ValueError:
        print("Please enter a number.")
