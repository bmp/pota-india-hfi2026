"""07_license_class: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# 🎨 HIGHLY MUTED VINTAGE PALETTE
paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
vu2_color = '#c46060'       # Crimson for VU2
vu3_color = '#5a7a68'       # Vintage olive/teal for VU3
text_color = '#44403c'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# --- NETWORK HARDENING ---
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# 1. Fetch data
url = "https://api.pota.app/program/parks/IN"
try:
    parks_data = session.get(url, headers=headers, timeout=15).json()
except requests.exceptions.RequestException:
    parks_data = []

parks_df = pd.DataFrame(parks_data)
if not parks_df.empty:
    parks_df['activations'] = pd.to_numeric(parks_df['activations'], errors='coerce').fillna(0)
    activated_parks = parks_df[parks_df['activations'] > 0]['reference'].tolist()
else:
    activated_parks = []

activation_records = []

# 2. Extract logs (Full History)
for ref in activated_parks:
    act_url = f"https://api.pota.app/park/activations/{ref}?count=5000"
    try:
        res = session.get(act_url, headers=headers, timeout=15)
        if res.status_code == 200:
            for a in res.json():
                callsign = a.get('activeCallsign') or a.get('activator') or a.get('callsign')
                raw_qsos = a.get('qsoCount') or a.get('qsos') or a.get('totalQSOs') or a.get('count') or 0
                qsos = int(raw_qsos)
                if callsign:
                    activation_records.append({
                        'callsign': str(callsign).upper(),
                        'successful': 1 if qsos >= 10 else 0
                    })
    except requests.exceptions.RequestException:
        pass # Skip park on total failure
    time.sleep(0.1)

acts_df = pd.DataFrame(activation_records)

# 3. Categorize License Classes
if not acts_df.empty:
    activator_stats = acts_df.groupby('callsign').agg(successful_attempts=('successful', 'sum')).reset_index()

    def get_license_class(call):
        if 'VU2' in call: return 'VU2 (General Grade)'
        if 'VU3' in call: return 'VU3 (Restricted Grade)'
        return 'Other / Special Event'

    activator_stats['license_class'] = activator_stats['callsign'].apply(get_license_class)
    stats_filtered = activator_stats[activator_stats['license_class'] != 'Other / Special Event']
else:
    stats_filtered = pd.DataFrame(columns=['callsign', 'successful_attempts', 'license_class'])

# 4. Calculate X-Axis Statistical Summaries
tick_texts = []
classes_to_plot = ['VU2 (General Grade)', 'VU3 (Restricted Grade)']
total_all_acts = stats_filtered['successful_attempts'].sum() if not stats_filtered.empty else 1

for cls in classes_to_plot:
    cls_df = stats_filtered[stats_filtered['license_class'] == cls]
    cls_data = cls_df['successful_attempts']

    if not cls_data.empty:
        count = len(cls_data)
        total = cls_data.sum()
        share = (total / total_all_acts) * 100 if total_all_acts > 0 else 0
        mean = cls_data.mean()
        median = cls_data.median()
        q1 = cls_data.quantile(0.25)
        q3 = cls_data.quantile(0.75)
        iqr = q3 - q1
        lower_fence = max(0, q1 - 1.5 * iqr)
        upper_fence = q3 + 1.5 * iqr

        # Build the multi-line rich text label
        label = (
            f"<span style='font-size: 14px; font-weight: bold;'>{cls}</span><br>"
            f"<span style='font-size: 12px;'>"
            f"Operators: {count}<br>"
            f"Total Acts: {int(total)} ({share:.1f}%)<br>"
            f"Mean: {mean:.1f} | Median: {median:.1f}<br>"
            f"Q1: {q1:.1f} | Q3: {q3:.1f}<br>"
            f"Fences: [{lower_fence:.1f}, {upper_fence:.1f}]"
            f"</span>"
        )
    else:
        label = f"<b>{cls}</b><br>No Data"

    tick_texts.append(label)

# 5. Build the Box Plot
fig = go.Figure()

for cls, color in zip(classes_to_plot, [vu2_color, vu3_color]):
    cls_df = stats_filtered[stats_filtered['license_class'] == cls]

    # Generate custom hover strings for the dots
    hover_strings = [
        f"<b>Callsign:</b> {row['callsign']}<br><b>Successful Acts:</b> {row['successful_attempts']}"
        for _, row in cls_df.iterrows()
    ]

    fig.add_trace(go.Box(
        y=cls_df['successful_attempts'],
        name=cls,
        marker_color=color,
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        text=hover_strings,
        hoverinfo='text',
        hoveron='points' # Disables box-level hover, isolating tooltips to individual operators
    ))

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date} | VU3GLJ'

fig.update_layout(
    title=dict(text="Distribution of Successful Activations by License Class", x=0.5, font=dict(family="Georgia, 'Times New Roman', Times, serif", size=22, color=text_color)),
    margin={"r":40, "t":80, "l":60, "b":180}, # Increased bottom margin significantly to fit the large stat blocks
    height=650, # Increased height to balance the layout
    paper_bgcolor=paper_bg,
    plot_bgcolor=paper_bg,
    showlegend=False,
    annotations=[dict(x=0.5, y=-0.38, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), yanchor='top')],
    xaxis=dict(
        tickmode='array',
        tickvals=classes_to_plot,
        ticktext=tick_texts,
        showgrid=False,
        linecolor=grid_color,
        tickfont=dict(color=text_color, family="Georgia, serif")
    ),
    yaxis=dict(
        title=dict(text="Successful Activations per Operator", font=dict(color=text_color)),
        showgrid=True,
        gridcolor=grid_color,
        linecolor=grid_color,
        tickfont=dict(color=text_color),
        rangemode='tozero'
    )
)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'boxSelect']
})

# 6. Export the Graphic
print("#+begin_export html")
print('<figure id="fig:license-distribution" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 6:</strong> Baseline operational footprint of General vs. Restricted grade license holders.</p></figcaption>')
print('</figure>')
print("#+end_export\n")

# 7. Export Summary Statistics Table
print("#+begin_export html")
print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide License Class Demographics</summary>")
print("#+end_export\n")

print("#+CAPTION: Summary Statistics of India POTA Activators by License Class")
print("#+NAME: tab:license-class-stats")
print("| License Class | Active Operators | Median Activations | Maximum Activations | Total Activations (Class) |")
print("|---|---|---|---|---|")

if not stats_filtered.empty:
    summary_df = stats_filtered.groupby('license_class').agg(
        Active_Operators=('callsign', 'count'),
        Median_Acts=('successful_attempts', 'median'),
        Max_Acts=('successful_attempts', 'max'),
        Total_Acts=('successful_attempts', 'sum')
    ).reset_index()

    for _, row in summary_df.iterrows():
        print(f"| {row['license_class']} | {int(row['Active_Operators'])} | {int(row['Median_Acts'])} | {int(row['Max_Acts'])} | {int(row['Total_Acts'])} |")

print("\n#+begin_export html")
print("</details>")
print("#+end_export")
