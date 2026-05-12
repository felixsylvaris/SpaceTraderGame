Request for next update.  

maybe lost messege:
here is file i changed. Engineering Bay stays in Starport for now. I thought so much about it it was already in my eyes. We need some low value goods. So make sure that paprica is always low. Allspice.. default 120... even if in game there is low price, it could be hand fixed anytime.  Yes ultimate low for cinanome is 15-5, and max 155.  But since low goods have small spread... they will stay away from 0. Ok make the check if module instaled. (travelers). For now blast the song full speed. At least in terminal for now i could scroll back. Code.

# Small Tweaks
I changed .py file. Dont reatract this. 
v8.1(small twiches)
- drop price on Void Colony of Clover to 40 to avoid perfect pair with Nexus. 
- added high festival boost for allspice
- boosted void torpeda +2, so we can hunt pirates more efficient

# Farm f-key bind
On Terra farm interactions go for "f" key bind. It is special action and we may need numbers for popular options. 
Also farm exists only on Terra. While having appartment on Nexus could help managing trading empire, but void colony shelter is not a dream to chase. Just Terra farming. 

# Promenade > Cantine
On Planets in Spaceport Add Promenade link (6) which will move us to promenade screan. 
Promenade will be for some other services on planet, maybe less related with ship.trade. 
Move cantine there. 
On Terra move farm there with f key. Still only on terra. 
0 is back to spaceport

# Promenade and Infobroker
On Promenade on each planet add Infobroker. It will be place for extra insight. 
For now it will have options: 1) Goods 2) Harvest 3)Festivals

# =============================================================
#  INFOBROKER TABLES  —  paste these into spice_trader_v8.py
#  Call from visit_infobroker() or wherever fits in Promenade
# =============================================================

# ── TABLE 1: GOODS ────────────────────────────────────────────
def infobroker_goods_table():
    # Data derived from planets_template + GOOD_SEASONS
    # Columns: Good | Planets | Production | Demand
    goods_data = [
        # (good,          planets,                                    production,    demand)
        ("Allspice",    "Terra, Agrica, Nexus",                     "—",           "Terra"),
        ("Cardamom",    "Terra, Agrica, Void Colony",               "—",           "Void Colony"),
        ("Cinnamon",    "Terra, Zeta-9, Agrica",                    "Terra",       "—"),
        ("Clove",       "Terra, Void Colony, Nexus",                "Nexus",       "—"),
        ("Ginger",      "Terra, Zeta-9, Void Colony",               "—",           "Zeta-9"),
        ("Nutmeg",      "Zeta-9, Agrica, Nexus",                    "—",           "—"),
        ("Paprika",     "Terra, Zeta-9, Agrica",                    "Agrica",      "—"),
        ("Saffron",     "Zeta-9, Void Colony, Nexus",               "Zeta-9",      "—"),
        ("Turmeric",    "Zeta-9, Agrica, Nexus",                    "—",           "Nexus"),
        ("Vanilla",     "Terra, Void Colony, Agrica",               "—",           "Agrica"),
        ("Void Pepper", "Void Colony, Nexus",                       "Void Colony", "—"),
    ]

    W = [14, 32, 14, 14]
    sep = "  +" + "+".join("-" * w for w in W) + "+"
    header = (
        "  |" +
        "Good".ljust(W[0]) + "|" +
        "Planets".ljust(W[1]) + "|" +
        "Production".ljust(W[2]) + "|" +
        "Demand".ljust(W[3]) + "|"
    )

    print("\n── INFOBROKER: GOODS DIRECTORY ─────────────────────")
    print(sep)
    print(header)
    print(sep)
    for good, planets, production, demand in goods_data:
        row = (
            "  |" +
            good.ljust(W[0]) + "|" +
            planets.ljust(W[1]) + "|" +
            production.ljust(W[2]) + "|" +
            demand.ljust(W[3]) + "|"
        )
        print(row)
    print(sep)


