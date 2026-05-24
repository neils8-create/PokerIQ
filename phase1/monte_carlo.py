import random
import itertools
from hand_evaluator import build_deck, best_hand

HAND_NAMES = {
    0: 'High Card',
    1: 'One Pair',
    2: 'Two Pair',
    3: 'Three of a Kind',
    4: 'Straight',
    5: 'Flush',
    6: 'Full House',
    7: 'Four of a Kind',
    8: 'Straight Flush',
    9: 'Royal Flush'
}

def run_monte_carlo(hole_cards, num_players, num_simulations = 50000, known_board = []):
    wins = 0
    hand_type_counts = {name: 0 for name in HAND_NAMES.values()}
    opponent_hand_type_counts = {name: 0 for name in HAND_NAMES.values()}
    equity_progression = []
    results = {'wins': 0, 'ties': 0, 'losses': 0}

    for i in range(num_simulations):
        # build deck and remove known cards

        deck = build_deck()
        remaining_deck = [card for card in deck if card not in hole_cards + known_board]

        # deal opponent hands
        temp_deck = remaining_deck.copy()
        opponents = []
        for j in range(num_players - 1):
            opponent_cards = random.sample(temp_deck, 2)
            opponents.append(opponent_cards)
            temp_deck = [card for card in temp_deck if card not in opponent_cards]

        # fill out the board randomly

        cards_needed = 5 - len(known_board)
        random_board = random.sample(temp_deck, cards_needed)
        board = known_board + random_board

        # evaluate your best hand
        your_rank = best_hand(hole_cards, board)  
        hand_name = HAND_NAMES[your_rank[0]]
        hand_type_counts[hand_name] += 1

        # check if you beat all opponents
        best_opponent = max(best_hand(opp, board) for opp in opponents)
        opponent_hand_name = HAND_NAMES[best_opponent[0]]
        opponent_hand_type_counts[opponent_hand_name] += 1

        if your_rank > best_opponent:
            results['wins'] += 1
        elif your_rank == best_opponent:
            results['ties'] += 1
        else:
            results['losses'] += 1

        # every 100 simulations, record current equity estimate
        if i % 100 == 0:
            current_equity = (results['wins'] + results['ties'] * 0.5) / (i + 1) * 100
            equity_progression.append(current_equity)

    total = num_simulations
    win_pct = (results['wins'] + results['ties'] * 0.5) / total * 100
    loss_pct = (results['losses'] + results['ties'] * 0.5) / total * 100
    tie_pct = results['ties'] / total * 100

    return {
        'win_pct': win_pct,
        'loss_pct': loss_pct,
        'tie_pct': tie_pct,
        'wins': results['wins'],
        'ties': results['ties'],
        'losses': results['losses'],
        'hand_type_counts': hand_type_counts,
        'equity_progression': equity_progression,
        'opponent_hand_type_counts': opponent_hand_type_counts
    }

def run_exact_enumeration(hole_cards, num_players, known_board):

    if len(known_board) < 3:
        return None

    deck = build_deck()
    remaining_deck = [card for card in deck if card not in hole_cards + known_board]

    cards_needed = 5 - len(known_board)

    results = {'wins': 0, 'ties': 0, 'losses': 0}

    for combo in itertools.combinations(remaining_deck, cards_needed):
        board = known_board + list(combo)

        opp_deck = [card for card in remaining_deck if card not in combo]
        temp_deck = opp_deck.copy()
        opponents = []
        for j in range(num_players - 1):
            opponent_cards = random.sample(temp_deck, 2)
            opponents.append(opponent_cards)
            temp_deck = [card for card in temp_deck if card not in opponent_cards]

        your_rank = best_hand(hole_cards, board)

        best_opponent = max(best_hand(opp, board) for opp in opponents)

        if your_rank > best_opponent:
            results['wins'] += 1
        elif your_rank == best_opponent:
            results['ties'] += 1
        else:
            results['losses'] += 1

    # 11 — calculate final percentages
    total = results['wins'] + results['ties'] + results['losses']
    win_pct = (results['wins'] + results['ties'] * 0.5) / total * 100
    tie_pct = (results['ties']) / total * 100
    loss_pct = (results['losses'] + results['ties'] * 0.5) / total * 100

    return {
        'win_pct': win_pct,
        'tie_pct': tie_pct,
        'loss_pct': loss_pct,
        'wins': results['wins'],
        'ties': results['ties'],
        'losses': results['losses'],
        'total': total
    }

result = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h'])
print(f'Exact win %: {result["win_pct"]:.2f}%')
print(f'Ties: {result["ties"]}')
print(f'Total boards evaluated: {result["total"]}')

# After turn — should evaluate exactly 46 boards
result2 = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s'])
print(f'Exact win %: {result2["win_pct"]:.2f}%')
print(f'Total boards evaluated: {result2["total"]}')



result = run_monte_carlo(['As', 'Ah'], 2)
print(f'Win %: {result["win_pct"]:.1f}%')
print('Hand type counts:', result['hand_type_counts'])
print('Equity progression length:', len(result['equity_progression']))
print('First 5 progression values:', result['equity_progression'][:5])
print('Last 5 progression values:', result['equity_progression'][-5:])