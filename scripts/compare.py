import json, sys, collections, re
d = sys.argv[1]
parks = json.load(open(f'{d}/parks_IN.json'))
acts = json.load(open(f'{d}/activations.json'))
boards = json.load(open(f'{d}/leaderboards.json'))
recs = []
for ref, lst in acts.items():
    for a in lst or []:
        recs.append(dict(ref=ref, call=str(a['activeCallsign']).upper(), date=a['qso_date'], q=int(a.get('totalQSOs') or 0)))
def stats(cut):
    r = [x for x in recs if x['date'] <= cut]
    ok = [x for x in r if x['q'] >= 10]
    calls = collections.Counter(x['call'] for x in r)
    okcalls = {x['call'] for x in ok}
    yearly = collections.Counter(x['date'][:4] for x in r)
    return dict(attempts=len(r), successful=len(ok), activators=len(calls), successful_activators=len(okcalls),
                parks_attempted=len({x['ref'] for x in r}), parks_activated=len({x['ref'] for x in ok}),
                vu2=len({c for c in calls if c.startswith('VU2')}), vu3=len({c for c in calls if c.startswith('VU3')}),
                yearly=dict(sorted(yearly.items())))
for cut in ['20260709', '20260710', '20260713']:
    print(cut, stats(cut))
now = stats('99999999'); print('NOW', now)
print('parks listed', len(parks), '| park-level sum activations', sum(p['activations'] for p in parks), '| parks with activations>0', sum(p['activations'] > 0 for p in parks))
# changes since July cutoff
cut = '20260713'
new = sorted([x for x in recs if x['date'] > cut], key=lambda x: x['date'])
print('\nNEW RECORDS since', cut, len(new))
names = {p['reference']: (p['name'], p['locationDesc']) for p in parks}
for x in new: print(' ', x['date'], x['ref'], names[x['ref']], x['call'], x['q'])
before_ok = {x['ref'] for x in recs if x['date'] <= cut and x['q'] >= 10}
after_ok = {x['ref'] for x in recs if x['q'] >= 10}
print('first-time activated parks:', [(r, names[r]) for r in sorted(after_ok - before_ok)])
before_calls = {x['call'] for x in recs if x['date'] <= cut}
print('new activators:', sorted({x['call'] for x in recs} - before_calls))
print('new parks listed (ref > IN-0191 or not in July count):', [(p['reference'], p['name'], p['locationDesc']) for p in parks if int(p['reference'][3:]) > 191])
# hunters
agg = {}
for ref, b in boards.items():
    for h in (b or {}).get('hunter_qsos', []):
        c = str(h.get('callsign')).upper().strip()
        if c and c != 'NONE':
            agg.setdefault(c, [set(), 0]); agg[c][0].add(ref); agg[c][1] += int(h.get('count', 1))
vu = [c for c in agg if re.match(r'^(VU|AT|AU|AW|8T|8U|8V|8W|8X|8Y)', c)]
print('\nhunters', len(agg), 'domestic', len(vu), 'DX share %.1f%%' % (100 * (len(agg) - len(vu)) / len(agg)))
top = sorted(agg.items(), key=lambda kv: (-len(kv[1][0]), -kv[1][1]))[:6]
print('top hunters', [(c, len(v[0]), v[1]) for c, v in top])
# activator leaderboard now
ac = collections.defaultdict(lambda: [0, 0, set()])
for x in recs:
    ac[x['call']][0] += 1; ac[x['call']][1] += x['q'] >= 10; ac[x['call']][2].add(x['ref'])
print('top activators now', sorted([(c, v[0], v[1], len(v[2])) for c, v in ac.items()], key=lambda t: -t[1])[:6])
