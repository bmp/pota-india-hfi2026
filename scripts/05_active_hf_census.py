"""05_active_hf_census: extracted from the "Status of POTA in India" post.

Prints Org-mode/HTML output to stdout, as run from Org Babel.
"""
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import io
import re
import time
from datetime import datetime, timedelta
import zipfile
import gzip

# --- CENTRALIZED CONFIGURATION ---
strict_vu_pattern = r'^(?:VU|AT|AU|AW|8T|8U|8V|8W|8X|8Y)\d{1,2}[A-Z]{1,4}$'
html_vu_pattern = r'\b(?:VU|AT|AU|AW|8T|8U|8V|8W|8X|8Y)\d{1,2}[A-Z]{1,4}\b'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

now = datetime.now()
yesterday = now - timedelta(days=1)
cutoff_date = pd.to_datetime(f'{now.year - 3}-01-01')
years = [now.year - 2, now.year - 1, now.year]

# --- NETWORK HARDENING ---
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

data_sources = []
successful_urls = set()

# ==========================================
# 🗄️ BUCKET 1: LOGBOOK OF THE WORLD (LOTW)
# ==========================================
lotw_set = set()
try:
    lotw_url = "https://lotw.arrl.org/lotw-user-activity.csv"
    response = session.get(lotw_url, headers=headers, timeout=30)
    if response.status_code == 200:
        successful_urls.add(lotw_url)
        df = pd.read_csv(io.StringIO(response.text), names=['callsign', 'last_date', 'last_time'], on_bad_lines='skip')
        df['callsign'] = df['callsign'].astype(str).str.upper().str.strip()
        vu_df = df[df['callsign'].str.match(strict_vu_pattern, na=False)].copy()
        vu_df['last_date'] = pd.to_datetime(vu_df['last_date'], errors='coerce')
        lotw_set = set(vu_df[vu_df['last_date'] >= cutoff_date]['callsign'].unique())
except Exception:
    pass
data_sources.append({'name': 'Logbook of The World (LoTW)', 'set': lotw_set})

# ==========================================
# 📻 BUCKET 2: PARKS ON THE AIR (POTA)
# ==========================================
pota_set = set()
try:
    pota_index = "https://api.pota.app/program/parks/IN"
    parks_resp = session.get(pota_index, headers=headers, timeout=30)
    if parks_resp.status_code == 200:
        successful_urls.add(pota_index)
        activated_parks = [p['reference'] for p in parks_resp.json() if p.get('activations', 0) > 0]
        for ref in activated_parks:
            pota_url = f"https://api.pota.app/park/leaderboard/{ref}"
            res = session.get(pota_url, headers=headers, timeout=15)
            if res.status_code == 200:
                successful_urls.add(pota_url)
                for cat in ['activations', 'activator_qsos', 'hunter_qsos']:
                    for rec in res.json().get(cat, []):
                        call = str(rec.get('callsign', '')).upper().strip()
                        if re.match(strict_vu_pattern, call):
                            pota_set.add(call)
            time.sleep(0.05)
except Exception:
    pass
data_sources.append({'name': 'Parks on the Air (POTA)', 'set': pota_set})

# ==========================================
# 🏆 BUCKET 3: GLOBAL CONTEST ARCHIVES
# ==========================================
# 3A: Static URLs (CQ Contests)
static_contest_configs = {
    'CQ WPX SSB': ["https://cqwpx.com/logs_received_ssb.htm"] + [f"https://cqwpx.com/publiclogs/{y}ph/" for y in years],
    'CQ WPX CW': ["https://cqwpx.com/logs_received_cw.htm"] + [f"https://cqwpx.com/publiclogs/{y}cw/" for y in years],
    'CQ WW SSB': ["https://cqww.com/logs_received_ssb.htm"] + [f"https://cqww.com/publiclogs/{y}ph/" for y in years],
    'CQ WW CW': ["https://cqww.com/logs_received_cw.htm"] + [f"https://cqww.com/publiclogs/{y}cw/" for y in years],
    'CQ WW RTTY': ["https://cqwwrtty.com/logs_received.htm"] + [f"https://cqwwrtty.com/publiclogs/{y}/" for y in years],
    'CQ WPX RTTY': ["https://cqwpxrtty.com/logs_received.htm"] + [f"https://cqwpxrtty.com/publiclogs/{y}/" for y in years],
    'CQ 160 CW': ["https://cq160.com/logs_received_cw.htm"] + [f"https://cq160.com/publiclogs/{y}cw/" for y in years],
    'CQ 160 SSB': ["https://cq160.com/logs_received_ssb.htm"] + [f"https://cq160.com/publiclogs/{y}ph/" for y in years]
}

for contest_name, urls in static_contest_configs.items():
    c_set = set()
    for url in urls:
        try:
            res = session.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                successful_urls.add(url)
                c_set.update(m.upper().strip() for m in re.findall(html_vu_pattern, res.text, re.IGNORECASE))
        except Exception:
            pass
        time.sleep(0.1)
    data_sources.append({'name': contest_name, 'set': c_set})

