import json, glob, re, csv, statistics as st
from collections import defaultdict

def load(path):
    txt = open(path).read()
    return json.loads(txt[txt.index('{'):])   # skip any text before the JSON

data = defaultdict(list)
for f in sorted(glob.glob('results/case*_qd*_run*.json')):
    c, qd, rep = re.search(r'case(\w)_qd(\d+)_run(\d+)', f).groups()
    j = load(f)['jobs'][0]
    r, w = j['read'], j['write']
    def pct(d, p):
        return d['clat_ns']['percentile'][p] / 1000 if d['io_bytes'] else 0
    def avg(d):
        return d['lat_ns']['mean'] / 1000 if d['io_bytes'] else 0
    data[(c, int(qd))].append({
        'iops': r['iops'] + w['iops'],
        'bw_mib': (r['bw'] + w['bw']) / 1024,
        'r_avg': avg(r), 'r_p95': pct(r, '95.000000'), 'r_p99': pct(r, '99.000000'),
        'w_avg': avg(w), 'w_p95': pct(w, '95.000000'), 'w_p99': pct(w, '99.000000'),
    })

keys = ['iops','bw_mib','r_avg','r_p95','r_p99','w_avg','w_p95','w_p99']
with open('summary.csv', 'w', newline='') as fh:
    wr = csv.writer(fh)
    wr.writerow(['case','qd','runs'] + [k+'_mean' for k in keys] + ['iops_stdev'])
    for (c, qd) in sorted(data):
        runs = data[(c, qd)]
        means = [st.mean(x[k] for x in runs) for k in keys]
        sd = st.stdev(x['iops'] for x in runs) if len(runs) > 1 else 0
        wr.writerow([c, qd, len(runs)] + [round(m, 1) for m in means] + [round(sd, 1)])

print(f"{'case':<5}{'qd':<4}{'IOPS':>9}{'BW MiB/s':>10}{'rd avg':>9}{'rd p95':>9}{'rd p99':>9}{'wr p99':>9}{'IOPS sd':>9}")
for (c, qd) in sorted(data):
    runs = data[(c, qd)]
    m = {k: st.mean(x[k] for x in runs) for k in keys}
    sd = st.stdev(x['iops'] for x in runs)
    print(f"{c:<5}{qd:<4}{m['iops']:>9.0f}{m['bw_mib']:>10.1f}{m['r_avg']:>9.0f}{m['r_p95']:>9.0f}{m['r_p99']:>9.0f}{m['w_p99']:>9.0f}{sd:>9.0f}")