# ── TABLE 2: FESTIVALS ────────────────────────────────────────
def infobroker_festival_table():
    # Data derived from PLANET_FESTIVALS + MONTH_NAMES
    # Columns: Planet | Mo# | Month | Festival Name | Good
    festival_data = [
        # (planet,        mo_num, mo_name, festival_name,               good)
        ("Terra",        3,  "Mari",  "Cinnamon Roll Festival",    "Cinnamon"),
        ("Agrica",       4,  "Aprix", "Paprika Panic Parade",      "Paprika"),
        ("Zeta-9",       6,  "Iuin",  "Golden Ginger Gala",        "Ginger"),
        ("Void Colony",  8,  "Octo",  "Void Vanilla Vigil",        "Vanilla"),
        ("Nexus",        10, "Dedl",  "Allspice Arbitrage Fete",   "Allspice"),
    ]

    W = [13, 4, 7, 26, 12]
    sep = "  +" + "+".join("-" * w for w in W) + "+"
    header = (
        "  |" +
        "Planet".ljust(W[0]) + "|" +
        "Mo#".ljust(W[1]) + "|" +
        "Month".ljust(W[2]) + "|" +
        "Festival Name".ljust(W[3]) + "|" +
        "Good".ljust(W[4]) + "|"
    )

    print("\n── INFOBROKER: FESTIVAL CALENDAR ───────────────────")
    print(sep)
    print(header)
    print(sep)
    for planet, mo_num, mo_name, fest_name, good in festival_data:
        row = (
            "  |" +
            planet.ljust(W[0]) + "|" +
            str(mo_num).ljust(W[1]) + "|" +
            mo_name.ljust(W[2]) + "|" +
            fest_name.ljust(W[3]) + "|" +
            good.ljust(W[4]) + "|"
        )
        print(row)
    print(sep)
    print("  Note: prices spike in festival month, drop the month after.")


# ── TABLE 3: HARVEST SEASONS ──────────────────────────────────
def infobroker_harvest_table():
    # Data derived from GOOD_SEASONS + MONTH_NAMES
    # Columns: Good | Mo# | Month | Pattern
    # Sorted by harvest month number
    harvest_data = [
        # (good,          mo_num, mo_name,  pattern)
        ("Cinnamon",    1,  "Ianu",  "Low"),
        ("Turmeric",    2,  "Febu",  "Low"),
        ("Paprika",     3,  "Mari",  "Mid"),
        ("Ginger",      4,  "Aprix", "Mid"),
        ("Clove",       5,  "Maiu",  "Mid"),
        ("Vanilla",     6,  "Iuin",  "Mid"),
        ("Cardamom",    7,  "Septr", "Mid"),
        ("Allspice",    8,  "Octo",  "High"),
        ("Saffron",     9,  "Nova",  "High"),
        ("Nutmeg",      10, "Dedl",  "High"),
        ("Void Pepper", "—", "—",    "None — no harvest cycle"),
    ]

    W = [14, 4, 7, 26]
    sep = "  +" + "+".join("-" * w for w in W) + "+"
    header = (
        "  |" +
        "Good".ljust(W[0]) + "|" +
        "Mo#".ljust(W[1]) + "|" +
        "Month".ljust(W[2]) + "|" +
        "Season Pattern".ljust(W[3]) + "|"
    )

    print("\n── INFOBROKER: HARVEST SEASONS ─────────────────────")
    print(sep)
    print(header)
    print(sep)
    for good, mo_num, mo_name, pattern in harvest_data:
        row = (
            "  |" +
            good.ljust(W[0]) + "|" +
            str(mo_num).ljust(W[1]) + "|" +
            mo_name.ljust(W[2]) + "|" +
            pattern.ljust(W[3]) + "|"
        )
        print(row)
    print(sep)
    print("  Low: prices rise slowly after harvest (+20 peak at anti-harvest).")
    print("  Mid: prices dip at harvest (-20), peak 5mo later (+20).")
    print("  High: prices dip hard at harvest (-20), peak 5mo later (+50).")

    For now it is free to access. 

    # Price Spread 
    The traders are haggling much better now. They will sell high and buy low, just as us. Bastards.  
        "Cinnamon":   (0,  "low"),   # harvest Ianu
    "Turmeric":   (1,  "low"),   # harvest Febu
    "Paprika":    (2,  "low"),   # harvest Mari
    "Ginger":     (3,  "mid"),   # harvest Aprix
    "Clove":      (4,  "mid"),   # harvest Maiu
    "Vanilla":    (5,  "mid"),   # harvest Iuin
    "Cardamom":   (6,  "mid"),   # harvest Septr
    "Allspice":   (7,  "high"),  # harvest Octo
    "Saffron":    (8,  "high"),  # harvest Nova
    "Nutmeg":     (9,  "high"),  # harvest Dedl
    "Void Pepper": High too,
    "Mystery Crate": None,

    Low -5/+5
    Mid -10/+10
    High -15/+15
    There is mean price which is subject of all changes. And spread changes which are alteration of mean price. 
    In price check and starport trade view the price are shown as sellprice/buyprice So higher price will be right. 

    # Max Price Min Price
    There is ultimate low price , max price in galaxy. And mean price (efficient) cant drop below min, and above max. Spread could push it below, or below, but only a little. 
    Min price is 30% of default, max price is 300% of default 
    min, mean, max, spreadtype
    "Cinnamon":  15,50,150,low 
    "Turmeric":  18,60,180,low 
    "Paprika":   21,70,210,low
    "Ginger":    24,80,240,mid
    "Clove":     27,90,270,mid
    "Vanilla":   30,100,300,mid 
    "Cardamom":  33,110,330,mid
    "Allspice":  36,120,360,high
    "Saffron":   45,150,450,high 
    "Nutmeg":    42,140,420,high 
    "Void Pepper": 150,500,1500,high
    Look at starting prices and make sure they are in brackets. 

    # Promenade Concert 
    In Promenade on every planet add "Concert" [10c] otpion. By entering we pay 10c and attempt to load song.json. There will be try to connect json file with song. If succesful it will write a song for us. Maybe some asci art. If connection failure it will give us 10c back, and message "Concert got cancelled since Artists was stopped by pirate attack. We all pray for their soon return." 
