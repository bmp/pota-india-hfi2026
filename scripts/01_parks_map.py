"""01_parks_map: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Full name mapping for ISO-3166-2 state codes
state_map = {
    'IN-AN': 'Andaman and Nicobar', 'IN-AP': 'Andhra Pradesh', 'IN-AR': 'Arunachal Pradesh',
    'IN-AS': 'Assam', 'IN-BR': 'Bihar', 'IN-CH': 'Chandigarh', 'IN-CT': 'Chhattisgarh',
    'IN-DN': 'Dadra and Nagar Haveli', 'IN-DL': 'Delhi', 'IN-GA': 'Goa', 'IN-GJ': 'Gujarat',
    'IN-HR': 'Haryana', 'IN-HP': 'Himachal Pradesh', 'IN-JK': 'Jammu and Kashmir',
    'IN-JH': 'Jharkhand', 'IN-KA': 'Karnataka', 'IN-KL': 'Kerala', 'IN-LA': 'Ladakh',
    'IN-LD': 'Lakshadweep', 'IN-MP': 'Madhya Pradesh', 'IN-MH': 'Maharashtra',
    'IN-MN': 'Manipur', 'IN-ML': 'Meghalaya', 'IN-MZ': 'Mizoram', 'IN-NL': 'Nagaland',
    'IN-OD': 'Odisha', 'IN-PY': 'Puducherry', 'IN-PB': 'Punjab', 'IN-RJ': 'Rajasthan',
    'IN-SK': 'Sikkim', 'IN-TN': 'Tamil Nadu', 'IN-TS': 'Telangana', 'IN-TR': 'Tripura',
    'IN-UP': 'Uttar Pradesh', 'IN-UK': 'Uttarakhand', 'IN-WB': 'West Bengal'
}

def fetch_india_pota_parks():
    url = "https://api.pota.app/program/parks/IN"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            if 'activations' in df.columns:
                df['activations'] = pd.to_numeric(df['activations'], errors='coerce').fillna(0)

            # Convert state codes to full names for the table and tooltips
            if 'locationDesc' in df.columns:
                df['StateName'] = df['locationDesc'].map(state_map).fillna(df['locationDesc'])
            else:
                df['StateName'] = 'Unknown'
            return df
    return pd.DataFrame()

pota_df = fetch_india_pota_parks()

# 1. Fetch the complete GeoJSON vector outline of India
geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
india_geojson = requests.get(geojson_url).json()

first_props = india_geojson['features'][0]['properties']
if 'state_name' in first_props:
    feature_key, name_key = 'properties.state_name', 'state_name'
else:
    name_key = list(first_props.keys())[0]
    feature_key = f'properties.{name_key}'

state_names = [feat['properties'][name_key] for feat in india_geojson['features']]

# ==========================================
# 🎨 HIGHLY MUTED VINTAGE PALETTE
# ==========================================
paper_bg = '#f7f6f1'        # Very pale, delicate ivory
wash_color = '#c4beba'      # Desaturated, soft stone-grey wash
wet_edge = '#9e9690'        # Softer edge tone to blend beautifully
crimson_dot = '#c46060'     # Soft crimson for unactivated sites
watercolour_green = '#5a7a68' # Muted watercolour green for activated sites

fig = go.Figure()

# 2. Draw the vector outline of India
fig.add_trace(go.Choropleth(
    geojson=india_geojson,
    locations=state_names,
    featureidkey=feature_key,
    z=[1] * len(state_names),
    colorscale=[[0, wash_color], [1, wash_color]],
    showscale=False,
    marker_line_color=wet_edge,
    marker_line_width=1.0,
    hoverinfo='skip'
))

# 3. Overlay the POTA Parks
if not pota_df.empty:
    plot_df = pota_df.dropna(subset=['latitude', 'longitude']).copy()

    # Segregate tracking subsets
    activated_df = plot_df[plot_df['activations'] > 0]
    unactivated_df = plot_df[plot_df['activations'] == 0]

    # Trace 3a: Unactivated Parks (Crimson)
    if not unactivated_df.empty:
        hover_text_unact = unactivated_df['reference'] + "<br>" + unactivated_df['name'] + "<br>" + unactivated_df['StateName'] + "<br>Activations: " + unactivated_df['activations'].astype(int).astype(str)
        sizes_unact = (unactivated_df['activations'] ** 0.5) * 3.5 + 6

        fig.add_trace(go.Scattergeo(
            lon=unactivated_df['longitude'],
            lat=unactivated_df['latitude'],
            text=hover_text_unact,
            mode='markers',
            customdata=unactivated_df['reference'],
            name='Unactivated Sites',
            marker=dict(
                size=sizes_unact,
                color=crimson_dot,
                opacity=0.95,
                line=dict(width=1, color=paper_bg)
            ),
            hoverinfo='text'
        ))

    # Trace 3b: Activated Parks (Muted Watercolour Green)
    if not activated_df.empty:
        hover_text_act = activated_df['reference'] + "<br>" + activated_df['name'] + "<br>" + activated_df['StateName'] + "<br>Activations: " + activated_df['activations'].astype(int).astype(str)
        sizes_act = (activated_df['activations'] ** 0.5) * 3.5 + 6

        fig.add_trace(go.Scattergeo(
            lon=activated_df['longitude'],
            lat=activated_df['latitude'],
            text=hover_text_act,
            mode='markers',
            customdata=activated_df['reference'],
            name='Activated Sites',
            marker=dict(
                size=sizes_act,
                color=watercolour_green,
                opacity=0.95,
                line=dict(width=1, color=paper_bg)
            ),
            hoverinfo='text'
        ))

# 4. Configure layout
fig.update_geos(
    fitbounds="locations",
    visible=False,
    projection_type="mercator",
    bgcolor=paper_bg
)

# Build the Footer Text
today_date = datetime.now().strftime("%d %b %Y")
footer_text = (
    f'Data: <a href="https://api.pota.app" target="_blank">POTA.app</a> | '
    f'<a href="https://ham.bharathpalavalli.com" target="_blank">ham.bharathpalavalli.com</a> | '
    f'Generated: {today_date} | VU3GLJ'
)

fig.update_layout(
    title=dict(
        text="POTA Sites in India",
        x=0.5,
        font=dict(
            family="Georgia, 'Times New Roman', Times, serif",
            size=24,
            color='#44403c'
        )
    ),
    margin={"r":0, "t":60, "l":0, "b":60},
    height=650,
    paper_bgcolor=paper_bg,
    plot_bgcolor=paper_bg,
    dragmode="pan",
    showlegend=True,
    legend=dict(
        orientation="h",
        x=0.5,
        y=0.02,
        xanchor="center",
        yanchor="bottom",
        font=dict(family="Georgia, serif", size=11, color='#44403c'),
        bgcolor="rgba(247, 246, 241, 0.8)"
    ),
    annotations=[
        dict(
            x=0.5, y=-0.08,
            xref='paper', yref='paper',
            text=footer_text,
            showarrow=False,
            font=dict(size=12, color='#78716c')
        )
    ]
)

# 5. Export HTML with the SVG Download Fix
html_out = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='pota_india_map', config={
    'scrollZoom': True,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'svg',
        'filename': 'POTA_India_Map'
    },
    'displaylogo': False
})

# 6. JavaScript to make the dots clickable
click_js = """
<script>
    var mapDiv = document.getElementById('pota_india_map');
    mapDiv.on('plotly_click', function(data){
        var ref = data.points[0].customdata;
        if(ref){
            window.open('https://pota.app/#/park/' + ref, '_blank');
        }
    });
