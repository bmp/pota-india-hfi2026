"""06_activator_profiles: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# 🎨 HIGHLY MUTED VINTAGE TERRACOTTA PALETTE
paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
text_color = '#44403c'

# Reverted to the Terracotta progression buckets
bands = [
    {"min": 0,      "max": 20.001, "color": "#a8a29e", "name": "0-20% (Low)"},
    {"min": 20.001, "max": 80.001, "color": "#d4a373", "name": "21-80% (Moderate)"},
    {"min": 80.001, "max": 101.0,  "color": "#c46060", "name": "81-100% (High)"}
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 1. Data Retrieval
url = "https://api.pota.app/program/parks/IN"
parks_data = requests.get(url, headers=headers).json()
parks_df = pd.DataFrame(parks_data)
parks_df['activations'] = pd.to_numeric(parks_df['activations'], errors='coerce').fillna(0)

activated_parks = parks_df[parks_df['activations'] > 0]['reference'].tolist()
activation_records = []

# 2. Log Analysis Iteration (With full historic logs)
for ref in activated_parks:
    act_url = f"https://api.pota.app/park/activations/{ref}?count=5000"
    res = requests.get(act_url, headers=headers)
    if res.status_code == 200:
        for a in res.json():
            callsign = a.get('activeCallsign') or a.get('activator') or a.get('callsign')
            raw_qsos = a.get('qsoCount') or a.get('qsos') or a.get('totalQSOs') or a.get('count') or 0
            qsos = int(raw_qsos)
            if callsign:
                activation_records.append({
                    'callsign': str(callsign).upper(),
                    'park': ref,
                    'successful': 1 if qsos >= 10 else 0,
                    'unsuccessful': 1 if qsos < 10 else 0
                })
    time.sleep(0.1)

acts_df = pd.DataFrame(activation_records)

# 3. Structural Processing & Aggregations
if not acts_df.empty:
    activator_stats = acts_df.groupby('callsign').agg(
        total_attempts=('park', 'count'),
        successful_attempts=('successful', 'sum'),
        unsuccessful_attempts=('unsuccessful', 'sum'),
        unique_parks=('park', 'nunique')
    ).reset_index()

    activator_stats['success_rate'] = (activator_stats['successful_attempts'] / activator_stats['total_attempts']) * 100

    # Sort ascending by Unique Parks so the highest explorers sit at the top of the graph
    activator_stats = activator_stats.sort_values(by=['unique_parks', 'successful_attempts'], ascending=[True, True]).reset_index(drop=True)
else:
    activator_stats = pd.DataFrame(columns=['callsign', 'total_attempts', 'successful_attempts', 'unsuccessful_attempts', 'unique_parks', 'success_rate'])

# Scale rows dynamically
num_operators = len(activator_stats)
chart_height = max(500, num_operators * 28 + 180)
callsign_array = activator_stats['callsign'].tolist()

# 4. Initialize Multi-panel Canvas
fig = make_subplots(rows=1, cols=2, shared_yaxes=False, horizontal_spacing=0.18)

# 5. Populate Traces using Native Plotly Tooltips
for b in bands:
    band_df = activator_stats[(activator_stats['success_rate'] >= b['min']) & (activator_stats['success_rate'] < b['max'])]

    x_left = band_df['unique_parks'].tolist() if not band_df.empty else []
    x_right = band_df['total_attempts'].tolist() if not band_df.empty else []
    y_labels = band_df['callsign'].tolist() if not band_df.empty else []

    hover_info = []
    if not band_df.empty:
        for _, row in band_df.iterrows():
            profile = (
                f"<b>{row['callsign']}</b><br>"
                f"Success Rate: {row['success_rate']:.1f}%<br>"
                f"Unique Parks: {row['unique_parks']}<br>"
                f"Total Attempts: {row['total_attempts']}<br>"
                f"Successful (>=10): {row['successful_attempts']}<br>"
                f"Failed (<10): {row['unsuccessful_attempts']}"
            )
            hover_info.append(profile)

    # Left Wing Panel: Unique Parks
    fig.add_trace(go.Bar(
        x=x_left, y=y_labels, orientation='h',
        marker=dict(color=b['color']), showlegend=False,
        hoverinfo='text', hovertext=hover_info
    ), row=1, col=1)

    # Right Wing Panel: Total Attempts
    fig.add_trace(go.Bar(
        x=x_right, y=y_labels, orientation='h',
        marker=dict(color=b['color']), name=b['name'],
        showlegend=True if not band_df.empty else False,
        hoverinfo='text', hovertext=hover_info
    ), row=1, col=2)

# 6. Central Alignment Architecture & Annotations
fig.update_yaxes(type='category', categoryorder='array', categoryarray=callsign_array, side='right', showticklabels=True, tickfont=dict(family="Courier New, monospace", size=13, color=text_color), showgrid=False, row=1, col=1)
fig.update_yaxes(type='category', categoryorder='array', categoryarray=callsign_array, showticklabels=False, showgrid=False, row=1, col=2)

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date} | VU3GLJ'

annotations = [
    dict(x=0.5, y=1.03, xref='paper', yref='paper', text="<b>Activator</b>", showarrow=False, xanchor='center', yanchor='bottom', font=dict(family="Georgia, serif", size=14, color=text_color)),
    dict(x=0.5, y=-0.08, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), xanchor='center', yanchor='top')
]

fig.update_layout(
    title=dict(text="Activator Profiles: Exploration vs. Effort", x=0.5, y=0.98, font=dict(family="Georgia, serif", size=24, color=text_color)),
    margin={"r":40, "t":140, "l":40, "b":100},
    height=chart_height,
    paper_bgcolor=paper_bg, plot_bgcolor=paper_bg,
    barmode='stack',
    bargap=0.20,
    annotations=annotations,
    hovermode='closest',
    hoverlabel=dict(bgcolor="rgba(255,255,255,0.85)", font_size=12, font_family="Georgia, serif"), # Semi-transparent box prevents full blocking
    legend=dict(
        title=dict(text="Success Rate Percentage Band", font=dict(size=12, family="Georgia, serif", color=text_color)),
        orientation="h", yanchor="bottom", y=-0.06, xanchor="center", x=0.5,
        font=dict(family="Georgia, serif", size=11, color=text_color)
    )
)

# 7. Axis Configurations Firmly Top-Mounted
fig.update_xaxes(title=dict(text="Unique Parks (Exploration)", font=dict(family="Georgia, serif", size=13)), autorange="reversed", side="top", showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color), row=1, col=1)
fig.update_xaxes(title=dict(text="Total Attempts (Overall Outings)", font=dict(family="Georgia, serif", size=13)), side="top", showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color), row=1, col=2)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'boxSelect', 'toggleHover', 'resetScale2d']
})

# 8. Output Pipeline Rendering (Pure HTML/Plotly, No JS)
print("#+begin_export html")
print('<figure id="fig:activator-profiles" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 5:</strong> Twin-axis butterfly chart mapping operator exploration and effort.</p></figcaption>')
print('</figure>')
print("#+end_export\n")

print("#+begin_export html")
print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Activator Statistics Table</summary>")
print("#+end_export\n")

# Display the table sorted identically to the chart
display_stats = activator_stats.sort_values(by=['unique_parks', 'successful_attempts'], ascending=[False, False])

print("#+CAPTION: Individual Activator Statistics (India)")
print("#+NAME: tab:activator-stats")
print("| Callsign | Unique Parks Activated | Total Activations | Successful (>=10 QSOs) | Failed (<10 QSOs) | Success Rate |")
print("|---|---|---|---|---|---|")
for _, row in display_stats.iterrows():
    print(f"| {row['callsign']} | {int(row['unique_parks'])} | {int(row['total_attempts'])} | {int(row['successful_attempts'])} | {int(row['unsuccessful_attempts'])} | {row['success_rate']:.1f}% |")

print("\n#+begin_export html")
print("</details>")
print("#+end_export")
