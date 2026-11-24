import json, sys, time, pathlib, requests
out = pathlib.Path(sys.argv[1])
H = {'User-Agent': 'Mozilla/5.0 (VU3GLJ POTA-India analysis)'}
s = requests.Session(); s.headers.update(H)
def get(url):
    for i in range(4):
        try:
            r = s.get(url, timeout=30)
            if r.status_code == 200: return r.json()
            print('HTTP', r.status_code, url, file=sys.stderr)
        except Exception as e:
            print('ERR', e, url, file=sys.stderr)
        time.sleep(2 * (i + 1))
    return None
parks = get("https://api.pota.app/program/parks/IN")
json.dump(parks, open(out / 'parks_IN.json', 'w'))
acts, boards = {}, {}
for p in parks:
    if (p.get('activations') or 0) > 0:
        ref = p['reference']
        acts[ref] = get(f"https://api.pota.app/park/activations/{ref}?count=5000")
        boards[ref] = get(f"https://api.pota.app/park/leaderboard/{ref}")
        time.sleep(0.2)
json.dump(acts, open(out / 'activations.json', 'w'))
json.dump(boards, open(out / 'leaderboards.json', 'w'))
print(len(parks), 'parks;', len(acts), 'activated parks fetched;', sum(v is None for v in acts.values()), 'activation fetch failures;', sum(v is None for v in boards.values()), 'leaderboard failures')
