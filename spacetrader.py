import random

# --- Game Setup: Planets with Production, Demand, and Neutral Spices ---
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
            "Clove": 70
        },
        "farm_fluff": [
            "You sit on the porch of your cinnamon farm, sipping a warm drink. The sunset paints the orchard in gold, and the scent of spices fills the air.",
            "The cinnamon trees rustle in the breeze. A neighbor waves from across the field. 'Harvest was good this year,' they say.",
            "The scent of cinnamon fills the air. You made it. No more fuel calculations, no more pirate attacks. Just peace."
        ]
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
            "Nutmeg": 135
        }
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
            "Clove": 70
        }
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
            "Allspice": 80
        }
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
            "Turmeric": 40
        }
    }
}

# Initialize planets with random +/- 0-10 for non-production/demand prices
planets = {}
for planet_name, planet_data in planets_template.items():
    new_prices = {}
    for spice, price in planet_data["base_prices"].items():
        if spice == planet_data["production"] or spice == planet_data["demand"]:
            new_prices[spice] = price
        else:
            new_prices[spice] = max(1, price + random.randint(-10, 10))
    planets[planet_name] = {
        **planet_data,
        "base_prices": new_prices
    }

# --- Cantina Data ---
cantinas = {
    "Terra": {
        "name": "The Cinnamon Tavern",
        "drink": {
            "name": "Cinnamon Beer",
            "ingredient": "Cinnamon",
            "fluff": [
                "The warm, spicy beer fills your chest with nostalgia. It tastes like home—if home were a planet covered in cinnamon trees.",
                "You take a sip. It’s sweet, it’s spicy, it’s… exactly what you needed after a long day of haggling.",
                "The bartender winks. ‘Made from Terra’s finest. You won’t find this anywhere else.’"
            ]
        }
    },
    "Zeta-9": {
        "name": "The Golden Saffron",
        "drink": {
            "name": "Saffron Mead",
            "ingredient": "Saffron",
            "fluff": [
                "Golden and rich, this mead tastes like liquid sunlight. You suddenly understand why Zeta-9’s nobles are so smug.",
                "The mead is so expensive, the glass is lined with actual gold. Or maybe that’s just the lighting.",
                "You feel fancy just holding the glass. The bartender smirks—you’re clearly not from around here."
            ]
        }
    },
    "Void Colony": {
        "name": "The Pepper’s Shadow",
        "drink": {
            "name": "Void Pepper Whiskey",
            "ingredient": "Void Pepper",
            "fluff": [
                "The whiskey burns like a supernova going down. You see stars. Literally. Maybe don’t fly the ship for a while.",
                "This drink is so strong, it’s rumored to power small starships. You feel invincible. (You are not.)",
                "The bartender warns you: ‘One sip and you’ll forget your name. Two sips and you’ll forget your debts.’"
            ]
        }
    },
    "Agrica": {
        "name": "The Paprika Den",
        "drink": {
            "name": "Spiced Paprika Ale",
            "ingredient": "Paprika",
            "fluff": [
                "The ale is fiery and bold, just like Agrica’s farmers. You cough a little, but it’s worth it.",
                "The bartender slides you a glass. ‘Careful, that’s our house special. Made from last season’s best.’",
                "You take a sip and immediately feel warmer. Maybe it’s the ale, maybe it’s the planet’s famous hospitality."
            ]
        }
    },
    "Nexus": {
        "name": "The Clove & Dagger",
        "drink": {
            "name": "Clove Rum",
            "ingredient": "Clove",
            "fluff": [
                "The rum is smooth but packs a punch. Nexus traders swear by it to close deals.",
                "The bartender leans in. ‘This one’s on the house… if you tell me where you got that Void Pepper.’",
                "You sip it slowly. The flavor is complex, just like the deals made in this cantina."
            ]
        }
    }
}

# Advice pools
advice_pools = {
    "game": [
        "In theory, it is simple. Buy low, sell high. Move around for better deal. But life, life is more complex than that.",
        "Taking strangers on your ship can cause trouble. But life without them—all alone all the time—could get boring in the long run.",
        "You can collect credits forever, but at some point, there’s nothing more to buy. Maybe it’s time for that farm on Terra.",
        "Weapons are expensive to buy, but losing cargo to pirates will cost you more.",
        "Not all pirates are worth the fight. Your ship gets damaged, and they might like it. Bribery or running away is a valid option too.",
        "Nexus is full of bankers and brokers, all high on Void Pepper. They’ll pay any price to get their fix. You can get cheap peppers on Void Colony… or hunt Space Whales if that’s your style.",
        "Upgrading your ship will let you seize opportunities and face challenges you couldn’t before.",
        "Bad trades from the past won’t block you from good deals in the future.",
        "Even if the galaxy looks the same, just following the annual cycles, there are bigger changes in the background, altering the universe forever."
    ],
    "divorced": [
        "Never date a Psionic Girl. You’ll be judged by your thoughts, not just your actions and words.",
        "Some opportunities happen once in a lifetime. If you see a Space Whale, feast your eyes—it might never happen again.",
        "If you have a cargo hold full of Void Whiskey, don’t drink it all in one night. The hangover isn’t worth it, even for the spiciest nights.",
        "You need to look into your heart to save yourself from your other self. Only then will your true self reveal itself.",
        "There is no grand destiny, only semi-random rolls of unseen dice. We make our own destiny."
    ],
    "iroh": [
        "It’s important to trade with many planets. Wide horizons reveal opportunities unseen on stable routes.",
        "Life happens all the time, whether you manage it or not. But you can make it cozy and peaceful.",
        "Bad trades happen. You need to let go of pride and shame. Too much pride is the cause of shame and anger. Trading in anger leads to bad deals.",
        "Don’t take too much stuff onto your ship—no more than your cargo can hold. Always leave spare space for surprise opportunities.",
        "If you have a good ship and a bit of credits, you’re already better off than many. Just set a course and keep going until you reach your goal.",
        "You can accept errands from brokers, but don’t let others decide what your ultimate goal looks like. Your goal is what *you* want to achieve."
    ]
}

