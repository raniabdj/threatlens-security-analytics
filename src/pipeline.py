"""Synthetic security telemetry analytics demo. No real customer data."""
import argparse
import csv
import json
import random
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUTS = ROOT / 'outputs'
SCHEMA = '''CREATE TABLE events (event_id INTEGER PRIMARY KEY, event_time TEXT NOT NULL, host TEXT NOT NULL, user_id TEXT NOT NULL, src_ip TEXT NOT NULL, event_type TEXT NOT NULL, outcome TEXT NOT NULL, process_name TEXT, destination_ip TEXT); CREATE INDEX idx_events_user_time ON events(user_id,event_time); CREATE INDEX idx_events_host ON events(host);'''

def generate(seed=42, normal_count=1200):
    rng = random.Random(seed)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    hosts = [f'workstation-{i:02d}' for i in range(1, 16)]
    users = [f'employee{i:02d}' for i in range(1, 21)]
    rows = []
    for i in range(normal_count):
        user = rng.choice(users)
        host = rng.choice(hosts)
        kind = rng.choices(['login', 'process', 'network'], [0.55, 0.25, 0.20])[0]
        outcome = ('failure' if rng.random() < 0.07 else 'success') if kind == 'login' else 'observed'
        rows.append((start + timedelta(minutes=rng.randrange(7*24*60)), host, user,
                     f'10.0.{rng.randrange(1,5)}.{rng.randrange(2,250)}', kind, outcome,
                     rng.choice(['explorer.exe','chrome.exe','python.exe']) if kind == 'process' else None,
                     f'203.0.113.{rng.randrange(1,250)}' if kind == 'network' else None))
    # Inject labelled scenario for reproducible validation: repeated failures then success.
    for i in range(14):
        rows.append((start + timedelta(days=3, hours=10, minutes=i), 'workstation-03', 'employee07',
                     '198.51.100.77', 'login', 'failure', None, None))
    rows.append((start + timedelta(days=3, hours=10, minutes=15), 'workstation-03', 'employee07',
                 '198.51.100.77', 'login', 'success', None, None))
    for i in range(8):
        rows.append((start + timedelta(days=4, hours=2, minutes=i), 'workstation-09', 'employee12',
                     '10.0.1.44', 'network', 'observed', None, '203.0.113.250'))
    rows.sort(key=lambda x: x[0])
    DATA.mkdir(exist_ok=True)
    with (DATA/'events.csv').open('w', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['event_id','event_time','host','user_id','src_ip','event_type','outcome','process_name','destination_ip'])
        for idx, r in enumerate(rows, 1):
            writer.writerow([idx, r[0].isoformat(), *r[1:]])
    return len(rows)

def load():
    conn = sqlite3.connect(DATA/'telemetry.sqlite')
    conn.executescript('DROP TABLE IF EXISTS events;'+SCHEMA)
    with (DATA/'events.csv').open(newline='') as f:
        records = list(csv.DictReader(f))
    conn.executemany('INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)', [tuple(row.values()) for row in records])
    conn.commit()
    return conn

def analyze(conn):
    OUTPUTS.mkdir(exist_ok=True)
    results={}
    for path in sorted((ROOT/'sql').glob('*.sql')):
        cur=conn.execute(path.read_text())
        columns=[x[0] for x in cur.description]
        results[path.stem]=[dict(zip(columns, r)) for r in cur.fetchall()]
    counts=dict(conn.execute('SELECT event_type, COUNT(*) FROM events GROUP BY event_type'))
    results['summary']={'total_events':sum(counts.values()), 'event_types':counts,
                        'note':'Detections are heuristics on synthetic data; not verified threats.'}
    (OUTPUTS/'findings.json').write_text(json.dumps(results, indent=2))
    for name, rows in results.items():
        if not isinstance(rows, list) or not rows: continue
        with (OUTPUTS/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return results

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args()
    count=generate(seed=args.seed)
    conn=load()
    results=analyze(conn)
    print(f'Generated and analysed {count} synthetic events.')
    for key, val in results.items():
        if isinstance(val,list): print(f'{key}: {len(val)} rows')
    conn.close()

if __name__=='__main__': main()
