import random

# Card deck setup
suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10,
          'J':10, 'Q':10, 'K':10, 'A':11}

# AI Profiles and Bankrolls
ai_profiles = {
    "Skittish Tom": {"threshold": 15, "bankroll": 500},
    "Mad Alice": {"threshold": 18, "bankroll": 1000},
    "Lucky Ace Juck": {"threshold": 17, "bankroll": 2000},
}

# Initialize deck
def initialize_deck():
    return [{'rank': rank, 'suit': suit, 'value': values[rank]}
            for suit in suits for rank in ranks]

# Shuffle deck
def shuffle_deck(deck):
    random.shuffle(deck)

# Deal initial cards
def deal_initial(deck, hands):
    for _ in range(2):
        for hand in hands:
            hand.append(deck.pop())

# Calculate hand total (handle Aces)
def calculate_total(hand):
    total = sum(card['value'] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

# Player turn
def player_turn(deck, hand):
    while True:
        print(f"\nYour hand: {[f\"{card['rank']} of {card['suit']}\" for card in hand]} (Total: {calculate_total(hand)})")
        action = input("Hit (H) or Stand (S)? ").upper()
        if action == 'H':
            hand.append(deck.pop())
            if calculate_total(hand) > 21:
                print("Bust! You lose.")
                return False
        elif action == 'S':
            return True

# AI turn
def ai_turn(deck, hand, profile_name):
    threshold = ai_profiles[profile_name]["threshold"]
    while calculate_total(hand) <= threshold:
        hand.append(deck.pop())
        if calculate_total(hand) > 21:
            print(f"{profile_name} busts!")
            return False
    print(f"{profile_name} stands on {calculate_total(hand)}.")
    return True

# Special handling for Lucky Ace Juck
def setup_lucky_ace_juck(deck, ai_hands):
    ace_of_spades = next(card for card in deck if card['rank'] == 'A' and card['suit'] == 'Spades')
    deck.remove(ace_of_spades)
    ai_hands["Lucky Ace Juck"].append(ace_of_spades)

# Determine winner
def determine_winner(hands, ai_hands, bets, player_bankroll, ai_bankrolls):
    all_hands = {"Player": hands} | ai_hands
    results = {}
    for name, hand in all_hands.items():
        results[name] = calculate_total(hand)

    max_total = max(total for total in results.values() if total <= 21)
    winners = [name for name, total in results.items() if total == max_total and total <= 21]

    if not winners:
        print("Everyone busted! No winner.")
        return player_bankroll, ai_bankrolls

    for winner in winners:
        if winner == "Player":
            player_bankroll += sum(bets.values())
        else:
            ai_bankrolls[winner] += bets[winner] * 2  # Win = bet * 2 (original bet + opponent's bet)

    if len(winners) == 1:
        print(f"{winners[0]} wins with {max_total}!")
    else:
        print(f"It's a tie between {', '.join(winners)} with {max_total}!")

    return player_bankroll, ai_bankrolls

# Place bets
def place_bets(player_bankroll, ai_bankrolls, active_ais):
    bets = {}
    print(f"\nYour bankroll: {player_bankroll}")
    while True:
        try:
            player_bet = int(input("Place your bet: "))
            if player_bet > player_bankroll:
                print(f"You don't have enough credits. Max bet: {player_bankroll}")
                continue
            break
        except ValueError:
            print("Invalid input. Enter a number.")

    bets["Player"] = player_bet

    for ai in active_ais:
        ai_bet = min(random.randint(10, 100), ai_bankrolls[ai])
        bets[ai] = ai_bet
        print(f"{ai} bets {ai_bet}.")
        ai_bankrolls[ai] -= ai_bet

    player_bankroll -= player_bet
    return bets, player_bankroll, ai_bankrolls

# Main game loop
def play_blackjack():
    # Initialize bankrolls
    player_bankroll = 1000
    ai_bankrolls = {name: data["bankroll"] for name, data in ai_profiles.items()}

    while True:
        # Select opponents
        print("\nAvailable opponents:")
        for i, name in enumerate(ai_profiles.keys(), 1):
            print(f"{i}. {name} (Bankroll: {ai_bankrolls[name]})")
        selected = input("Choose opponents (e.g., 1,2,3 or 1 3): ").strip()
        active_ais = []
        for choice in selected.split():
            try:
                idx = int(choice) - 1
                active_ais.append(list(ai_profiles.keys())[idx])
            except (ValueError, IndexError):
                print(f"Invalid selection: {choice}. Skipping.")
        if not active_ais:
            print("No opponents selected. Exiting.")
            break

        # Initialize deck and hands
        deck = initialize_deck()
        shuffle_deck(deck)
        player_hand = []
        ai_hands = {name: [] for name in active_ais}

        # Special setup for Lucky Ace Juck
        if "Lucky Ace Juck" in active_ais:
            setup_lucky_ace_juck(deck, ai_hands)

        # Place bets
        bets, player_bankroll, ai_bankrolls = place_bets(player_bankroll, ai_bankrolls, active_ais)

        # Deal initial cards
        deal_initial(deck, [player_hand] + list(ai_hands.values()))

        # Check for Blackjack
        if calculate_total(player_hand) == 21:
            print("\nBlackjack! You win!")
            player_bankroll += sum(bets.values()) * 1.5  # Blackjack payout: 1.5x
            continue

        # Player turn
        if not player_turn(deck, player_hand):
            player_bankroll, ai_bankrolls = determine_winner(player_hand, ai_hands, bets, player_bankroll, ai_bankrolls)
            continue

        # AI turns
        for name in active_ais:
            print(f"\n{name}'s turn:")
            ai_turn(deck, ai_hands[name], name)

        # Determine winner
        player_bankroll, ai_bankrolls = determine_winner(player_hand, ai_hands, bets, player_bankroll, ai_bankrolls)

        # Display bankrolls
        print(f"\nYour bankroll: {player_bankroll}")
        for name in active_ais:
            print(f"{name}'s bankroll: {ai_bankrolls[name]}")

        # Play again?
        if input("\nPlay again? (Y/N): ").upper() != 'Y':
            break

# Start the game
play_blackjack()
