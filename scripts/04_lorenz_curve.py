"""04_lorenz_curve: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
crimson_line = '#c46060'
equality_line = '#c4beba'
text_color = '#44403c'

url = "https://api.pota.app/program/parks/IN"
parks_data = requests.get(url).json()
parks_df = pd.DataFrame(parks_data)
parks_df['activations'] = pd.to_numeric(parks_df['activations'], errors='coerce').fillna(0)
parks_df = parks_df.sort_values(by='activations', ascending=False).reset_index(drop=True)

n_parks = len(parks_df)
parks_df['Rank'] = np.arange(1, n_parks + 1)
total_activations = parks_df['activations'].sum()
parks_df['Cum_Pct'] = (parks_df['activations'].cumsum() / total_activations * 100) if total_activations > 0 else 0.0

fig = go.Figure()

fig.add_trace(go.Scatter(x=parks_df['Rank'], y=parks_df['Cum_Pct'], mode='lines', name='Actual Distribution', line=dict(color=crimson_line, width=3), fill='tozeroy', fillcolor='rgba(196, 96, 96, 0.1)', hovertemplate='Rank %{x}<br>Cumulative %{y:.1f}%<extra></extra>'))
fig.add_trace(go.Scatter(x=[1, n_parks], y=[0, 100], mode='lines', name='Perfect Equality', line=dict(color=equality_line, width=2, dash='dash'), hoverinfo='skip'))

if n_parks >= 5:
    fig.add_trace(go.Scatter(x=[5, 5], y=[0, 100], mode='lines', name='Top 5 Parks Cutoff', line=dict(color='#5a7a68', width=2, dash='dot'), hovertemplate='Top 5 Parks Threshold<extra></extra>'))

parks_gt_1 = parks_df[parks_df['activations'] > 1]
if not parks_gt_1.empty:
    last_rank_gt_1 = parks_gt_1['Rank'].max()
    fig.add_trace(go.Scatter(x=[last_rank_gt_1, last_rank_gt_1], y=[0, 100], mode='lines', name='Activations > 1 Cutoff', line=dict(color='#a67c52', width=2, dash='dot'), hovertemplate='Activations > 1 Boundary<extra></extra>'))

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date} | VU3GLJ'

fig.update_layout(
    title=dict(text="Distribution of Lifetime Activations by Park Rank", x=0.5, font=dict(family="Georgia, 'Times New Roman', Times, serif", size=24, color=text_color)),
    margin={"r":20, "t":60, "l":20, "b":120}, height=550, paper_bgcolor=paper_bg, plot_bgcolor=paper_bg, showlegend=True, legend=dict(x=0.05, y=0.95, bgcolor='rgba(255,255,255,0.6)'),
    annotations=[dict(x=0.5, y=-0.26, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), yanchor='top')],
    xaxis=dict(title=dict(text="Individual POTA Parks Ranked by Activity (Rank 1 = Most Active)", font=dict(color=text_color)), showgrid=True, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color)),
    yaxis=dict(title=dict(text="Share of Total Lifetime India Activations (%)", font=dict(color=text_color)), showgrid=True, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color), range=[0, 100])
)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False})

# Output Graph with HTML5 Figure Caption
print("#+begin_export html")
print('<figure id="fig:lorenz-curve" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 4:</strong> Lorenz Curve showing the inequality of park activations</p></figcaption>')
print('</figure>')
print("#+end_export\n")

# Output Collapsible Table
print("#+begin_export html")
print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Ranked Parks Data Table</summary>")
print("#+end_export\n")

print("#+CAPTION: Complete Ranking of India POTA Parks by Activation Count")
print("#+NAME: tab:park-rankings")
print("| Rank | Reference | Park Name | Activations | Cumulative % |")
print("|---|---|---|---|---|")
for _, row in parks_df.iterrows():
    print(f"| {row['Rank']} | {row['reference']} | {row.get('name', 'Unknown')} | {int(row['activations'])} | {row['Cum_Pct']:.2f}% |")

print("\n#+begin_export html")
print("</details>")
print("#+end_export")
