import plotly.graph_objects as go
from monte_carlo import run_monte_carlo, calculate_street_equities, calculate_player_count_equities

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

def plot_outcome_distribution(hand_type_counts, num_simulations):
    labels = list(hand_type_counts.keys())
    values = list(hand_type_counts.values())
    percentages = [count / num_simulations * 100 for count in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=percentages,
        marker_color='#00c853'
    ))

    fig.update_layout(
        title='Hand Type Distribution',
        xaxis_title='Hand Type',
        yaxis_title='Frequency (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_dark',
        xaxis=dict(
            tickfont=dict(size=10)
        ),  # <-- comma was missing here
        paper_bgcolor='#080b0f',
        plot_bgcolor='#0d1117',
        font=dict(color='#e8edf2'),
        showlegend=False
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

result = run_monte_carlo(['As', 'Ah'], 2, num_simulations=50000)
fig2 = plot_outcome_distribution(result['hand_type_counts'], 50000)
fig2.show()
fig3 = plot_opponent_distribution(result['hand_type_counts'], result['opponent_hand_type_counts'], 50000)
fig3.show()
street_result = calculate_street_equities(['As', 'Ah'], 2, ['Kd', '7c', '2h', '9s', '3d'])
fig4 = plot_equity_over_streets(street_result['streets'], street_result['equities'])
fig4.show()
pc_result = calculate_player_count_equities(['As', 'Ah'], [])
fig5 = plot_player_count_curve(pc_result['player_counts'], pc_result['win_pcts'])
fig5.show()