Note: This for testing IDE of multi file handling. And in future we can kick parameters, and libraries into other file, which would make engine codding faster. 

    # News Feed
    When we enter planet each time news feed is print. But if we enter cantina and then return to spaceport it will not. 1 is enought. 
    This could be done with temp flag newsread=1, set to 0 when newsfeed printed, and back to 1 when we leave planet. 
    Structure:
    "Travelers are waiting in Promenade Cantina" (only visible if travelers are indeed waiting)
    "Join {Festival Name} on {Planet}. Let the fun begin!" (Shown only if planet is right and month is right, this one will shown sparsly) 
    "Harvest {Good} in full swing. Reap all you can. Fill your stockpile untill yield last." (We check what good is currently harvested, this one is shown always, there should alwasy be some harvest maybe)
    
    # Song 
    So there will be songs.json file with dict of songs, with field shortname, full name, text, art (optional). Not sure if asci art is good call it could be fun. 
    It should handle more songs in future even if now is just one. 

    Actual Song:
    short: eventhor
    Full name: Event Horizon
    Text:
[Intro]   
They say we’re drifting in the dark
A spiral sunk beyond the mark
No light escapes, no truth gets through
Just echoes of what stars once knew



This ain’t the place they write in songs
No rising arc, no right from wrong
Just quiet weight, a silent hum
Where dreams go still, and futures (numb)

[Verse]
The sky’s a wall of starless sleep
We orbit silence, cold and deep
No ladder climbs, no prayers reply
The universe forgot to (try)

[Verse]
This isn’t hell, but not quite home
A waiting room with monochrome
Where every plan dissolves in time
And hope gets rusted, out of (line)

[Chorus]
But still I hang up fairy lights
In corners where there’s barely nights
I plant my cactus in a can
And hum a song where none began
The void won’t love me, this I know—
But damn it, I will (make it glow)

[Verse]
No hero arc, no breakthrough scene
No golden gate or field of green
Just coffee cold and half-paid rent
And tired hands that won’t (relent)

[Verse]
They say this hole will birth the next
A black hole’s child, a new context
But who will feel that newborn spark?
We’re trapped in here, and it’s still (dark)

