# =============================================================
#  SPICE SPACE TRADER — data/exp/easy_job.py
#  Mission: Easy Job
#  Entry point: run_easy_job(ship, character, state)
#  Returns when mission ends (any outcome).
#  Modifies ship["credits"] and ship["cargo"] in place.
#  Modifies character["easy_job_token"] in place.
#  No imports from game.py or parameters.py.
# =============================================================

# ── HELPERS ───────────────────────────────────────────────────

def _stat(character, key):
    return character["stats"].get(key, 0)

def _has(character, key):
    return key in character["equipment"]

def _print_header(title):
    print("\n" + "─"*52)
    print(f"  {title}")
    print("─"*52)

def _pause():
    input("\n  [Enter to continue...]")

def _hp_bar(exphp):
    filled = max(0, exphp[0])
    total  = exphp[1]
    bar    = "█" * filled + "░" * (total - filled)
    return f"HP: [{bar}] {exphp[0]}/{exphp[1]}"

def _take_damage(exphp, amount, reason=""):
    actual = max(0, amount)
    exphp[0] -= actual
    if reason:
        print(f"\n  💥 {reason}  −{actual} HP  ({_hp_bar(exphp)})")
    else:
        print(f"\n  💥 −{actual} HP  ({_hp_bar(exphp)})")

def _heal(exphp, amount, reason=""):
    actual = min(amount, exphp[1] - exphp[0])
    exphp[0] = min(exphp[1], exphp[0] + actual)
    if actual > 0:
        msg = reason if reason else f"+{actual} HP"
        print(f"\n  💊 {msg}  ({_hp_bar(exphp)})")

def _is_dead(exphp):
    return exphp[0] <= 0

def _choice(options):
    """
    options: list of (key, label) tuples.
    Returns chosen key string.
    """
    print()
    for key, label in options:
        print(f"  [{key}] {label}")
    valid = {k for k, _ in options}
    while True:
        raw = input("\n  Your choice: ").strip().lower()
        if raw in valid:
            return raw
        print(f"  Choose from: {', '.join(sorted(valid))}")

# ── RESOLUTION ────────────────────────────────────────────────

def _end_mission(ship, character, outcome, got_peppers=False, spent_credits=False):
    """
    Handle all end-of-mission bookkeeping and print closing text.
    outcome: "success_paid" | "success_free" | "success_kill" | "walked" | "surrendered" | "bled_out" | "ran"
    """
    print("\n" + "═"*52)

    if got_peppers:
        amount = 20
        ship["cargo"]["Void Pepper"] = ship["cargo"].get("Void Pepper", 0) + amount
        print(f"  +{amount} Void Pepper added to cargo.")

    if outcome == "success_paid":
        ship["credits"] -= 5000
        print("  −5,000 cr paid to Vex.")
        print("\n  You paid the man. You got the goods. A deal's a deal,")
        print("  even when the deal was made at gunpoint in a jungle at midnight.")
        print("  The Nexus market will make you whole. Probably.")

    elif outcome == "success_free":
        print("  You kept your credits. Vex kept his life. Even trade.")
        print("\n  The jungle swallows the sound of retreating footsteps.")
        print("  You walk back to the spaceport with 20 bags of synthetic void")
        print("  and the particular satisfaction of someone who won a fight")
        print("  they didn't start.")

    elif outcome == "success_kill":
        print("  Vex didn't make it. His drugs are yours now.")
        print("\n  The jungle doesn't care. It was already making noise")
        print("  before the shots and it's making the same noise after.")
        print("  You collect the bags and don't look at what's left.")
        print("  Some jobs end clean. This one ended.")

    elif outcome == "walked":
        print("  You walked away empty-handed. Credits intact. Dignity intact.")
        print("\n  Some jobs aren't worth the trouble. This was one of them.")
        print("  The Punkbusters will find another mark. You'll find another deal.")

    elif outcome == "ran":
        print("  You made it back. Bleeding, muddy, empty-handed.")
        print("\n  The bartender at The Paprika Den takes one look at you")
        print("  and pours something without being asked.")
        print("  You didn't get the drugs. You didn't lose the credits.")
        print("  You're alive. On Agrica, that counts.")

    elif outcome == "bled_out":
        ship["credits"] -= 5000
        print("  −5,000 cr. They took everything.")
        print("\n  You wake up face-down in the mud, lighter by 5,000 credits")
        print("  and several units of dignity. The bartender finds you")
        print("  crawling back to the spaceport and gives you a free drink")
        print("  and an ice pack. She doesn't ask questions.")
        print("  Neither do you.")

    print("\n" + "═"*52)
    _pause()

# ── NODES ─────────────────────────────────────────────────────

