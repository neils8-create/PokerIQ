import random

def evaluate_hand(cards):
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    ranks = [card[0] for card in cards]
    suits = [card[1] for card in cards]

    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    suit_counts = {suit: suits.count(suit) for suit in set(suits)}

    is_flush = max(suit_counts.values()) == 5
    sorted_ranks = sorted([rank_order.index(rank) for rank in ranks])
    is_straight = sorted_ranks == list(range(min(sorted_ranks), min(sorted_ranks) + 5))
    is_wheel_straight = sorted_ranks == [0, 1, 2, 3, 12] # A-2-3-4-5 straight

    if is_flush and sorted(ranks) == sorted(['T', 'J', 'Q', 'K', 'A']):
        return (9, []) # Royal Flush
    elif is_wheel_straight and is_flush:
        return (8, [max(sorted_ranks)]) # Wheel Straight Flush
    elif is_straight and is_flush:
        return (8, [max(sorted_ranks)]) # Straight Flush
    elif 4 in rank_counts.values():
        quad_rank = [rank_order.index(rank) for rank, count in rank_counts.items() if count == 4][0]
        kicker_value = [rank_order.index(rank) for rank, count in rank_counts.items() if count == 1][0]
        return (7, [quad_rank, kicker_value]) # Four of a Kind
    elif 3 in rank_counts.values() and 2 in rank_counts.values():
        trips_value = [rank_order.index(rank) for rank, count in rank_counts.items() if count == 3][0]
        pair_value = [rank_order.index(rank) for rank, count in rank_counts.items() if count == 2][0]
        return (6, [trips_value, pair_value]) # Full House
    elif is_flush:
        return (5, sorted(sorted_ranks, reverse = True)) # Flush
    elif is_straight or is_wheel_straight:
        return (4, [max(sorted_ranks)]) # Straight
    elif 3 in rank_counts.values():
        trips_value = [rank_order.index(rank) for rank, count in rank_counts.items() if count == 3][0]
        kickers = sorted([rank_order.index(rank) for rank, count in rank_counts.items() if count == 1], reverse=True)
        return (3, [trips_value] + kickers) # Three of a Kind
    elif list(rank_counts.values()).count(2) == 2:
        sorted_by_freq = sorted(sorted_ranks, key = lambda v: (sorted_ranks.count(v), v), reverse = True)
        return (2, sorted_by_freq) # Two Pair
    elif 2 in rank_counts.values():
        sorted_by_freq = sorted(sorted_ranks, key = lambda v: (sorted_ranks.count(v), v), reverse = True)
        return (1, sorted_by_freq) # One Pair
    else:
        return (0, sorted(sorted_ranks, reverse=True)) # High Card
    
def get_five_card_combinations(cards):
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            for k in range(j + 1, len(cards)):
                for l in range(k + 1, len(cards)):
                    for m in range(l + 1, len(cards)):
                        yield [cards[i], cards[j], cards[k], cards[l], cards[m]]

def best_hand(hole_cards, board):
    all_cards = hole_cards + board
    best_rank = (0, [])
    for combination in get_five_card_combinations(all_cards):
        rank = evaluate_hand(combination)
        if rank > best_rank:
            best_rank = rank
    return best_rank

def deal_random_board(remaining_deck):
    board = random.sample(remaining_deck, 5)
    return board

def build_deck():
    deck = []
    suits = ['s', 'h', 'd', 'c']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    for suit in suits:
        for rank in ranks:
            card = rank + suit
            deck.append(card)
    return deck

def calculate_equity(hole_p1, hole_p2, num_simulations = 10000):
    p1_wins = 0
    p2_wins = 0
    ties = 0
    for i in range(num_simulations):
        deck = build_deck()
        remaining_deck = [card for card in deck if card not in hole_p1 + hole_p2]
        board = deal_random_board(remaining_deck)
        
        rank_p1 = best_hand(hole_p1, board)
        rank_p2 = best_hand(hole_p2, board)

        if rank_p1 > rank_p2:
            p1_wins += 1
        elif rank_p2 > rank_p1:
            p2_wins += 1
        else:
            p1_wins += 0.5
            p2_wins += 0.5
    total = num_simulations
    p1_equity = p1_wins / total * 100
    p2_equity = p2_wins / total * 100

    print(f'Player 1 equity: {p1_equity:.1f}%')
    print(f'Player 2 equity: {p2_equity:.1f}%')

    return {'p1': p1_equity, 'p2': p2_equity}

def calculate_equity_single(hole_cards, num_players, num_simulations=10000, known_board=[]):
    wins = 0
    for i in range(num_simulations):
        deck = build_deck()
        remaining_deck = [card for card in deck if card not in hole_cards + known_board]

        temp_deck = remaining_deck.copy()
        opponents = []
        for j in range(num_players - 1):
            opponent_cards = random.sample(temp_deck, 2)
            opponents.append(opponent_cards)
            temp_deck = [card for card in temp_deck if card not in opponent_cards]

        # fill out the rest of the board randomly
        cards_needed = 5 - len(known_board)
        random_board = random.sample(temp_deck, cards_needed)
        board = known_board + random_board

        your_rank = best_hand(hole_cards, board)
        you_win = all(your_rank > best_hand(opp, board) for opp in opponents)

        if you_win:
            wins += 1

    return wins / num_simulations * 100