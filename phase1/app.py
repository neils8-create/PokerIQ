import streamlit as st
from monte_carlo import run_monte_carlo, run_exact_enumeration, calculate_street_equities, calculate_player_count_equities, calculate_outs
from graphs import plot_convergence, plot_opponent_distribution, plot_equity_over_streets, plot_player_count_curve, plot_outs_visualization, plot_exact_distribution

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title='PokerIQ',
    page_icon='♠',
    layout='centered'
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    background-color: #080b0f;
    color: #e8edf2;
}

.stApp {
    background-color: #080b0f;
}

.poker-header {
    text-align: center;
    padding: 40px 0 20px;
}

.poker-title {
    font-family: 'Playfair Display', serif;
    font-size: 72px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
    letter-spacing: -2px;
    margin: 0;
}

.poker-title span { color: #00c853; text-shadow: 0 0 40px rgba(0,200,83,0.4); }

.poker-suits { font-size: 24px; letter-spacing: 16px; margin: 12px 0 6px; opacity: 0.4; }
.poker-suits .red { color: #ff4d4d; }

.poker-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #4a5a66;
    margin: 0;
}

.divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 28px 0; }

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #00c853;
    margin-bottom: 12px;
    margin-top: 24px;
}

.stSelectbox > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #4a5a66 !important;
}

div[data-baseweb="select"] > div {
    background-color: #0d1117 !important;
    border: 1px solid rgba(0,200,83,0.2) !important;
    border-radius: 4px !important;
    color: #e8edf2 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stNumberInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #4a5a66 !important;
}

.stNumberInput > div > div > input {
    background-color: #0d1117 !important;
    border: 1px solid rgba(0,200,83,0.2) !important;
    color: #e8edf2 !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-align: center !important;
}

.stButton > button {
    width: 100%;
    background-color: #00c853 !important;
    color: #080b0f !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 14px !important;
    margin-top: 8px !important;
}

.stButton > button:hover {
    background-color: #00a844 !important;
    transform: translateY(-1px) !important;
}