def _ejx01(ship, character, state, exphp):
    """Start — pre-mission briefing, choose preparation."""
    _print_header("EASY JOB  —  The Setup")

    print("""
  You agreed to meet a dealer named Vex, who wants to offload
  20 bags of synthetic Void Pepper — locally called Beetlejuice —
  for 5,000 credits. On Nexus it would fetch twice that, easy.

  In and out. Quick trade. Back on the ship before sector security
  even knows you were here. The classic easy job.

  Vex wants to meet outside the city walls tonight, away from
  prying eyes. The jungle starts where the lights end.
  You still have a few hours to kill.""")

    if _stat(character, "medicine") >= 1:
        print("""
  [You know the Beetlejuice angle. Corporation Pandora has been
   trying to synthesise Void Pepper from local insect biochemistry.
   Results are inconsistent and the bugs keep escaping the lab.
   The product is cheap because nobody trusts it yet.]""")

    if _stat(character, "power") >= 2:
        print("""
  [You're carrying enough hardware to start a small war.
   You hope Vex doesn't spook when he sees you coming.]""")

    ch = _choice([
        ("1", "Head to the cantina. Kill time properly."),
        ("2", "Ask around about Vex. Do some homework."),
        ("0", "Actually — forget it. Back to the promenade."),
    ])

    if ch == "0":
        character["easy_job_token"] -= 1
        print("\n  You think better of it. The token is spent — Vex won't")
        print("  wait forever and you've already made the first move.")
        _pause()
        return "promenade"

    if ch == "1":
        return _ejx01x1(ship, character, state, exphp)
    if ch == "2":
        return _ejx01x2(ship, character, state, exphp)


def _ejx01x1(ship, character, state, exphp):
    """Optional node — cantina detour."""
    _print_header("The Paprika Den — Late Afternoon")

    print("""
  You find a corner booth and nurse something amber and sharp.
  The Den is loud with shift workers ending their day.
  Without even trying, you catch a name: Vex. Leader of a small
  outfit called the Punkbusters. Too small to matter, apparently —
  nobody finishes the story. He's not worth the words.""")

    _pause()
    return _ejx02(ship, character, state, exphp)


def _ejx01x2(ship, character, state, exphp):
    """Optional node — recon. Costs 1 HP, gives intel."""
    _print_header("Street Work")

    print("""
  You spend the afternoon circling the promenade and the outer
  market stalls, buying drinks you don't finish, asking questions
  sideways. Someone clips you near the cargo yards — wrong place,
  wrong time, or maybe not. You walk away with a bloody nose
  and a cleaner picture.""")

    _take_damage(exphp, 1, "Scuffle in the cargo yards.")

    print("""
  Vex runs the Punkbusters. Small crew, big mouths, always broke.
  They raided a Corporation Pandora lab site for the Beetlejuice
  stock — which explains the price. Stolen goods move fast
  or they don't move at all.""")

    if _stat(character, "perception") >= 1:
        print("""
  [You also heard something else. Vex has done this before —
   found a buyer, set a meet, taken the credits, never delivered.
   The last trader who dealt with him hasn't been seen on Agrica since.
   Could be coincidence. Probably isn't.]""")

    if _stat(character, "agility") >= 1:
        print("""
  [Trailing a Punkbuster back toward the spaceport, you catch
   them talking to someone on another freighter. Port logs show
   that ship departing tomorrow at first light. Whatever Vex is
   planning, he wants to be gone before you figure it out.]""")

    print("\n  Your nose stops bleeding somewhere around the third alley.")
    print("  Worth it. Probably.")

    ch = _choice([
        ("1", "Push forward. Meet Vex tonight."),
        ("9", "Too much risk. Walk away and cut losses."),
        ("0", "Back to the promenade for now."),
    ])

    if ch == "9":
        character["easy_job_token"] -= 1
        print("\n  You fold the intel and walk. Smart money. The token is burned.")
        _pause()
        return "promenade"

    if ch == "0":
        return "promenade"

    if _is_dead(exphp):
        return _ej05(ship, character)

    return _ejx02(ship, character, state, exphp)


def _ejx02(ship, character, state, exphp):
    """The meet. It goes wrong."""
    _print_header("Outside the City Walls — Night")

    print("""
  The spaceport lights bleed into the sky behind you, orange
  against the dark. The jungle starts ten metres past the last
  fence post and it is immediately, aggressively alive —
  insects the size of your fist, something large moving in
  the canopy, the wet rot smell of things eating other things.

  Vex arrives with five people and enough hardware to suggest
  this was never a trade. The boxes are there. So are the guns,
  pointed at you before anyone says hello.

  "Good to see you made it," Vex starts. "Thought you might
  chicken out."

  "I came for the drugs," you say.

  "Yeah, about that." He smiles. The crew fans out. "I found
  a better deal — I take your credits and ship the product
  myself. Saves me a middleman. Give me the money and walk,
  and nobody has a bad night."

  The police would love this story. Unfortunately, explaining
  the Beetlejuice would be complicated.

  What do you do?""")

    if _has(character, "bodyguard"):
        print("""
  [Your bodyguard shifts weight behind you. Not alarmed. Just ready.]""")

    ch = _choice([
        ("1", "Hand it over. 5,000 credits. No trouble."),
        ("2", "Run. Jungle first, questions later."),
        ("3", "Fight. You didn't come this far to be robbed."),
    ])

    if ch == "1":
        return _ejx02x01(ship, character)
    if ch == "2":
        return _ejx02x02(ship, character, state, exphp)
    if ch == "3":
        return _ejx02x03(ship, character, state, exphp)


