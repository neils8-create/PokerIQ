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

def evaluate_opponents(hole_cards, board, remaining_deck, num_players, num_opponent_samples=1000):
    results = {'wins': 0, 'ties': 0, 'losses': 0}
    your_rank = best_hand(hole_cards, board)

    if num_players == 2:
        # exact — enumerate all 990 possible opponent hands
        for opp_combo in itertools.combinations(remaining_deck, 2):
            opp_rank = best_hand(list(opp_combo), board)
            if your_rank > opp_rank:
                results['wins'] += 1
            elif your_rank == opp_rank:
                results['ties'] += 1
            else:
                results['losses'] += 1

    elif num_players == 3:
        # exact — enumerate all opponent hand combinations
        for opp1 in itertools.combinations(remaining_deck, 2):
            deck_after_opp1 = [c for c in remaining_deck if c not in opp1]
            for opp2 in itertools.combinations(deck_after_opp1, 2):
                best_opp = max(best_hand(list(opp1), board), best_hand(list(opp2), board))
                if your_rank > best_opp:
                    results['wins'] += 1
                elif your_rank == best_opp:
                    results['ties'] += 1
                else:
                    results['losses'] += 1

    else:
        # monte carlo — sample random opponent hands
        for _ in range(num_opponent_samples):
            temp_deck = remaining_deck.copy()
            opponents = []
            for j in range(num_players - 1):
                opp_cards = random.sample(temp_deck, 2)
                opponents.append(opp_cards)
                temp_deck = [c for c in temp_deck if c not in opp_cards]
            best_opp = max(best_hand(opp, board) for opp in opponents)
            if your_rank > best_opp:
                results['wins'] += 1
            elif your_rank == best_opp:
                results['ties'] += 1
            else:
                results['losses'] += 1

    return results

def run_exact_enumeration(hole_cards, num_players, known_board):

    if len(known_board) < 3:
        return None

    deck = build_deck()
    remaining_deck = [card for card in deck if card not in hole_cards + known_board]
    results = {'wins': 0, 'ties': 0, 'losses': 0}

    if len(known_board) == 5:
        # river — no board cards to enumerate, just evaluate opponents
        opp_results = evaluate_opponents(hole_cards, known_board, remaining_deck, num_players)
        results['wins'] += opp_results['wins']
        results['ties'] += opp_results['ties']
        results['losses'] += opp_results['losses']

    else:
        # turn or flop — enumerate every possible board completion
        cards_needed = 5 - len(known_board)
        for combo in itertools.combinations(remaining_deck, cards_needed):
            board = known_board + list(combo)
            opp_deck = [card for card in remaining_deck if card not in combo]
            opp_results = evaluate_opponents(hole_cards, board, opp_deck, num_players)
            results['wins'] += opp_results['wins']
            results['ties'] += opp_results['ties']
            results['losses'] += opp_results['losses']

    total = results['wins'] + results['ties'] + results['losses']
    win_pct = (results['wins'] + results['ties'] * 0.5) / total * 100
    tie_pct = results['ties'] / total * 100
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

def calculate_street_equities(hole_cards, num_players, known_board, num_simulations=10000):
    streets = ['Pre-flop']
    equities = []

    # always calculate pre-flop
    preflop = run_monte_carlo(hole_cards, num_players, num_simulations, known_board=[])
    equities.append(preflop['win_pct'])

    # flop — monte carlo with first 3 board cards
    if len(known_board) >= 3:
        flop = run_monte_carlo(hole_cards, num_players, num_simulations, known_board[:3])
        streets.append('Flop')
        equities.append(flop['win_pct'])

    # turn — exact enumeration with first 4 board cards
    if len(known_board) >= 4:
        turn = run_exact_enumeration(hole_cards, num_players, known_board[:4])
        streets.append('Turn')
        equities.append(turn['win_pct'])

    # river — exact enumeration with all 5 board cards
    if len(known_board) == 5:
        river = run_exact_enumeration(hole_cards, num_players, known_board)
        streets.append('River')
        equities.append(river['win_pct'])

    return {'streets': streets, 'equities': equities}


# Turn test — 2 players, should be 46 × 990 = 45,540 total
result4 = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s'])
print(f'Turn exact win %: {result4["win_pct"]:.2f}%')
print(f'Turn total evaluations: {result4["total"]}')

# River test — 2 players, should be 990 total
result3 = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s', '3d'])
print(f'River exact win %: {result3["win_pct"]:.2f}%')
print(f'River total evaluations: {result3["total"]}')

# 3 player river test
result5 = run_exact_enumeration(['As', 'Ah'], 3, ['Kd', '7c', '2h', '9s', '3d'])
print(f'3-player river exact win %: {result5["win_pct"]:.2f}%')

result = run_monte_carlo(['As', 'Ah'], 2)
print(f'Win %: {result["win_pct"]:.1f}%')
print('Hand type counts:', result['hand_type_counts'])
print('Equity progression length:', len(result['equity_progression']))
print('First 5 progression values:', result['equity_progression'][:5])
print('Last 5 progression values:', result['equity_progression'][-5:])