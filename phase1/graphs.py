import plotly.graph_objects as go
from monte_carlo import run_monte_carlo, run_exact_enumeration, calculate_street_equities, calculate_player_count_equities, calculate_outs

def plot_convergence(equity_progression, final_win_pct):
    x_values = list(range(100, len(equity_progression) * 100 + 1, 100))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_values,
        y=equity_progression,
        mode='lines',
        name='Win % Estimate',
        line=dict(color='#00c853', width=1.5)
    ))

    fig.add_hline(
        y=final_win_pct,
        line_dash='dash',
        line_color='rgba(0,200,83,0.4)',
        annotation_text=f'Converged: {final_win_pct:.1f}%',
        annotation_font_color='#00c853'
    )

    fig.update_layout(
        title='Monte Carlo Convergence',
        xaxis_title='Simulations Run',
        yaxis_title='Win Probability (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_dark',
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=True
    )

    return fig

def plot_opponent_distribution(hand_type_counts, opponent_hand_type_counts, num_simulations):
    labels = list(hand_type_counts.keys())
    your_percentages = [count / num_simulations * 100 for count in hand_type_counts.values()]
    opponent_percentages = [count / num_simulations * 100 for count in opponent_hand_type_counts.values()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=your_percentages,
        name='Your Hand',
        marker_color='#00c853'
    ))

    fig.add_trace(go.Bar(
        x=labels,
        y=opponent_percentages,
        name='Opponent Hand',
        marker_color='#ff4d4d'
    ))

    fig.update_layout(
        title='Hand Type Distribution — You vs Opponent',
        xaxis_title='Hand Type',
        yaxis_title='Frequency (%)',
        yaxis=dict(range=[0, 100]),
        barmode='group',
        template='plotly_dark',
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=True
    )

    return fig

def plot_equity_over_streets(streets, equities):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=streets,
        y=equities,
        mode='lines+markers',
        line=dict(color='#00c853', width=2),
        marker=dict(size=8, color='#00c853')
    ))

    for street, equity in zip(streets, equities):
        fig.add_annotation(
            x=street,
            y=equity,
            text=f'{equity:.1f}%',
            showarrow=False,
            yshift=15,
            font=dict(color='#00c853', size=12)
        )

    fig.update_layout(
        title='Equity Progression Over Streets',
        xaxis_title='Street',
        yaxis_title='Equity (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_dark',
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=False
    )

    return fig

def plot_player_count_curve(player_counts, win_pcts):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=player_counts,
        y=win_pcts,
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(0,200,83,0.1)',
        line=dict(color='#00c853', width=2),
        marker=dict(size=8, color='#00c853'),
        name='Win %'
    ))

    for count, pct in zip(player_counts, win_pcts):
        fig.add_annotation(
            x=count,
            y=pct,
            text=f'{pct:.1f}%',
            showarrow=False,
            yshift=15,
            font=dict(color='#00c853', size=11)
        )

    fig.update_layout(
        title='Win Probability vs Player Count',
        xaxis_title='Number of Players',
        yaxis_title='Win Probability (%)',
        yaxis=dict(range=[0, 100]),
        xaxis=dict(tickmode='linear', tick0=2, dtick=1),
        template='plotly_dark',
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=False
    )

    return fig

def plot_outs_visualization(cards, classifications, hole_cards, known_board):
    RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
    SUITS = ['c','d','h','s']
    rank_to_x = {r: i for i, r in enumerate(RANKS)}
    suit_to_y = {s: i for i, s in enumerate(SUITS)}

    COLOR_MAP = {
        'bright_green': '#00c853',
        'yellow': '#ffd740',
        'green': '#69f0ae',
        'red': '#ff4d4d',
        'grey': '#2a3a46',
        'used': '#111827'
    }

    LEGEND_ITEMS = [
        ('bright_green', 'Immediate improvement'),
        ('yellow', 'Draw advancement'),
        ('green', 'Kicker improvement'),
        ('red', 'Danger card'),
        ('grey', 'Neutral'),
        ('used', 'In play (hole/board)')
    ]

    card_to_class = dict(zip(cards, classifications))
    used_cards = set(hole_cards + known_board)

    x_vals = []
    y_vals = []
    colors = []
    labels = []

    for suit in SUITS:
        for rank in RANKS:
            card = rank + suit
            x_vals.append(rank_to_x[rank])
            y_vals.append(suit_to_y[suit])
            labels.append(card)
            if card in used_cards:
                colors.append(COLOR_MAP['used'])
            else:
                cls = card_to_class.get(card, 'grey')
                colors.append(COLOR_MAP.get(cls, COLOR_MAP['grey']))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers+text',
        marker=dict(
            size=35,
            color=colors,
            symbol='square',
            line=dict(width=1, color='#1a2332')
        ),
        text=labels,
        textposition='middle center',
        textfont=dict(color='#e8edf2', size=9),
        showlegend=False
    ))

    for key, name in LEGEND_ITEMS:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=12, color=COLOR_MAP[key], symbol='square'),
            name=name,
            showlegend=True
        ))

    fig.update_layout(
        title='Outs Visualization',
        template='plotly_dark',
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        xaxis=dict(
            title='',
            showticklabels=False,
            range=[-0.5, 12.5],
            fixedrange=True,
            showgrid=False
        ),
        yaxis=dict(
            title='',
            showticklabels=False,
            range=[-0.5, 3.5],
            fixedrange=True,
            showgrid=False,
            scaleanchor='x',
            scaleratio=1
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=80)
    )

    return fig

def plot_exact_distribution(hand_type_counts, total):
    labels = list(hand_type_counts.keys())
    values = list(hand_type_counts.values())
    percentages = [count / total * 100 for count in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=percentages,
        marker_color='#4da6ff'
    ))

    fig.update_layout(
        title='Exact Enumeration Hand Type Distribution',
        xaxis_title='Hand Type',
        yaxis_title='Frequency (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_dark',
        xaxis=dict(tickfont=dict(size=10)),
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=False
    )

    return fig

result = run_monte_carlo(['As', 'Ah'], 2, num_simulations=50000)
fig3 = plot_opponent_distribution(result['hand_type_counts'], result['opponent_hand_type_counts'], 50000)
fig3.show()
street_result = calculate_street_equities(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s', '3d'])
fig4 = plot_equity_over_streets(street_result['streets'], street_result['equities'])
fig4.show()
from monte_carlo import calculate_player_count_equities
pc_result = calculate_player_count_equities(['As', 'Ah'], [])
fig5 = plot_player_count_curve(pc_result['player_counts'], pc_result['win_pcts'])
fig5.show()
outs = calculate_outs(['9h', '7d'], ['5h', '2c', 'Kd'])
fig6 = plot_outs_visualization(outs['cards'], outs['classifications'], ['9h', '7d'], ['5h', '2c', 'Kd'])
fig6.show()
exact = run_exact_enumeration(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s'])
fig7 = plot_exact_distribution(exact['hand_type_counts'], sum(exact['hand_type_counts'].values()))
fig7.show()