[Bridge]
Some say to wait for rescue beams
But I’ve outlived a thousand dreams
So I just sweep this crater floor
And try to hope a little (more)

[Chorus]
But still I hang up fairy lights
In corners where there’s barely nights
I plant my cactus in a can
And hum a song where none began
The void won’t love me, this I know—
But damn it, I will (make it glow)

[Verse]
I rearrange the broken parts
Make space for books and open hearts
I water hope, though roots stay dry
And watch the ceiling, whisper (why?)

[Verse]
I’ll never touch another sky
But I still try, and I still try
To cook a meal, to write a joke
To find a reason not to (choke)

[Chorus]
But still I hang up fairy lights
In corners where there’s barely nights
I plant my cactus in a can
And hum a song where none began
The void won’t love me, this I know—
But damn it, I will (make it glow)

[Outro]
So here I stay, beneath the weight
No grand escape, no twist of fate
Just quiet fights and stubborn cheer—
I’ll build a home inside this (sphere)

[End]
I light a match, I breathe the grey
I make a bed where pain can lay
The black hole hums, and I reply—
“I’m here. I live. I (still) defy.”

Art: 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠖⠃⠀⠀⠀⡁⠀⠀⠀⠀⠀⠐⠆⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⢔⡤⠊⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠁⠀⠀⠘⠁⢀⠀⠀⠀⠀⢈⠓⠂⠠⡄⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⠿⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠒⠁⠀⠠⡚⠁⢀⣙⣀⣈⡩⠬⢁⠀⢑⠶⠤⡆⠤⡀⠀⠀⠀⠀⠀⠀⢀⠴⢲⣋⣽⣷⠟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⢠⠀⠀⣶⠃⠗⣡⣶⣮⣿⡿⠿⠿⢿⣿⣷⣶⣤⣤⠤⠴⠦⠬⣤⣤⠄⣉⠉⠝⢲⣿⡷⠻⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠁⡀⡸⠁⣰⣿⡿⠛⠋⣁⡀⠤⠤⢄⡀⠈⠛⢯⣿⣟⣾⣶⣶⣮⣭⣵⣾⣿⣟⠿⠉⢨⠖⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⢠⠳⡧⣻⡿⠋⢀⠒⠉⠀⠀⠀⠀⠀⠀⠉⠢⠀⠀⠙⠛⣻⣿⣿⣿⢿⣿⣿⠟⡱⠖⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⢠⣧⠓⣾⣿⠁⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢦⣠⣾⣿⠿⣿⣿⣿⡿⣫⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠂⢃⣸⣿⠇⢠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣿⠟⢿⠁⠸⡿⣿⣯⡶⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⢘⡄⠘⣿⣿⠀⠸⡀⠀⠀⠀⠀⠀⢀⣀⣴⣾⣿⡿⡟⡋⠐⡇⠀⢸⣿⣿⠃⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠘⢰⣿⡿⡆⠀⣇⠀⣀⣠⣤⣶⣿⢷⢟⠻⠀⠈⠀⠀⠀⡇⠀⣼⣿⣿⠂⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⢀⡴⢯⣾⠟⡏⢀⣠⣿⣿⣿⣟⢟⡋⠅⠘⠉⠀⠀⠀⠀⢀⠀⠁⢠⣿⣟⠃⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⣻⣷⡿⢙⣩⣶⡿⠿⠛⠉⠑⢡⡁⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⣰⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⣾⣥⣾⢫⡦⠾⠛⠙⠉⠀⠀⢀⣀⠀⠈⠙⠓⠦⠤⠤⠀⠘⠁⢀⡤⣾⡿⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠔⣴⣾⣿⣿⢟⢝⠢⠃⢀⣤⢴⣾⣮⣷⣶⢿⣶⡤⣐⡀⠀⣠⣤⢶⣪⣿⣿⡿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡀⣦⣾⡿⡛⠵⠺⢈⡠⠶⠿⠥⠥⡭⠉⠉⢱⡛⠻⠿⣿⣿⣿⣿⣿⠿⠿⠿⠟⠭⠛⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⢴⠕⣋⠝⠕⠐⠀⠔⠉⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠉⠁⠁⠁⠁⠈⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⣠⠁⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
