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

# ==============================================================================
# DRAW DETECTION HELPERS
# ==============================================================================

def count_flush_draw(hole_cards, board):
    all_cards = hole_cards + board
    if not all_cards:
        return 0
    suits = [card[1] for card in all_cards]
    suit_counts = {}
    for suit in suits:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1
    return max(suit_counts.values())

def count_straight_draw(hole_cards, board):
    all_cards = hole_cards + board
    if not all_cards:
        return 0
    RANK_TO_VALUE = {
        '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,
        'T':10, 'J':11, 'Q':12, 'K':13, 'A':14
    }
    values = set(RANK_TO_VALUE[card[0]] for card in all_cards)
    if 14 in values:
        values.add(1)
    sorted_vals = sorted(list(values))
    max_count = 0
    for low_rank in range(1, 11):
        high_rank = low_rank + 4
        count_in_window = sum(1 for v in sorted_vals if low_rank <= v <= high_rank)
        if count_in_window > max_count:
            max_count = count_in_window
    return max_count

def classify_draw_advancement(hole_cards, known_board, test_board):
    flush_before = count_flush_draw(hole_cards, known_board)
    straight_before = count_straight_draw(hole_cards, known_board)
    flush_after = count_flush_draw(hole_cards, test_board)
    straight_after = count_straight_draw(hole_cards, test_board)
    if flush_before == 3 and flush_after == 4:
        return True
    if straight_before == 3 and straight_after == 4:
        return True
    return False

# ==============================================================================
# OUTS CALCULATOR
# ==============================================================================

def calculate_outs(hole_cards, known_board, num_players=2, num_samples=100):
    if len(known_board) < 3:
        return None

    deck = build_deck()
    remaining_deck = [card for card in deck if card not in hole_cards + known_board]

    cards = []
    classifications = []

    for card in remaining_deck:
        test_board = known_board + [card]

        your_rank_with = best_hand(hole_cards, test_board)
        your_rank_without = best_hand(hole_cards, known_board)

        hand_improved = your_rank_with > your_rank_without
        hand_type_improved = your_rank_with[0] > your_rank_without[0]

        draw_advances = classify_draw_advancement(hole_cards, known_board, test_board)

        opp_improvement = 0
        for _ in range(num_samples):
            temp_deck = [c for c in remaining_deck if c != card]
            opp_cards = random.sample(temp_deck, 2)
            opp_rank_with = best_hand(opp_cards, test_board)
            opp_rank_without = best_hand(opp_cards, known_board)
            if opp_rank_with > opp_rank_without:
                opp_improvement += 1

        opp_improvement_rate = opp_improvement / num_samples

        if hand_type_improved:
            classifications.append('bright_green')
        elif draw_advances:
            classifications.append('yellow')
        elif hand_improved:
            classifications.append('green')
        elif opp_improvement_rate > 0.5 and not hand_improved:
            classifications.append('red')
        else:
            classifications.append('grey')

        cards.append(card)

    return {'cards': cards, 'classifications': classifications}

# ==============================================================================
# SIMULATION CORE
# ==============================================================================

def run_monte_carlo(hole_cards, num_players, num_simulations=50000, known_board=[]):
    wins = 0
    hand_type_counts = {name: 0 for name in HAND_NAMES.values()}
    opponent_hand_type_counts = {name: 0 for name in HAND_NAMES.values()}
    equity_progression = []
    results = {'wins': 0, 'ties': 0, 'losses': 0}

    for i in range(num_simulations):
        deck = build_deck()
        remaining_deck = [card for card in deck if card not in hole_cards + known_board]

        temp_deck = remaining_deck.copy()
        opponents = []
        for j in range(num_players - 1):
            opponent_cards = random.sample(temp_deck, 2)
            opponents.append(opponent_cards)
            temp_deck = [card for card in temp_deck if card not in opponent_cards]

        cards_needed = 5 - len(known_board)
        random_board = random.sample(temp_deck, cards_needed)
        board = known_board + random_board

        your_rank = best_hand(hole_cards, board)
        hand_name = HAND_NAMES[your_rank[0]]
        hand_type_counts[hand_name] += 1

        best_opponent = max(best_hand(opp, board) for opp in opponents)
        opponent_hand_name = HAND_NAMES[best_opponent[0]]
        opponent_hand_type_counts[opponent_hand_name] += 1

        if your_rank > best_opponent:
            results['wins'] += 1
        elif your_rank == best_opponent:
            results['ties'] += 1
        else:
            results['losses'] += 1

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
        for opp_combo in itertools.combinations(remaining_deck, 2):
            opp_rank = best_hand(list(opp_combo), board)
            if your_rank > opp_rank:
                results['wins'] += 1
            elif your_rank == opp_rank:
                results['ties'] += 1
            else:
                results['losses'] += 1

    elif num_players == 3:
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
    hand_type_counts = {name: 0 for name in HAND_NAMES.values()}

    if len(known_board) == 5:
        your_rank = best_hand(hole_cards, known_board)
        hand_name = HAND_NAMES[your_rank[0]]
        hand_type_counts[hand_name] += 1
        opp_results = evaluate_opponents(hole_cards, known_board, remaining_deck, num_players)
        results['wins'] += opp_results['wins']
        results['ties'] += opp_results['ties']
        results['losses'] += opp_results['losses']

    else:
        cards_needed = 5 - len(known_board)
        for combo in itertools.combinations(remaining_deck, cards_needed):
            board = known_board + list(combo)
            your_rank = best_hand(hole_cards, board)
            hand_name = HAND_NAMES[your_rank[0]]
            hand_type_counts[hand_name] += 1
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
        'total': total,
        'hand_type_counts': hand_type_counts
    }

