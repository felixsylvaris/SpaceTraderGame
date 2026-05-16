# =============================================================
#  SPICE SPACE TRADER — data/blackjack.py
#  Blackjack mini-game. Called from cantina in game.py.
#  Entry point: play_blackjack(ship, state)
#  No imports from game.py or parameters.py — fully self-contained.
# =============================================================

import random

# ── OPPONENTS ─────────────────────────────────────────────────

OPPONENTS = {
    "Skittish Tom": {
        "threshold":  15,    # stands when total > threshold (i.e. at 16+)
        "entry":     500,    # minimum credits to sit down
        "limit":     500,    # maximum bet
        "intro":     "Skittish Tom eyes you nervously over his cards. He folds early and often.",
        "win_text":  "Tom slams his cards down. 'Rigged!' he mutters, sliding his credits over.",
        "lose_text": "Tom exhales slowly. 'Didn't think you'd fold so easy.' He pockets your credits.",
        "bust_text": "Tom groans and throws his cards across the table. 'Every time!'",
    },
    "Mad Alice": {
        "threshold":  18,
        "entry":    1000,
        "limit":    1000,
        "intro":     "Mad Alice grins at you with too many teeth. She plays reckless and loves it.",
        "win_text":  "Alice laughs like it's all a joke. 'Good hand. Next round I'll have you.'",
        "lose_text": "Alice slaps the table. 'Yes! That's what I'm talking about!' She sweeps your bet.",
        "bust_text": "Alice stares at her cards. 'How. HOW.' She shoves the pot toward you.",
    },
    "Lucky \"Ace\" Jack": {
        "threshold":  17,
        "entry":    2000,
        "limit":    2000,
        "intro":     "Lucky Ace Jack tips his hat. He always draws the Ace of Spades first. Always.",
        "win_text":  "Jack sets his cards down quietly. 'Well played.' He pays without complaint.",
        "lose_text": "Jack smiles. 'Luck favours the prepared.' He counts your credits methodically.",
        "bust_text": "Jack blinks at his hand, then at you. 'That... doesn't happen.' He pays up.",
        "special":   "ace_of_spades",
    },
}

# ── DECK ──────────────────────────────────────────────────────

SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
VALUES = {
    "2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,
    "J":10,"Q":10,"K":10,"A":11,
}

def _build_deck():
    return [{"rank": r, "suit": s} for s in SUITS for r in RANKS]

def _shuffle(deck):
    random.shuffle(deck)
    return deck

def _card_str(card):
    return f"{card['rank']}{card['suit']}"

def _hand_str(hand):
    return "  ".join(_card_str(c) for c in hand)

def _total(hand):
    """Calculate best hand total. Aces count 11, drop to 1 if bust."""
    total = sum(VALUES[c["rank"]] for c in hand)
    aces  = sum(1 for c in hand if c["rank"] == "A")
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total

def _is_bust(hand):
    return _total(hand) > 21

# ── DISPLAY ───────────────────────────────────────────────────

def _print_table(player_hand, opp_hand, opp_name, hide_opp=True):
    print()
    print(f"  {'─'*44}")
    if hide_opp:
        shown = _card_str(opp_hand[0]) + "  [hidden]"
        print(f"  {opp_name:<20}  {shown}")
    else:
        print(f"  {opp_name:<20}  {_hand_str(opp_hand)}  (total: {_total(opp_hand)})")
    print(f"  {'─'*44}")
    print(f"  {'You':<20}  {_hand_str(player_hand)}  (total: {_total(player_hand)})")
    print(f"  {'─'*44}")

# ── PLAYER TURN ───────────────────────────────────────────────

def _player_turn(deck, player_hand, opp_hand, opp_name):
    """Player hits or stands. Returns False if bust."""
    while True:
        _print_table(player_hand, opp_hand, opp_name, hide_opp=True)
        total = _total(player_hand)
        if total == 21:
            print("  Blackjack! Standing automatically.")
            return True
        print(f"  [h] Hit   [s] Stand")
        ch = input("  Your move: ").strip().lower()
        if ch == "h":
            card = deck.pop()
            player_hand.append(card)
            print(f"  You draw: {_card_str(card)}")
            if _is_bust(player_hand):
                _print_table(player_hand, opp_hand, opp_name, hide_opp=True)
                print(f"  Bust! Total: {_total(player_hand)}")
                return False
        elif ch == "s":
            return True
        else:
            print("  Hit [h] or Stand [s].")