# --- Ship Setup ---
ship = {
    "credits": 1000,
    "cargo": {},
    "location": "Terra",
    "fuel": 1000,
    "max_cargo": 100,
    "farm_bought": False
}

# --- Helper Functions ---
def show_status():
    print(f"\n=== STATUS ===")
    print(f"Location: {ship['location']}")
    print(f"Credits: {ship['credits']}")
    print(f"Fuel: {ship['fuel']}")
    print(f"Cargo: {ship['cargo']} (Capacity: {ship['max_cargo'] - sum(ship['cargo'].values())} left)")
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

    if ship['location'] == "Terra":
        if not ship['farm_bought']:
            print("\n6. Buy Cinnamon Farm (10,000 credits)")
        else:
            print("\n6. Visit Cinnamon Farm")
    print("7. Visit Cantina")

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
            ship["fuel"]
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
            sell_price = 1
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
        ship["fuel"] += amount
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

        for spice in planets[destination]["base_prices"]:
            if spice != planets[destination]["production"] and spice != planets[destination]["demand"]:
                planets[destination]["base_prices"][spice] = max(
                    1,
                    planets[destination]["base_prices"][spice] + random.randint(-10, 10)
                )

        print(f"Traveled to {destination}. Fuel used: {fuel_cost}")
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
    print("\n" + "="*50)
    print(random.choice(planets["Terra"]["farm_fluff"]))
    print("="*50)
    print("\n[1] Stay a little longer")
    print("[2] Return to the stars")
    choice = input("Choose: ")
    if choice == "1":
        visit_farm()
    elif choice == "2":
        print("\nYou leave the farm, ready to face the galaxy again... or not.")
    else:
        print("You doze off on the porch. Time passes.")

# --- Cantina Functions ---
def visit_cantina():
    """Handle visiting the cantina on the current planet."""
    cantina = cantinas[ship["location"]]
    print(f"\n=== {cantina['name'].upper()} ({ship['location']}) ===")
    print("1. I need a drink")
    print("2. Ask for advice")
    print("3. I just need to rest for a moment")
    print("9. Back to spaceport")
    choice = input("Choose: ")

    if choice == "1":
        buy_drink(cantina)
    elif choice == "2":
        give_advice()
    elif choice == "3":
        rest_for_a_moment()
    elif choice == "9":
        return
    else:
        print("Invalid choice.")
        visit_cantina()

def buy_drink(cantina):
    """Buy a drink at the cantina."""
    drink = cantina["drink"]
    ingredient_price = planets[ship["location"]]["base_prices"][drink["ingredient"]]
    drink_cost = max(1, int(ingredient_price * 0.5))  # Drink costs half the ingredient's price

    if ship["credits"] < drink_cost:
        print(f"You don’t have enough credits for a {drink['name']} ({drink_cost} credits).")
        return

    ship["credits"] -= drink_cost
    print(f"\nYou buy a {drink['name']} for {drink_cost} credits.")
    print(random.choice(drink["fluff"]))

def give_advice():
    """Give random advice from one of the pools."""
    pool = random.choice(list(advice_pools.keys()))
    advice = random.choice(advice_pools[pool])
    print(f"\n[Bartender ({pool.upper()} ADVICE)]: {advice}")

def rest_for_a_moment():
    """Rest at the cantina (placeholder for future time skip)."""
    print("\n" + "-"*50)
    print("You spend a month in the cantina, drinking, eating snacks, and waiting for a good deal.")
    print("The days blur together as you watch traders come and go, their stories of profit and loss")
    print("echoing in your ears. You wonder if life is just a constant train of orders and tasks,")
    print("and if something awaits you beyond pirates and credits.")
    print("")
    print("Maybe it’s time to buy that nice cinnamon farm on Terra, to look at the trees in the sunset")
    print("instead of all this.")
    print("-"*50)
    print("\n[Press Enter to return to the cantina menu...]")
    input()  # Wait for user to press Enter
    visit_cantina()

# --- Game Loop ---
print("=== SPICE SPACE TRADER v6 ===")
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
        elif action == 7:
            visit_cantina()
        else:
            print("Invalid action.")
    except ValueError:
        print("Please enter a number.")