def calculate_street_equities(hole_cards, num_players, known_board, num_simulations=10000):
    streets = ['Pre-flop']
    equities = []

    preflop = run_monte_carlo(hole_cards, num_players, num_simulations, known_board=[])
    equities.append(preflop['win_pct'])

    if len(known_board) >= 3:
        flop = run_monte_carlo(hole_cards, num_players, num_simulations, known_board[:3])
        streets.append('Flop')
        equities.append(flop['win_pct'])

    if len(known_board) >= 4:
        turn = run_exact_enumeration(hole_cards, num_players, known_board[:4])
        streets.append('Turn')
        equities.append(turn['win_pct'])

    if len(known_board) == 5:
        river = run_exact_enumeration(hole_cards, num_players, known_board)
        streets.append('River')
        equities.append(river['win_pct'])

    return {'streets': streets, 'equities': equities}

def calculate_player_count_equities(hole_cards, known_board, num_simulations=5000):
    player_counts = [2, 3, 4, 5, 6, 7, 8, 9]
    equities_by_count = {}

    for count in player_counts:
        equity = run_monte_carlo(hole_cards, count, num_simulations, known_board)['win_pct']
        equities_by_count[count] = equity

    return {
        'player_counts': player_counts,
        'win_pcts': [equities_by_count[count] for count in player_counts]
    }

# ==============================================================================
# TEST BLOCK
# ==============================================================================

# Turn test
result4 = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s'])
print(f'Turn exact win %: {result4["win_pct"]:.2f}%')
print(f'Turn total evaluations: {result4["total"]}')

# River test
result3 = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s', '3d'])
print(f'River exact win %: {result3["win_pct"]:.2f}%')
print(f'River total evaluations: {result3["total"]}')

# 3 player river test
result5 = run_exact_enumeration(['As', 'Ah'], 3, ['Kd', '7c', '2h', '9s', '3d'])
print(f'3-player river exact win %: {result5["win_pct"]:.2f}%')

# Monte Carlo test
result = run_monte_carlo(['As', 'Ah'], 2)
print(f'Win %: {result["win_pct"]:.1f}%')
print('Hand type counts:', result['hand_type_counts'])
print('Equity progression length:', len(result['equity_progression']))
print('First 5 progression values:', result['equity_progression'][:5])
print('Last 5 progression values:', result['equity_progression'][-5:])

# Outs tests
outs = calculate_outs(['As', 'Kh'], ['Ah', 'Kd', '2c'])
print(f'Top two pair — Bright green: {outs["classifications"].count("bright_green")}, Green: {outs["classifications"].count("green")}, Yellow: {outs["classifications"].count("yellow")}, Red: {outs["classifications"].count("red")}, Grey: {outs["classifications"].count("grey")}')

outs2 = calculate_outs(['9h', '8h'], ['7h', '6h', '2c'])
print(f'Straight flush draw — Bright green: {outs2["classifications"].count("bright_green")}, Green: {outs2["classifications"].count("green")}, Yellow: {outs2["classifications"].count("yellow")}, Red: {outs2["classifications"].count("red")}, Grey: {outs2["classifications"].count("grey")}')

outs3 = calculate_outs(['9h', '8d'], ['7h', '2c', '3s'])
print(f'3-card straight draw — Bright green: {outs3["classifications"].count("bright_green")}, Green: {outs3["classifications"].count("green")}, Yellow: {outs3["classifications"].count("yellow")}, Red: {outs3["classifications"].count("red")}, Grey: {outs3["classifications"].count("grey")}')

outs4 = calculate_outs(['9h', '7d'], ['5h', '2c', 'Kd'])
print(f'Gutshot — Bright green: {outs4["classifications"].count("bright_green")}, Green: {outs4["classifications"].count("green")}, Yellow: {outs4["classifications"].count("yellow")}, Red: {outs4["classifications"].count("red")}, Grey: {outs4["classifications"].count("grey")}')