# ── DOUBLE DOWN ───────────────────────────────────────────────

def _offer_double(ship, bet):
    """Offer player the chance to double their bet. Returns new bet."""
    if ship["credits"] < bet:
        print("  (You can't afford to double.)")
        return bet
    print(f"\n  Double down? Your bet goes from {bet:,} to {bet*2:,} cr.")
    print(f"  You have {ship['credits']:,} cr.  [y] Double  [n] Keep bet")
    ch = input("  ").strip().lower()
    if ch == "y":
        ship["credits"] -= bet
        print(f"  Bet doubled to {bet*2:,} cr.")
        return bet * 2
    return bet

def _ai_doubles(deck, opp_hand, total_after_stand, opp_name):
    """
    AI doubles based on their standing total.
    21 → up to 3 doubles, 19+ → up to 2, 17+ → up to 1.
    Each double = draw 1 card + double their side stake (tracked separately).
    Returns (final_hand, ai_stake_multiplier).
    """
    if total_after_stand == 21:
        max_doubles = 3
    elif total_after_stand >= 19:
        max_doubles = 2
    elif total_after_stand >= 17:
        max_doubles = 1
    else:
        max_doubles = 0

    multiplier = 1
    for _ in range(max_doubles):
        if _is_bust(opp_hand): break
        print(f"  {opp_name} doubles down and draws a card...")
        card = deck.pop()
        opp_hand.append(card)
        multiplier *= 2
        print(f"  {opp_name} draws: {_card_str(card)}  (total: {_total(opp_hand)})")
        if _is_bust(opp_hand):
            print(f"  {opp_name} busts on the double!")
            break

    return multiplier

# ── AI TURN ───────────────────────────────────────────────────

def _ai_turn(deck, opp_hand, opp_name, threshold):
    """AI hits until total > threshold or busts."""
    print(f"\n  {opp_name} plays...")
    while _total(opp_hand) <= threshold:
        card = deck.pop()
        opp_hand.append(card)
        print(f"  {opp_name} draws: {_card_str(card)}  (total: {_total(opp_hand)})")
        if _is_bust(opp_hand):
            return False
    print(f"  {opp_name} stands at {_total(opp_hand)}.")
    return True

# ── SINGLE ROUND ──────────────────────────────────────────────

def _play_round(ship, opp_name, opp_data):
    """
    Play one round of blackjack.
    Returns: "win", "lose", "push", "quit"
    """
    # ── Bet ──
    limit    = opp_data["limit"]
    entry    = opp_data["entry"]
    max_bet  = min(limit, ship["credits"])
    print(f"\n  Bet between {entry:,} and {max_bet:,} cr.  [0] Walk away")
    while True:
        raw = input("  Your bet: ").strip()
        if raw == "0": return "quit"
        try:
            bet = int(raw)
        except ValueError:
            print("  Enter a number."); continue
        if bet < entry:
            print(f"  Minimum bet is {entry:,} cr."); continue
        if bet > max_bet:
            print(f"  Maximum bet is {max_bet:,} cr."); continue
        break

    ship["credits"] -= bet
    print(f"  Bet placed: {bet:,} cr.  Remaining: {ship['credits']:,} cr.")

    # ── Build deck ──
    deck = _shuffle(_build_deck())

    # ── Deal — Lucky Ace Jack gets Ace of Spades first ──
    player_hand = []
    opp_hand    = []

    if opp_data.get("special") == "ace_of_spades":
        ace = next(c for c in deck if c["rank"] == "A" and c["suit"] == "♠")
        deck.remove(ace)
        opp_hand.append(ace)

    # Standard two-card deal alternating
    for _ in range(2):
        player_hand.append(deck.pop())
        if len(opp_hand) < 2:
            opp_hand.append(deck.pop())

    # ── Player turn ──
    player_ok = _player_turn(deck, player_hand, opp_hand, opp_name)

    if not player_ok:
        # Player busted — lose immediately
        print(f"\n  {opp_data['lose_text']}")
        return "lose"

    # ── Player double-down offer ──
    bet = _offer_double(ship, bet)

    # ── AI turn ──
    threshold = opp_data["threshold"]
    ai_ok     = _ai_turn(deck, opp_hand, opp_name, threshold)

    # ── AI doubles ──
    ai_multiplier = 1
    if ai_ok and not _is_bust(opp_hand):
        ai_multiplier = _ai_doubles(deck, opp_hand, _total(opp_hand), opp_name)

    # ── Reveal & resolve ──
    print()
    _print_table(player_hand, opp_hand, opp_name, hide_opp=False)

    player_total = _total(player_hand)
    opp_total    = _total(opp_hand)

    if not ai_ok or _is_bust(opp_hand):
        print(f"\n  {opp_data['bust_text']}")
        # AI busted — player wins. AI multiplier inflates their loss too.
        winnings = bet + int(bet * ai_multiplier)
        ship["credits"] += winnings
        print(f"  +{winnings:,} cr  (your {bet:,} back + their {int(bet*ai_multiplier):,})")
        return "win"
    elif player_total > opp_total:
        print(f"\n  {opp_data['win_text']}")
        winnings = bet + int(bet * ai_multiplier)
        ship["credits"] += winnings
        print(f"  +{winnings:,} cr  (your {bet:,} back + their {int(bet*ai_multiplier):,})")
        return "win"
    elif opp_total > player_total:
        print(f"\n  {opp_data['lose_text']}")
        # bet already deducted — nothing returned
        print(f"  -{bet:,} cr")
        return "lose"
    else:
        print(f"\n  Push — it's a tie. Bet returned.")
        ship["credits"] += bet
        return "push"