def _ejx02x01(ship, character):
    """Surrender the money."""
    _print_header("The Smart Play")

    print("""
  You count out 5,000 credits and hold them out. Vex takes them
  without breaking eye contact, like he was expecting resistance
  and is slightly disappointed you didn't give him any.

  "Smart," he says. "Most people make it complicated."

  His crew melts back into the dark. You stand in the jungle
  with your dignity mostly intact and your wallet considerably
  lighter, listening to something large move in the canopy above.

  At least you still have the cantina.""")

    _end_mission(ship, {}, "surrendered", got_peppers=False, spent_credits=False)
    ship["credits"] -= 5000
    return "promenade"


def _ejx02x02(ship, character, state, exphp):
    """Run through the jungle."""
    _print_header("Into the Dark")

    print("""
  You break left and run.

  The jungle swallows you immediately — roots, mud, branches
  that grab at your jacket. Behind you, shouting, then shots.
  Something bright tears through the canopy overhead.
  You keep moving.""")

    agility  = _stat(character, "agility")
    raw_dmg  = max(0, 5 - agility)
    _take_damage(exphp, raw_dmg, "Gunfire and jungle in equal measure.")

    if _stat(character, "medicine") >= 1:
        heal_amt = _stat(character, "medicine")
        print(f"""
  You don't stop moving but your hands find the med kit by memory.
  Solid foam into the worst of it, a strip of fake skin, a stimulant
  that makes everything sharp and slightly wrong. It holds.""")
        _heal(exphp, heal_amt, f"Field dressing. +{heal_amt} HP from Medicine.")

    if _is_dead(exphp):
        print("""
  You made it far enough that they stopped shooting, but not far
  enough to matter. The jungle floor comes up hard.""")
        return _ej05(ship, character)

    print("""
  You come out the far side of the thicket bleeding and breathing
  hard, alone. The lights of the spaceport are visible through
  the trees. You have your credits. You don't have the drugs.

  Some nights you win. Tonight you escaped. On Agrica,
  that's close enough.""")

    _end_mission(ship, character, "ran", got_peppers=False)
    return "promenade"


def _ejx02x03(ship, character, state, exphp):
    """Fight."""
    _print_header("Law of the Jungle")

    print("""
  You don't answer. You move.

  The first shot goes wide. You're already behind a fallen trunk,
  the bark wet and soft and smelling of rot. Your pistol finds
  a hand in the muzzle flash.""")

    if _has(character, "bodyguard"):
        print("""
  Your bodyguard doesn't hesitate. A minigun appears from under
  a trenchcoat — you had no idea — and begins explaining the
  situation to the Punkbusters in considerable detail.
  Local wildlife evacuates the area at speed.""")

    power = _stat(character, "power")

    if power >= 2:
        dmg = max(0, 4 - power)
        if dmg > 0:
            _take_damage(exphp, dmg, "You took hits. You gave more.")
        else:
            print("\n  You took no hits. The Punkbusters took all of them.")

        print("""
  Vex's crew isn't trained for this. They were expecting compliance,
  not a firefight. One by one they stop shooting.
  Vex is the last one standing, and then he isn't.""")

        return _ejx03(ship, character, state, exphp)

    else:
        _take_damage(exphp, 3, "Outgunned. Too many of them.")
        print("""
  Five armed people was too many. You knew it before you started.
  The mud comes up slow and the jungle gets louder.""")

        if _is_dead(exphp):
            return _ej05(ship, character)
        return _ej05(ship, character)


def _ejx03(ship, character, state, exphp):
    """Upper hand — player won the fight."""
    _print_header("Upper Hand")

    print(f"""
  {_hp_bar(exphp)}

  Vex is on the ground, breathing but not arguing about it.
  His crew is gone — into the jungle or just gone. The boxes
  of Beetlejuice are sitting in the mud exactly where they
  were when this started.

  "Alright," he says, spitting something dark. "Alright.
  Take the product. We can still do this deal."

  Now he wants to trade. Could have started there.""")

    ch = _choice([
        ("1", "Deal is a deal. Take the product, pay 5,000 cr."),
        ("2", "Cover my medical expenses. Take the product, keep the credits."),
        ("3", "I'm done with you. Walk away — no product, no credits lost."),
        ("4", "No loose ends. Take the product. Vex doesn't leave the jungle."),
    ])

    if ch == "1":
        return _ejx03x01(ship, character)
    if ch == "2":
        return _ejx03x02(ship, character)
    if ch == "3":
        return _ejx03x03(ship, character)
    if ch == "4":
        return _ejx03x04(ship, character)


