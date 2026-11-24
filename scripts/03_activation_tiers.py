"""03_activation_tiers: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
crimson_bar = '#c46060'
text_color = '#44403c'

url = "https://api.pota.app/program/parks/IN"
parks_data = requests.get(url).json()
parks_df = pd.DataFrame(parks_data)
parks_df['activations'] = pd.to_numeric(parks_df['activations'], errors='coerce').fillna(0)

def assign_tier(count):
    if count == 0: return "Unactivated"
    elif count == 1: return "1 Activation"
    elif 2 <= count <= 5: return "2 to 5 Activations"
    elif 6 <= count <= 10: return "6 to 10 Activations"
    else: return "11+ Activations"

parks_df['Tier'] = parks_df['activations'].apply(assign_tier)
tier_order = ["Unactivated", "1 Activation", "2 to 5 Activations", "6 to 10 Activations", "11+ Activations"]
tier_counts = parks_df['Tier'].value_counts().reindex(tier_order).fillna(0).reset_index()
tier_counts.columns = ['Tier', 'Park_Count']

fig = go.Figure()
fig.add_trace(go.Bar(
    x=tier_counts['Tier'], y=tier_counts['Park_Count'], name='Park Distribution by Tier',
    marker_color=crimson_bar, text=tier_counts['Park_Count'], textposition='auto',
    textfont=dict(color=text_color), hovertemplate='Tier: %{x}<br>Parks: %{y}<extra></extra>'
))

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date} | VU3GLJ'

fig.update_layout(
    title=dict(text="Distribution of Indian POTA Parks by Activation Tier", x=0.5, font=dict(family="Georgia, 'Times New Roman', Times, serif", size=22, color=text_color)),
    margin={"r":20, "t":60, "l":20, "b":120}, height=550, paper_bgcolor=paper_bg, plot_bgcolor=paper_bg, showlegend=True,
    legend=dict(x=0.75, y=0.95, bgcolor='rgba(255,255,255,0.6)'),
    annotations=[dict(x=0.5, y=-0.26, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), yanchor='top')],
    xaxis=dict(title=dict(text="Activity Classification Tiers", font=dict(color=text_color)), showgrid=False, linecolor=grid_color, tickfont=dict(color=text_color)),
    yaxis=dict(title=dict(text="Total Number of Parks in Tier", font=dict(color=text_color)), showgrid=True, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color))
)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False})

# Output Graph with HTML5 Figure Caption
print("#+begin_export html")
print('<figure id="fig:activation-tiers" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 3:</strong> Bar Chart detailing the \'Long Tail\' of unactivated and lightly-activated parks</p></figcaption>')
print('</figure>')
print("#+end_export\n")

# Output Collapsible Table
print("#+begin_export html")
print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Tier Breakdown Table</summary>")
print("#+end_export\n")

print("#+CAPTION: Breakdown of POTA Parks by Activation Tiers")
print("#+NAME: tab:activation-tiers")
print("| Activation Tier | Number of Parks |")
print("|---|---|")
for _, row in tier_counts.iterrows():
    print(f"| {row['Tier']} | {int(row['Park_Count'])} |")

print("\n#+begin_export html")
print("</details>")
print("#+end_export")