# 3B: Dynamic URLs (ARRL & IARU Contests)
arrl_contests = {
    'IARU HF Champ': 'iaruhf',
    'ARRL DX CW': 'dxcw',
    'ARRL DX SSB': 'dxph',
    'ARRL RTTY Roundup': 'rttyru',
    'ARRL 160M': '160m',
    'ARRL Sweepstakes CW': 'sscw',
    'ARRL Sweepstakes SSB': 'ssph',
    'ARRL Int. Digital': 'dig',
    'ARRL 10M': '10m'
}

for name, cn in arrl_contests.items():
    c_set = set()
    try:
        index_url = f"https://contests.arrl.org/publiclogs.php?cn={cn}"
        res = session.get(index_url, headers=headers, timeout=15)
        if res.status_code == 200:
            instance_links = set(re.findall(r'publiclogs\.php\?eid=\d+&amp;iid=\d+|publiclogs\.php\?eid=\d+&iid=\d+', res.text))
            for link in instance_links:
                link = link.replace('&amp;', '&')
                log_url = f"https://contests.arrl.org/{link}"
                log_res = session.get(log_url, headers=headers, timeout=15)
                if log_res.status_code == 200:
                    successful_urls.add(log_url)
                    c_set.update(m.upper().strip() for m in re.findall(html_vu_pattern, log_res.text, re.IGNORECASE))
                time.sleep(0.1)
    except Exception:
        pass
    data_sources.append({'name': name, 'set': c_set})


# ==========================================
# 📡 BUCKET 4: LIVE SPOTTING NETWORKS (RBN / PSK / WSPR)
# ==========================================
rbn_set = set()
try:
    rbn_url = f"http://www.reversebeacon.net/raw_data/dl.php?f={yesterday.strftime('%Y%m%d')}"
    r = session.get(rbn_url, headers=headers, timeout=60)
    if r.status_code == 200 and len(r.content) > 1000:
        successful_urls.add(rbn_url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            with z.open(z.namelist()[0]) as f:
                for line in f:
                    for m in re.findall(html_vu_pattern, line.decode('utf-8', errors='ignore'), re.IGNORECASE):
                        rbn_set.add(m.upper().strip())
except Exception:
    pass
data_sources.append({'name': 'Reverse Beacon Network (24h)', 'set': rbn_set})

psk_set = set()
try:
    psk_url = "https://retrieve.pskreporter.info/query?senderCallsign=VU*&lastXSeconds=86400"
    r = session.get(psk_url, headers=headers, timeout=30)
    if r.status_code == 200:
        successful_urls.add(psk_url)
        psk_set.update(m.upper().strip() for m in re.findall(html_vu_pattern, r.text, re.IGNORECASE))
except Exception:
    pass
data_sources.append({'name': 'PSKReporter (24h)', 'set': psk_set})

wspr_set = set()
try:
    first_of_this_month = now.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    two_months_ago = last_month.replace(day=1) - timedelta(days=1)

    wspr_url = f"http://wsprnet.org/archive/wsprspots-{last_month.strftime('%Y-%m')}.csv.gz"
    r = session.get(wspr_url, headers=headers, timeout=60)

    if r.status_code == 404:
        wspr_url = f"http://wsprnet.org/archive/wsprspots-{two_months_ago.strftime('%Y-%m')}.csv.gz"
        r = session.get(wspr_url, headers=headers, timeout=60)

    if r.status_code == 200:
        successful_urls.add(wspr_url)
        with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as gz:
            for line in gz:
                for m in re.findall(html_vu_pattern, line.decode('utf-8', errors='ignore'), re.IGNORECASE):
                    wspr_set.add(m.upper().strip())
except Exception:
    pass
data_sources.append({'name': 'WSPRnet (Recent Archive)', 'set': wspr_set})


# ==========================================
# 📊 FINAL ORG-MODE TABLE OUTPUT
# ==========================================
print("#+CAPTION: Unified Active VU HF Operators Census [fn:data_sources]")
print("#+NAME: tab:active-census-report")
print("| Data Source / Metric | Total Discovered | Extracted Unique |")
print("|---|---|---|")

cumulative_set = set()

for source in data_sources:
    total_found = len(source['set'])
    new_unique = len(source['set'] - cumulative_set)
    cumulative_set.update(source['set'])
    print(f"| {source['name']} | {total_found} | +{new_unique} |")

print("|---|---|---|")
print(f"| *Total De-duplicated Active VU Population* | - | *{len(cumulative_set)}* |")
print("\n")

# Print the successful URLs as an Org Footnote
print("[fn:data_sources] Data successfully aggregated and verified from the following live endpoints:")
for url in sorted(successful_urls):
    print(f"- {url}")