def _ejx03x01(ship, character):
    """Honour the deal."""
    _print_header("A Deal's a Deal")

    print("""
  You count out 5,000 credits and drop them in the mud next to him.

  "Take it," you say. "We're done."

  You collect the 20 bags and don't look back. The jungle
  closes behind you. By the time you reach the spaceport fence,
  your hands have stopped shaking.

  The Nexus market will make this worth it.""")

    _end_mission(ship, character, "success_paid", got_peppers=True)
    return "promenade"


def _ejx03x02(ship, character):
    """Keep the credits — medical compensation."""
    _print_header("Medical Expenses")

    print("""
  "You tried to rob me," you say. "And then I got shot at.
  Consider the credits compensation for the inconvenience."

  Vex opens his mouth. You look at him.
  He closes it again.

  You pick up the boxes. All 20 bags. You walk back toward
  the spaceport lights without hurrying. Behind you, the jungle
  makes its usual noises.

  The credits stay in your pocket. The product goes in your hold.
  Fair outcome.""")

    _end_mission(ship, character, "success_free", got_peppers=True)
    return "promenade"


def _ejx03x03(ship, character):
    """Walk away."""
    _print_header("Not Worth It")

    print("""
  You look at the boxes. You look at Vex bleeding in the mud.
  You look at the jungle and the lights of the spaceport in
  the distance.

  "Keep it," you say.

  You walk. Empty-handed, unshot, in possession of all your
  credits and most of your dignity. The Punkbusters can sell
  the Beetlejuice to someone else or rot out here.
  Either way, not your problem anymore.""")

    _end_mission(ship, character, "walked", got_peppers=False)
    return "promenade"


def _ejx03x04(ship, character):
    """Kill Vex."""
    _print_header("No Loose Ends")

    print("""
  "Look who got busted," you say.

  Vex stares up at you. Still trying to calculate angles.

  "Here's the calculation," you tell him. "I need the product.
  I need to not have someone out here who knows my face and
  has a reason to use it. I don't need you."

  You make it quick. The jungle absorbs the sound like it
  absorbs everything else — without judgment, without memory.

  You collect all 20 bags and walk back to the spaceport.
  The bartender at The Paprika Den pours you something
  without being asked. You drink it without tasting it.""")

    _end_mission(ship, character, "success_kill", got_peppers=True)
    return "promenade"


def _ej05(ship, character):
    """Bleed out — bad ending."""
    _print_header("Bleeding Out")

    print("""
  You lost track of how you got here.

  At some point the mud stopped being something you were
  running through and started being something you were
  lying in. The jungle is very loud. Your credits are gone.
  The drugs were never yours to begin with.

  You crawl back to the spaceport the way wounded things
  do — slowly, without dignity, grateful for every metre.

  The bartender at The Paprika Den finds you at the door.
  She doesn't ask questions. She gives you a drink and an
  ice pack and sits with you while the stimulants wear off.

  Free drink, at least. On Agrica, that's something.""")

    # Check if credits can cover the loss
    loss = min(5000, ship["credits"])
    ship["credits"] -= loss
    print(f"\n  −{loss:,} cr. What they could take, they took.")

    _pause()
    return "promenade"


# ── ENTRY POINT ───────────────────────────────────────────────

def run_easy_job(ship, character, state):
    """
    Entry point called from expedition center in game.py.
    Returns when mission ends (any outcome).
    Modifies ship and character in place.
    """
    # Entry credit check
    if ship["credits"] < 5000:
        print("\n  You need 5,000 credits to seal the deal with Vex.")
        print("  He won't move product for someone who can't pay up front.")
        _pause()
        return

    # Consume token
    character["easy_job_token"] -= 1

    # Generate mission HP from health stat
    max_hp = character["stats"]["health"]
    exphp  = [max_hp, max_hp]

    print(f"\n  Mission HP: {_hp_bar(exphp)}")
    print(f"  Power: {_stat(character,'power')}  "
          f"Agility: {_stat(character,'agility')}  "
          f"Medicine: {_stat(character,'medicine')}  "
          f"Perception: {_stat(character,'perception')}")
    _pause()

    # Run the graph
    node = _ejx01(ship, character, state, exphp)
    # node return value is always "promenade" — caller returns to promenade