div[data-testid="column"]:nth-child(2) .stButton > button {
    background-color: #1a2530 !important;
    color: #4a5a66 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

div[data-testid="column"]:nth-child(2) .stButton > button:hover {
    background-color: #222f3a !important;
    color: #7a8a96 !important;
}

[data-testid="stMetric"] {
    background-color: #0d1117;
    border: 1px solid rgba(0,200,83,0.2);
    border-radius: 6px;
    padding: 20px 24px;
    text-align: center;
}

[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #4a5a66 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 48px !important;
    font-weight: 700 !important;
    color: #00c853 !important;
}

.stSuccess {
    background-color: rgba(0,200,83,0.08) !important;
    border: 1px solid rgba(0,200,83,0.2) !important;
    color: #00c853 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

.disabled-hint {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2a3a46;
    margin: 4px 0 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Conversion maps ──────────────────────────────────────────
RANKS = ['Ace','King','Queen','Jack','10','9','8','7','6','5','4','3','2']
SUITS = ['Spades','Hearts','Diamonds','Clubs']
SUIT_SYMBOLS = {'Spades':'♠','Hearts':'♥','Diamonds':'♦','Clubs':'♣'}
RANK_MAP = {'Ace':'A','King':'K','Queen':'Q','Jack':'J','10':'T','9':'9','8':'8','7':'7','6':'6','5':'5','4':'4','3':'3','2':'2'}
SUIT_MAP = {'Spades':'s','Hearts':'h','Diamonds':'d','Clubs':'c'}

def to_card(rank_name, suit_name):
    return RANK_MAP[rank_name] + SUIT_MAP[suit_name]

# ── Session state init ───────────────────────────────────────
if 'flop' not in st.session_state:
    st.session_state.flop = []

if 'results' not in st.session_state:
    st.session_state.results = None

for key in ['r1','s1','r2','s2','r3','s3','r4','s4','r5','s5','r6','s6','r7','s7']:
    if key not in st.session_state:
        st.session_state[key] = '—'

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="poker-header">
    <div class="poker-suits">♠ <span class="red">♥</span> ♣ <span class="red">♦</span></div>
    <h1 class="poker-title">Poker<span>IQ</span></h1>
    <p class="poker-subtitle">Real-time Hand Equity Calculator</p>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ── Card selector helper ─────────────────────────────────────
def card_selector(label_rank, label_suit, key_rank, key_suit, used_cards, optional=False):
    rank_options = ['—'] + RANKS if optional else RANKS
    suit_options = ['—'] + SUITS if optional else SUITS
    col_r, col_s = st.columns(2)
    with col_r:
        rank_index = rank_options.index(st.session_state.get(key_rank, '—')) if st.session_state.get(key_rank, '—') in rank_options else 0
        rank = st.selectbox(label_rank, rank_options, index=rank_index, key=key_rank)
    with col_s:
        suit_index = suit_options.index(st.session_state.get(key_suit, '—')) if st.session_state.get(key_suit, '—') in suit_options else 0
        suit = st.selectbox(label_suit, suit_options, index=suit_index, key=key_suit)
    if rank == '—' or suit == '—':
        return None
    card = to_card(rank, suit)
    if card in used_cards:
        st.error(f'{rank} of {suit} is already selected.')
        return None
    return card

# ── Hole Cards ───────────────────────────────────────────────
st.markdown('<p class="section-label">Your Cards</p>', unsafe_allow_html=True)
used_cards = []

card1 = card_selector('Card 1 Rank', 'Card 1 Suit', 'r1', 's1', used_cards, optional=True)
if card1:
    used_cards.append(card1)

card2 = card_selector('Card 2 Rank', 'Card 2 Suit', 'r2', 's2', used_cards, optional=True)
if card2:
    used_cards.append(card2)

# ── Table ────────────────────────────────────────────────────
st.markdown('<p class="section-label">Table</p>', unsafe_allow_html=True)
num_players = st.number_input('Number of players', min_value=2, max_value=9, value=2, step=1)
num_simulations = st.slider('Simulation count', min_value=10000, max_value=100000, value=10000, step=5000)

# ── Community Cards ──────────────────────────────────────────
st.markdown('<p class="section-label">Community Cards</p>', unsafe_allow_html=True)
st.caption('Leave as — if not yet dealt')

flop1 = card_selector('Flop 1 Rank', 'Flop 1 Suit', 'r3', 's3', used_cards, optional=True)
if flop1:
    used_cards.append(flop1)

flop2 = card_selector('Flop 2 Rank', 'Flop 2 Suit', 'r4', 's4', used_cards, optional=True)
if flop2:
    used_cards.append(flop2)

flop3 = card_selector('Flop 3 Rank', 'Flop 3 Suit', 'r5', 's5', used_cards, optional=True)
if flop3:
    used_cards.append(flop3)

flop_cards = [c for c in [flop1, flop2, flop3] if c is not None]
flop_complete = len(flop_cards) == 3

if flop_complete:
    turn = card_selector('Turn Rank', 'Turn Suit', 'r6', 's6', used_cards, optional=True)
    if turn:
        used_cards.append(turn)
else:
    st.markdown('<p class="disabled-hint">Complete all 3 flop cards to enter the turn</p>', unsafe_allow_html=True)
    turn = None

if turn:
    river = card_selector('River Rank', 'River Suit', 'r7', 's7', used_cards, optional=True)
    if river:
        used_cards.append(river)
elif flop_complete:
    st.markdown('<p class="disabled-hint">Enter the turn card before the river</p>', unsafe_allow_html=True)
    river = None
else:
    river = None

# ── Calculate & Reset buttons ────────────────────────────────
st.markdown('<div style="height: 8px"></div>', unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns([3, 1])

with btn_col1:
    calculate = st.button('Calculate Equity')
with btn_col2:
    reset = st.button('Reset')

if reset:
    for key in ['r1','s1','r2','s2','r3','s3','r4','s4','r5','s5','r6','s6','r7','s7']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.results = None
    st.rerun()

if calculate:
    errors = []

    if not card1 or not card2:
        errors.append('Please select both of your hole cards.')

    if len(flop_cards) == 1 or len(flop_cards) == 2:
        errors.append('Please select all 3 flop cards or leave the flop blank.')

    if turn and len(flop_cards) != 3:
        errors.append('Please complete the flop before adding the turn.')

    if river and not turn:
        errors.append('Please add the turn card before adding the river.')

    if errors:
        for error in errors:
            st.error(error)
    else:
        known_board = [c for c in [flop1, flop2, flop3, turn, river] if c is not None]
        hole_cards = [card1, card2]
        num_players_int = int(num_players)
        num_sims_int = int(num_simulations)

        with st.spinner('Running simulations...'):
            if len(known_board) >= 4:
                equity_result = run_exact_enumeration(hole_cards, num_players_int, known_board)
                algorithm = 'Exact Enumeration'
            else:
                equity_result = run_monte_carlo(hole_cards, num_players_int, num_sims_int, known_board)
                algorithm = 'Monte Carlo'

            mc_result = run_monte_carlo(hole_cards, num_players_int, num_sims_int, known_board)
            street_result = calculate_street_equities(hole_cards, num_players_int, known_board)
            pc_result = calculate_player_count_equities(hole_cards, known_board)
            outs_result = calculate_outs(hole_cards, known_board, num_players_int) if len(known_board) >= 3 else None

            st.session_state.results = {
                'equity_result': equity_result,
                'mc_result': mc_result,
                'street_result': street_result,
                'pc_result': pc_result,
                'outs_result': outs_result,
                'algorithm': algorithm,
                'hole_cards': hole_cards,
                'known_board': known_board,
                'num_simulations': num_sims_int,
            }

# ── Results display ──────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results
    equity = r['equity_result']
    algorithm = r['algorithm']

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.success('Simulation complete')
    st.metric(
        label=f'{algorithm} Win Probability',
        value=f'{equity["win_pct"]:.1f}%'
    )

    st.markdown('<p class="section-label">Simulation Graphs</p>', unsafe_allow_html=True)

    if algorithm == 'Monte Carlo':
        fig_conv = plot_convergence(r['mc_result']['equity_progression'], r['mc_result']['win_pct'])
        st.plotly_chart(fig_conv, use_container_width=True)

    fig_dist = plot_opponent_distribution(
        r['mc_result']['hand_type_counts'],
        r['mc_result']['opponent_hand_type_counts'],
        r['num_simulations']
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    fig_streets = plot_equity_over_streets(
        r['street_result']['streets'],
        r['street_result']['equities']
    )
    st.plotly_chart(fig_streets, use_container_width=True)

    fig_pc = plot_player_count_curve(
        r['pc_result']['player_counts'],
        r['pc_result']['win_pcts']
    )
    st.plotly_chart(fig_pc, use_container_width=True)

    if r['outs_result']:
        fig_outs = plot_outs_visualization(
            r['outs_result']['cards'],
            r['outs_result']['classifications'],
            r['hole_cards'],
            r['known_board']
        )
        st.plotly_chart(fig_outs, use_container_width=True)

    if len(r['known_board']) >= 4:
        fig_exact = plot_exact_distribution(
            r['equity_result']['hand_type_counts'],
            sum(r['equity_result']['hand_type_counts'].values())
        )
        st.plotly_chart(fig_exact, use_container_width=True)