# ── MAIN ENTRY ────────────────────────────────────────────────

def play_blackjack(ship, state):
    """
    Entry point called from cantina in game.py.
    Modifies ship["credits"] and state["blackjack_tokens"] in place.
    """
    tokens = state.get("blackjack_tokens", 3)

    while True:
        print(f"\n── GAME TABLE  ──────────────────────────────────────")
        print(f"  Credits : {ship['credits']:,}")
        print(f"  Tokens  : {tokens}  (win a game to spend one; 0 = locals won't play you)")
        print()

        if tokens <= 0:
            print("  Word travels fast. Nobody here will play you anymore.")
            print("  Move to another planet to find fresh opponents.")
            input("  [Enter to leave...]")
            state["blackjack_tokens"] = tokens
            return

        # List available opponents (need entry credits)
        available = [(name, data) for name, data in OPPONENTS.items()
                     if ship["credits"] >= data["entry"]]

        print("  Opponents:")
        for i, (name, data) in enumerate(OPPONENTS.items(), 1):
            affordable = ship["credits"] >= data["entry"]
            lock       = "" if affordable else f"  [need {data['entry']:,} cr to sit]"
            print(f"  [{i}] {name:<22} entry {data['entry']:,}cr  limit {data['limit']:,}cr{lock}")
        print("  [0] Leave table")
        print()

        ch = input("  Choose opponent: ").strip()
        if ch == "0" or ch.lower() == "q":
            state["blackjack_tokens"] = tokens
            return

        try:
            idx = int(ch) - 1
            if idx < 0 or idx >= len(OPPONENTS):
                raise ValueError
        except ValueError:
            print("  Invalid choice."); continue

        opp_name, opp_data = list(OPPONENTS.items())[idx]

        if ship["credits"] < opp_data["entry"]:
            print(f"  You need at least {opp_data['entry']:,} cr to play {opp_name}.")
            continue

        # Intro
        print(f"\n  {opp_data['intro']}")
        print()

        result = _play_round(ship, opp_name, opp_data)

        if result == "win":
            tokens -= 1
            print(f"\n  Token spent. Tokens remaining: {tokens}")
            if tokens <= 0:
                print("  The table goes cold. You've cleaned out the locals.")
                print("  Move to another planet.")
                input("  [Enter...]")
                state["blackjack_tokens"] = tokens
                return
        elif result == "quit":
            state["blackjack_tokens"] = tokens
            return

        # After each round ask to continue
        print(f"\n  Credits: {ship['credits']:,}  |  Tokens: {tokens}")
        again = input("  Play again? [y/n]: ").strip().lower()
        if again != "y":
            state["blackjack_tokens"] = tokens
            return

    state["blackjack_tokens"] = tokens