</script>
"""

# 7. Output the Map and JS
print("#+begin_export html")
print('<figure id="fig:pota-map" class="img-full">')
print(html_out)
print(click_js)
print('<figcaption><p><strong>Figure 1:</strong> Interactive Map of POTA Sites in India</p></figcaption>')
print('</figure>')
print("#+end_export\n")

# 8. Output the Org-Mode Data Table
if not pota_df.empty:

    # Calculate Summary Stats grouping by the newly mapped Full State Name
    df_summary = pota_df.groupby('StateName').agg(
        Total_Parks=('reference', 'count'),
        Activated=('activations', lambda x: (x > 0).sum()),
        Total_Activations=('activations', 'sum')
    ).reset_index()

    df_summary.rename(columns={'StateName': 'State / Region'}, inplace=True)

    # Sort by highest number of total activations, then by total parks
    df_summary = df_summary.sort_values(by=['Total_Activations', 'Total_Parks'], ascending=[False, False])

    print("#+begin_export html")
    print("<details style=\"margin-top: 1rem; margin-bottom: 2rem;\"><summary style=\"cursor: pointer; font-weight: bold; color: var(--table-strong); text-align: center; margin-bottom: 1rem;\">Click to view/hide Map Data Table</summary>")
    print("#+end_export\n")

    print("#+CAPTION: Statewise Breakdown of POTA Parks and Activations")
    print("#+NAME: tab:statewise-activations")
    # Print the Org Table
    print("| State / Region | Total Parks | Activated Parks | Total Activations |")
    print("|---|---|---|---|")

    for _, row in df_summary.iterrows():
        print(f"| {row['State / Region']} | {row['Total_Parks']} | {row['Activated']} | {int(row['Total_Activations'])} |")

    print("\n#+begin_export html")
    print("</details>")
    print("#+end_export")
