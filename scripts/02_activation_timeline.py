"""02_activation_timeline: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
crimson_line = '#c46060'
text_color = '#44403c'

url = "https://api.pota.app/program/parks/IN"
parks_data = requests.get(url).json()
parks_df = pd.DataFrame(parks_data)
parks_df['activations'] = pd.to_numeric(parks_df['activations'], errors='coerce').fillna(0)

activated_parks = parks_df[parks_df['activations'] > 0]['reference'].tolist()
all_dates = []

for ref in activated_parks:
    act_url = f"https://api.pota.app/park/activations/{ref}"
    res = requests.get(act_url)
    if res.status_code == 200:
        for a in res.json():
            date_str = a.get('qso_date') or a.get('active_date') or a.get('date')
            if date_str: all_dates.append(date_str.split('T')[0])
    time.sleep(0.2)

dates_df = pd.DataFrame({'date': pd.to_datetime(all_dates)}).dropna().sort_values('date')
daily_counts = dates_df.groupby('date').size().reset_index(name='daily_activations')
daily_counts['cumulative_activations'] = daily_counts['daily_activations'].cumsum()

dates_df['year'] = dates_df['date'].dt.year
yearly_counts = dates_df.groupby('year').size().reset_index(name='yearly_activations')
yearly_counts['cumulative_activations'] = yearly_counts['yearly_activations'].cumsum()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=daily_counts['date'], y=daily_counts['cumulative_activations'], mode='lines', name='Cumulative Activations Line',
    line=dict(color=crimson_line, width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(196, 96, 96, 0.1)', hoverinfo='x+y'
))

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date} | VU3GLJ'

fig.update_layout(
    title=dict(text="Cumulative POTA Activations in India", x=0.5, font=dict(family="Georgia, 'Times New Roman', Times, serif", size=24, color=text_color)),
    margin={"r":20, "t":60, "l":20, "b":120}, height=550, paper_bgcolor=paper_bg, plot_bgcolor=paper_bg, showlegend=True,
    legend=dict(x=0.05, y=0.95, bgcolor='rgba(255,255,255,0.6)'),
    annotations=[dict(x=0.5, y=-0.26, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), yanchor='top')],
    xaxis=dict(title=dict(text="Timeline (2020 – Present)", font=dict(color=text_color)), showgrid=True, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color)),
    yaxis=dict(title=dict(text="Cumulative Number of Completed Activations (Running Total)", font=dict(color=text_color)), showgrid=True, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color))
)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False})

# Output Graph with HTML5 Figure Caption
print("#+begin_export html")
print('<figure id="fig:timeline-activations" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 2:</strong> Historical Timeline of POTA Activations</p></figcaption>')
print('</figure>')
print("#+end_export\n")

# Output Collapsible Table
print("#+begin_export html")
print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Timeline Data Table</summary>")
print("#+end_export\n")

print("#+CAPTION: Year-wise Cumulative POTA Activations")
print("#+NAME: tab:yearly-activations")
print("| Year | Activations in Year | Cumulative Total |")
print("|---|---|---|")
for _, row in yearly_counts.iterrows():
    print(f"| {int(row['year'])} | {int(row['yearly_activations'])} | {int(row['cumulative_activations'])} |")

print("\n#+begin_export html")
print("</details>")
print("#+end_export")
