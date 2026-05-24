import plotly.graph_objects as go
from monte_carlo import run_monte_carlo

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

result = run_monte_carlo(['As', 'Ah'], 2, num_simulations=50000)
fig2 = plot_outcome_distribution(result['hand_type_counts'], 50000)
fig2.show()
fig3 = plot_opponent_distribution(result['hand_type_counts'], result['opponent_hand_type_counts'], 50000)
fig3.show()