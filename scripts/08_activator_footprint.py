"""08_activator_footprint: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import math
import re
import plotly.graph_objects as go
import time
from datetime import datetime
import textwrap

# ==========================================
# HAMQTH CREDENTIALS (OPTIONAL)
# ==========================================
# Set HAMQTH_USER and HAMQTH_PASS in the environment; without them the
# HamQTH location lookup is skipped.
HAMQTH_USER = os.environ.get('HAMQTH_USER', '')
HAMQTH_PASS = os.environ.get('HAMQTH_PASS', '')

# 🎨 HIGHLY MUTED VINTAGE PALETTE
paper_bg = '#f7f6f1'
grid_color = '#d6d3d1'
text_color = '#44403c'

# Cohesive vintage palette for operator identification
vintage_colors = ['#c46060', '#5a7a68', '#d4a373', '#4a6fa5', '#8b7355', '#6b8233', '#9c6b73']

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- HELPER FUNCTIONS ---
def hex_to_rgba(hex_str, alpha):
    """Converts a hex color string to an rgba string for transparent area fills."""
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"

def grid_to_latlon(grid):
    if not grid: return None, None
    grid = grid.upper().strip()
    if len(grid) < 4: return None, None
    lon = (ord(grid[0]) - 65) * 20 - 180
    lat = (ord(grid[1]) - 65) * 10 - 90
    lon += int(grid[2]) * 2
    lat += int(grid[3]) * 1
    if len(grid) >= 6:
        lon += (ord(grid[4]) - 65) * 5/60.0 + 2.5/60.0
        lat += (ord(grid[5]) - 65) * 2.5/60.0 + 1.25/60.0
    else:
        lon += 1
        lat += 0.5
    return lat, lon

def calculate_distance_bearing(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = R * c

    y = math.sin(dlon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360

    return dist, bearing

# 1. Fetch Parks & Coordinates
url_parks = "https://api.pota.app/program/parks/IN"
try:
    parks_resp = session.get(url_parks, headers=headers, timeout=15).json()
except requests.exceptions.RequestException:
    parks_resp = []

park_coords = {}
activated_parks = []
for p in parks_resp:
    if p.get('activations', 0) > 0:
        activated_parks.append(p['reference'])
        park_coords[p['reference']] = {
            'name': p.get('name', 'Unknown Park'),
            'lat': p.get('latitude'),
            'lon': p.get('longitude')
        }

# 2. Extract Logs
operator_footprints = set()
for ref in activated_parks:
    act_url = f"https://api.pota.app/park/activations/{ref}?count=5000"
    try:
        res = session.get(act_url, headers=headers, timeout=15)
        if res.status_code == 200:
            for a in res.json():
                callsign = a.get('activeCallsign') or a.get('activator') or a.get('callsign')
                if callsign:
                    base_call = str(callsign).upper().split('/')[0]
                    operator_footprints.add((base_call, ref))
    except requests.exceptions.RequestException:
        pass

ops_dict = {}
for call, park in operator_footprints:
    if call not in ops_dict: ops_dict[call] = []
    ops_dict[call].append(park)

# 3. Robust HamQTH Authentication
hamqth_session_id = None
debug_html = []

if HAMQTH_USER and HAMQTH_PASS:
    try:
        auth_res = session.get("https://www.hamqth.com/xml.php", params={'u': HAMQTH_USER, 'p': HAMQTH_PASS}, timeout=10)
        auth_text = auth_res.text

        error_match = re.search(r'<error>(.*?)</error>', auth_text, re.IGNORECASE)
        session_match = re.search(r'<session_id>(.*?)</session_id>', auth_text, re.IGNORECASE)

        if error_match:
            debug_html.append("")
        elif session_match:
            hamqth_session_id = session_match.group(1)
            debug_html.append("")
    except Exception as e:
        debug_html.append("")

# 4. Lookup Operator QTHs & Filter Valid/Missing Operators
plot_data = {}
all_operators = sorted(list(ops_dict.keys()))

valid_ops = []
missing_ops = []
global_max_dist = 50.0

for call in all_operators:
    grid = None
    if hamqth_session_id:
        try:
            lookup_res = session.get("https://www.hamqth.com/xml.php", params={'id': hamqth_session_id, 'callsign': call}, timeout=10)
            lookup_text = lookup_res.text

            error_match = re.search(r'<error>(.*?)</error>', lookup_text, re.IGNORECASE)
            if not error_match:
                grid_match = re.search(r'<grid>(.*?)</grid>', lookup_text, re.IGNORECASE)
                if grid_match:
                    grid = grid_match.group(1).strip()
        except Exception:
            pass

    lat1, lon1 = grid_to_latlon(grid) if grid else (None, None)

    if not (lat1 and lon1):
        missing_ops.append(call)
        continue

    valid_ops.append(call)

    parks_geodata = []
    for park in ops_dict[call]:
        p_info = park_coords.get(park)
        if p_info and p_info['lat'] and p_info['lon']:
            dist, brng = calculate_distance_bearing(lat1, lon1, float(p_info['lat']), float(p_info['lon']))
            parks_geodata.append({
                'park': park,
                'name': p_info['name'],
                'dist': dist,
                'bearing': brng
            })
            if dist > global_max_dist:
                global_max_dist = dist

    parks_geodata = sorted(parks_geodata, key=lambda x: x['bearing'])

    shape_r = []
    shape_theta = []
    marker_r = []
    marker_theta = []
    marker_text = []

    num_parks = len(parks_geodata)

    if num_parks > 0:
        for p in parks_geodata:
            marker_r.append(p['dist'])
            marker_theta.append(p['bearing'])
            marker_text.append(f"<b>{call}</b><br>Park: {p['park']} ({p['name']})<br>Distance: {p['dist']:.1f} km<br>Bearing: {p['bearing']:.1f}°")

        # Dynamic shape configuration criteria
        if num_parks >= 3:
            shape_r = [0] + [p['dist'] for p in parks_geodata] + [0]
            shape_theta = [parks_geodata[0]['bearing']] + [p['bearing'] for p in parks_geodata] + [parks_geodata[0]['bearing']]
        else:
            for p in parks_geodata:
                shape_r.extend([0, p['dist'], None])
                shape_theta.extend([0, p['bearing'], None])

    plot_data[call] = {
        'shape_r': shape_r,
        'shape_theta': shape_theta,
        'marker_r': marker_r,
        'marker_theta': marker_theta,
        'marker_text': marker_text,
        'is_amoeba': num_parks >= 3
    }

# 5. Build the Canvas
fig = go.Figure()
traces_per_op = 2
total_traces = len(valid_ops) * traces_per_op

for i, call in enumerate(valid_ops):
    color = vintage_colors[i % len(vintage_colors)]
    fill_color = hex_to_rgba(color, 0.15) if plot_data[call]['is_amoeba'] else None
    fill_mode = 'toself' if plot_data[call]['is_amoeba'] else None

    fig.add_trace(go.Scatterpolar(
        r=plot_data[call]['shape_r'],
        theta=plot_data[call]['shape_theta'],
        mode='lines',
        line=dict(color=color, width=1.5),
        fill=fill_mode,
        fillcolor=fill_color,
        opacity=0.7,
        showlegend=False,
        hoverinfo='skip',
        name=f"{call}_shape"
    ))

    fig.add_trace(go.Scatterpolar(
        r=plot_data[call]['marker_r'],
        theta=plot_data[call]['marker_theta'],
        mode='markers',
        marker=dict(color=color, size=8, line=dict(color=text_color, width=1)),
        text=plot_data[call]['marker_text'],
        hoverinfo='text',
        name=call
    ))

# 6. Configure Menus
dropdown_buttons = []

dropdown_buttons.append(dict(
    label='Select Operator',
    method='update',
    args=[
        {'visible': [True] * total_traces},
        {'title': dict(text="Geographic Footprint: All Operators", x=0.5, y=0.96, xanchor='center', font=dict(family="Georgia, serif", size=20, color=text_color))}
    ]
))

for i, call in enumerate(valid_ops):
    visibility = [False] * total_traces
    visibility[i * 2] = True
    visibility[i * 2 + 1] = True

    dropdown_buttons.append(dict(
        label=call,
        method='update',
        args=[
            {'visible': visibility},
            {'title': dict(text=f"Geographic Footprint: {call}", x=0.5, y=0.96, xanchor='center', font=dict(family="Georgia, serif", size=20, color=text_color))}
        ]
    ))

today_date = datetime.now().strftime("%d %b %Y")
footer_text = f'Data: POTA.app & HamQTH | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date}'

missing_str = ", ".join(missing_ops) if missing_ops else "None"
raw_disclaimer = f"Missing Location Data: {missing_str} (Excluded from rendering)"

# Wrap the text every ~90 characters and join the pieces with an HTML break
disclaimer_text = "<br>".join(textwrap.wrap(raw_disclaimer, width=90))

# Visual Real-Estate Layout Refinements
annotations = [
  dict(x=0.5, y=-0.06, xref='paper', yref='paper', text=footer_text, showarrow=False, font=dict(size=11, color='#78716c'), yanchor='top', xanchor='center'),
  dict(
      x=0.5, y=-0.12,
      xref='paper', yref='paper',
      text=disclaimer_text,
      showarrow=False,
      align="center", # This ensures the multi-line text remains perfectly centered
      font=dict(size=10, family="Georgia, serif", color='#a8a29e', style="italic"),
      yanchor='top', xanchor='center'
  )
]

radar_ceiling = global_max_dist * 1.08

fig.update_layout(
    title=dict(
        text="Geographic Footprint: All Operators",
        x=0.5,
        y=0.96,
        xanchor='center',
        yanchor='top',
        font=dict(family="Georgia, serif", size=20, color=text_color)
    ),
    margin={"r":60, "t":130, "l":60, "b":140}, # Shifted plot box downward to safely accommodate title bounds
    height=800,
    paper_bgcolor=paper_bg,
    polar=dict(
        bgcolor=paper_bg,
        angularaxis=dict(direction="clockwise", rotation=90, gridcolor=grid_color, linecolor=grid_color, tickfont=dict(color=text_color, family="Georgia, serif")),
        radialaxis=dict(
            gridcolor=grid_color,
            linecolor=grid_color,
            tickfont=dict(color=text_color, family="Georgia, serif"),
            title=dict(text="Distance (km)", font=dict(color=text_color, family="Georgia, serif")),
            range=[0, radar_ceiling]
        )
    ),
    updatemenus=[
        dict(
            type="dropdown",
            active=0,
            buttons=dropdown_buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.01, xanchor="left",
            y=1.06, yanchor="top", # Lowered controls underneath top-centered title panel
            bgcolor="rgba(255,255,255,0.9)", bordercolor=grid_color,
            font=dict(family="Georgia, serif", color=text_color)
        ),
        dict(
            type="buttons",
            direction="right",
            pad={"r": 10, "t": 10},
            showactive=False,
            buttons=[dict(
                label="↻ Reset to All",
                method="update",
                args=[
                    {"visible": [True] * total_traces},
                    {"title": dict(text="Geographic Footprint: All Operators", x=0.5, y=0.96, xanchor='center', font=dict(family="Georgia, serif", size=20, color=text_color))}
                ]
            )],
            x=0.99, xanchor="right",
            y=1.06, yanchor="top", # Lowered controls underneath top-centered title panel
            bgcolor="rgba(255,255,255,0.9)", bordercolor=grid_color,
            font=dict(family="Georgia, serif", color=text_color, size=12)
        )
    ],
    annotations=annotations,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.03, xanchor="center", x=0.5, font=dict(family="Georgia, serif", size=11, color=text_color))
)

html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', config={
    'displaylogo': False,
    'modeBarButtonsToRemove': [
        'select2d',    # Removes Box Select
        'lasso2d',     # Removes Lasso
        'zoom2d',      # Removes Zoom tool
        'pan2d',       # Removes Pan tool
        'zoomIn2d',    # Removes + button
        'zoomOut2d',   # Removes - button
        'autoScale2d'  # Removes Autoscale
    ]
    # By removing all of the above, 'resetScale2d' naturally becomes the primary visible tool.
})

# 7. Export Render Pipeline
print("#+begin_export html")
for d in debug_html:
    print(d)
print('<figure id="fig:polar-footprint" class="img-full">')
print(html_out)
print('<figcaption><p><strong>Figure 7: </strong>Geographic footprint and operational tracking radii of portable park activations.</p></figcaption>')
print('</figure>')
print("#+end_export\n")
