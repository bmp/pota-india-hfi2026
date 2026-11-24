"""09_hunters: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import cloudscraper
import pandas as pd
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import json
import urllib.request

# ==========================================
# 🎨 COHESIVE VINTAGE PALETTE CONFIGURATION
# ==========================================
paper_bg = '#f7f6f1'
grid_color = '#e5e3dc'
text_color = '#44403c'
vu_color = '#6b8296'        # Dusty Slate Blue for Domestic VU operators
dx_color = '#d1b77f'        # Muted Mustard for International DX chasers

terracotta_scale = [
    [0.0, '#eae7df'],   # Base Sand / Un-hunted
    [0.05, '#dcbfa6'],  # Soft Clay
    [0.3, '#c47b57'],   # Muted Terracotta
    [1.0, '#a64d3c']    # Deep Rust - High Intensity
]

debug_logs = []

# ==========================================
# 🗺️ ROBUST ITU CALLSIGN TO ISO-3 ROUTINE
# ==========================================
def callsign_to_iso3(call):
    call = str(call).upper().strip()

    # Comprehensive ITU / DXCC Prefix Mapping (Updated for R-digits, DA-DR, and LX)
    patterns = [
        (r'^(VU|AT|AU|AW|8T|8U|8V|8W|8X|8Y)', 'IND'),
        (r'^4S', 'LKA'), (r'^8Q', 'MDV'), (r'^9N', 'NPL'), (r'^S2', 'BGD'),
        (r'^(AP|AQ|AR|AS)', 'PAK'), (r'^V8', 'BRN'), (r'^(HS|E2)', 'THA'),
        (r'^(9M|9W)', 'MYS'), (r'^9V', 'SGP'), (r'^Y[B-H]', 'IDN'),
        (r'^(DU|DV|DW|DX|DY|DZ|4D|4E|4F|4G|4H|4I)', 'PHL'),
        (r'^(J[A-S]|7[J-N]|8[J-N])', 'JPN'),
        (r'^(HL|DS|DT|D7|D8|D9)', 'KOR'), (r'^B[A-Z]', 'CHN'),
        (r'^VR2', 'HKG'), (r'^XX9', 'MAC'), (r'^BV', 'TWN'),
        (r'^(W|K|N|A[A-K])', 'USA'),
        (r'^(V[A-G]|C[F-K]|C[Y-Z])', 'CAN'), (r'^X[A-I]', 'MEX'),
        (r'^(G|M|2[EWMDIU]|GX|MX|GB)', 'GBR'), (r'^D[A-R]', 'DEU'), # Catches DO, DL, DK, etc.
        (r'^F', 'FRA'), (r'^I', 'ITA'), (r'^E[A-H]', 'ESP'),
        (r'^C[Q-T]', 'PRT'), (r'^P[A-I]', 'NLD'),
        (r'^O[N-T]', 'BEL'), (r'^(HB9|HB0|HB)', 'CHE'),
        (r'^OE', 'AUT'), (r'^(S[A-M]|7S|8S)', 'SWE'), (r'^L[A-N]', 'NOR'),
        (r'^O[F-J]', 'FIN'), (r'^O[U-Z]', 'DNK'),
        (r'^(S[N-R]|3Z|HF)', 'POL'), (r'^O[K-L]', 'CZE'),
        (r'^OM', 'SVK'), (r'^H[A-G]', 'HUN'), (r'^Y[O-R]', 'ROU'),
        (r'^LZ', 'BGR'), (r'^(S[V-Z]|J4)', 'GRC'), (r'^T[A-C]', 'TUR'),
        (r'^(U[A-I]|R[A-Z0-9])', 'RUS'), # Catches RA-RZ, R0-R9, UA-UI
        (r'^U[R-Z]', 'UKR'),
        (r'^E[U-W]', 'BLR'), (r'^LY', 'LTU'), (r'^YL', 'LVA'),
        (r'^ES', 'EST'), (r'^Y[T-U]', 'SRB'), (r'^S5', 'SVN'),
        (r'^9A', 'HRV'), (r'^E7', 'BIH'), (r'^ZA', 'ALB'),
        (r'^VK', 'AUS'), (r'^ZL', 'NZL'), (r'^(P[P-Z]|Z[Y-Z])', 'BRA'),
        (r'^(L[U-W]|A[Y-Z])', 'ARG'), (r'^C[A-E]', 'CHL'),
        (r'^H[J-K]', 'COL'), (r'^Y[V-Y]', 'VEN'), (r'^CX', 'URY'),
        (r'^Z[S-U]', 'ZAF'), (r'^5Z', 'KEN'), (r'^SU', 'EGY'),
        (r'^CN', 'MAR'), (r'^4[X-Z]', 'ISR'), (r'^A6', 'ARE'),
        (r'^A4', 'OMN'), (r'^A7', 'QAT'), (r'^9K', 'KWT'),
        (r'^HZ', 'SAU'), (r'^U[N-Q]', 'KAZ'), (r'^LX', 'LUX') # Added Luxembourg
    ]
    for pattern, iso3 in patterns:
        if re.match(pattern, call): return iso3
    return 'UNK'

# ==========================================
# 🔌 CLOUDSCRAPER & DATA CRAWLER
# ==========================================
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
hunter_aggregation = {}

try:
    parks_resp = scraper.get("https://api.pota.app/program/parks/IN", timeout=15).json()
    activated_parks = [p['reference'] for p in parks_resp if p.get('activations', 0) > 0]
except Exception as e:
    activated_parks = []
    debug_logs.append(f"Error fetching parks: {e}")

if activated_parks:
    for ref in activated_parks:
        try:
            res = scraper.get(f"https://api.pota.app/park/leaderboard/{ref}", timeout=10)
            if res.status_code == 200:
                hunters = res.json().get('hunter_qsos', [])
                for h in hunters:
                    call = str(h.get('callsign')).upper().strip()
                    if call and call != 'NONE':
                        if call not in hunter_aggregation:
                            hunter_aggregation[call] = {'parks': set(), 'qsos': 0}
                        hunter_aggregation[call]['parks'].add(ref)
                        hunter_aggregation[call]['qsos'] += int(h.get('count', 1))
        except Exception:
            pass
        time.sleep(0.15)

hunter_records = []
for call, stats in hunter_aggregation.items():
    hunter_records.append({
        'callsign': call, 'unique_parks': len(stats['parks']),
        'total_qsos': stats['qsos'], 'iso3': callsign_to_iso3(call)
    })

hunter_stats = pd.DataFrame(hunter_records)

if not hunter_stats.empty:
    hunter_stats['origin'] = hunter_stats['iso3'].apply(lambda x: 'Domestic (VU)' if x == 'IND' else 'International (DX)')
else:
    hunter_stats = pd.DataFrame(columns=['callsign', 'unique_parks', 'total_qsos', 'iso3', 'origin'])

today_date = datetime.now().strftime("%d %b %Y")
base_footer = f'Data: POTA.app Leaderboard | <a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | Generated: {today_date}'

# ==========================================
# 📊 PIPELINE 1: THE DUAL-PLOT LANDSCAPE (FIG 8)
# ==========================================
if not hunter_stats.empty:
    fig8 = make_subplots(
        rows=1, cols=2, column_widths=[0.6, 0.4],
        specs=[[{"type": "bar"}, {"type": "pie"}]], horizontal_spacing=0.15
    )

    # Bar chart limits to top 15
    top_15 = hunter_stats.sort_values(by=['unique_parks', 'total_qsos'], ascending=[True, True]).tail(15)
    bar_colors = [vu_color if o == 'Domestic (VU)' else dx_color for o in top_15['origin']]

    fig8.add_trace(go.Bar(
        x=top_15['unique_parks'], y=top_15['callsign'],
        orientation='h', marker_color=bar_colors, customdata=top_15['total_qsos'],
        hovertemplate="<b>Hunter:</b> %{y}<br>Unique Parks: %{x}<br>Total QSOs: %{customdata}", name='', showlegend=False
    ), row=1, col=1)

    # Pie chart includes all data in hunter_stats
    geo_summary = hunter_stats.groupby('origin').size().reset_index(name='hunter_count')
    geo_summary = geo_summary.sort_values(by='origin', ascending=False)
    pie_colors = [vu_color if o == 'Domestic (VU)' else dx_color for o in geo_summary['origin']]

    fig8.add_trace(go.Pie(
        labels=geo_summary['origin'], values=geo_summary['hunter_count'], marker=dict(colors=pie_colors),
        textinfo='percent+label', hole=0.4, hoverinfo='label+value', showlegend=False
    ), row=1, col=2)

    fig8.update_layout(
        title=dict(text="The Hunter Landscape: Chasing Indian Parks", x=0.5, y=0.96, font=dict(family="Georgia, serif", size=22, color=text_color)),
        margin={"r":20, "t":100, "l":80, "b":130}, height=550, paper_bgcolor=paper_bg, plot_bgcolor=paper_bg, hovermode='closest',
        annotations=[dict(x=0.5, y=-0.25, xref='paper', yref='paper', text=base_footer, showarrow=False, font=dict(size=11, color='#78716c'), xanchor='center')]
    )

    fig8.update_xaxes(title=dict(text="Unique Parks Hunted", font=dict(family="Georgia, serif", size=12)), showgrid=True, gridcolor=grid_color, tickfont=dict(color=text_color), row=1, col=1)
    fig8.update_yaxes(type='category', tickfont=dict(family="Courier New, monospace", size=12, color=text_color), row=1, col=1)

    html_fig8 = fig8.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']})
    print("#+begin_export html")
    for log in debug_logs: print(f"")
    print("<figure id=\"fig:hunter-landscape\" class=\"img-full\">\n" + html_fig8 + "\n<figcaption><p><strong>Figure 8:</strong> Hunters of Indian POTA sites.</p></figcaption>\n</figure>\n#+end_export\n")

# ==========================================
# 🌍 PIPELINE 2: THE GLOBAL CHOROPLETH HEATMAP (FIG 9)
# ==========================================
if not hunter_stats.empty:
    # 'UNK' is intentionally kept in the aggregation
    world_data = hunter_stats.groupby('iso3').agg(
        total_qsos=('total_qsos', 'sum'), hunter_count=('callsign', 'count')
    ).reset_index()

    zmin_val, zmax_val = (world_data['total_qsos'].min(), world_data['total_qsos'].max()) if not world_data.empty else (0, 1)

    fig9 = go.Figure()

    india_data = world_data[world_data['iso3'] == 'IND']
    custom_india_loaded = False
    india_geojson = None
    state_names = []
    feature_key = 'properties.state_name'

    # 1. Fetch GeoJSON using native urllib (Bypasses scraper/requests CDN blocks)
    if not india_data.empty:
        try:
            req = urllib.request.Request(
                "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                india_geojson = json.loads(response.read().decode())

            first_props = india_geojson['features'][0]['properties']
            if 'state_name' in first_props:
                feature_key, name_key = 'properties.state_name', 'state_name'
            else:
                name_key = list(first_props.keys())[0]
                feature_key = f'properties.{name_key}'

            state_names = [feat['properties'][name_key] for feat in india_geojson['features']]
            custom_india_loaded = True
        except Exception as e:
            pass

    # 2. Build Base Map Data
    base_world_data = world_data[world_data['iso3'] != 'IND'] if custom_india_loaded else world_data

    # 3. Add Trace 1 (Global Base)
    fig9.add_trace(go.Choropleth(
        locations=base_world_data['iso3'], locationmode='ISO-3', z=base_world_data['total_qsos'],
        text=base_world_data['iso3'], customdata=base_world_data['hunter_count'],
        colorscale=terracotta_scale, zmin=zmin_val, zmax=zmax_val, autocolorscale=False, reversescale=False,
        marker_line_color='#bdae93', marker_line_width=0.6,
        colorbar=dict(title=dict(text="Confirmed QSOs", font=dict(family="Georgia, serif", size=12, color=text_color)), thickness=15, len=0.6, y=0.5, tickfont=dict(color=text_color, family="Georgia, serif")),
        hovertemplate="<b>Country ISO:</b> %{text}<br>Total Contacts: %{z:,}<br>Unique Hunters: %{customdata}",
    ))

    # 4. Add Trace 2 (India Overlay with full boundary compliance)
    if custom_india_loaded:
        india_qsos = india_data.iloc[0]['total_qsos']
        fig9.add_trace(go.Choropleth(
            geojson=india_geojson, locations=state_names, featureidkey=feature_key,
            z=[india_qsos] * len(state_names), colorscale=terracotta_scale, zmin=zmin_val, zmax=zmax_val,
            showscale=False, marker_line_color='#bdae93', marker_line_width=0.6, hoverinfo='skip'
        ))

    fig9.update_layout(
        title=dict(text="Global Chase Intensity: Total Confirmed QSOs", x=0.5, y=0.96, font=dict(family="Georgia, serif", size=22, color=text_color)),
        margin={"r":30, "t":100, "l":30, "b":120}, height=600, paper_bgcolor=paper_bg,
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', coastlinecolor=grid_color, landcolor=paper_bg, bgcolor=paper_bg, showcountries=True, countrycolor=grid_color),
        annotations=[dict(x=0.5, y=-0.12, xref='paper', yref='paper', text=base_footer, showarrow=False, font=dict(size=11, color='#78716c'), xanchor='center')]
    )

    html_fig9 = fig9.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']})
    print("#+begin_export html\n<figure id=\"fig:hunter-global-map\" class=\"img-full\">\n" + html_fig9 + "\n<figcaption><p><strong>Figure 9:</strong> Map of IN park hunters.</p></figcaption>\n</figure>\n#+end_export\n")

# ==========================================
# 📜 PIPELINE 3: COLLAPSIBLE MASTER TABLE
# ==========================================
print("#+begin_export html\n<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Master Hunter Leaderboard Table</summary>\n#+end_export\n")
print("#+CAPTION: Comprehensive Profile of Top Hunters for India POTA Parks\n#+NAME: tab:hunter-leaderboard-stats")
print("| Rank | Callsign | ISO | Classification | Unique Parks Hunted | Total Confirmed Contacts |\n|---|---|---|---|---|---|")

if not hunter_stats.empty:
    for rank, row in hunter_stats.sort_values(by=['unique_parks', 'total_qsos'], ascending=[False, False]).reset_index(drop=True).iterrows():
        print(f"| {rank + 1} | {row['callsign']} | {row['iso3']} | {row['origin']} | {int(row['unique_parks'])} | {int(row['total_qsos'])} |")
else:
    print("| - | No Active Hunter Data Discovered | - | - | - | - |")
print("\n#+begin_export html\n</details>\n#+end_export")
