# ThreatLens — Synthetic Security Telemetry Analytics

A reproducible **Python + SQLite security-data analytics** portfolio project inspired by the analytical skills required in cybersecurity data analyst roles. **Independent educational project; not affiliated with CrowdStrike.** Uses **100% synthetic telemetry**, not customer logs or real threat intelligence.

## Business question
How can an analyst convert raw endpoint-style events into daily operational KPIs and investigation leads without treating every anomaly as an actual attack?

## Architecture
`Seeded synthetic event generator → CSV ingestion → SQLite (indexed) → SQL detection queries → JSON/CSV findings`

## Features
- Deterministic generation of 1,223 events (1,200 baseline + 23 injected scenario events) across login, process and network event types
- Hourly failed-login burst query, success-after-failures correlation, repeated destination analysis, and daily KPIs
- Parameterized seeded generator, reproducible outputs, and unit tests
- No external dependencies, API keys or cloud charges

## Run
Requires Python 3.10+.
```bash
python src/pipeline.py
python -m unittest discover -s tests -v
```
Inspect `outputs/findings.json` and the CSV files in `outputs/`. The synthetic source data is in `data/events.csv`.

## Analysis approach
- **Signal 1:** >=5 failed logins for one user/source IP within the same UTC hour.
- **Signal 2:** a successful login preceded by >=5 failures from the same user/source IP in the prior 30 minutes.
- **Signal 3:** >=5 network observations for a destination IP from one host.
- **KPI:** daily login failure rate and event volume.

These thresholds are **illustrative heuristics**, not production-calibrated detections. NAT, service accounts, noisy applications and normal retries can create false positives. No maliciousness is inferred solely from a detection.

## Data dictionary
| Column | Meaning |
|---|---|
| event_id | Unique integer |
| event_time | UTC ISO 8601 timestamp |
| host | Synthetic endpoint identifier |
| user_id | Synthetic account identifier |
| src_ip | Documentation-only or RFC1918 address |
| event_type | login, process, network |
| outcome | success, failure, observed |
| process_name | Optional process name |
| destination_ip | Optional documentation-only destination |

## Data-quality checks
- Reproducible row counts and output for a fixed random seed
- Primary key and NOT NULL constraints on core identifiers
- Automated assertions that injected scenarios are detected
- SQL NULL handling for missing network destinations and daily KPI denominator

## Limitations and next steps
- Synthetic and low-volume: **not evidence of large-scale telemetry expertise**
- SQLite relational queries only: **not a graph database project**
- No real MITRE ATT&CK technique mapping or validated threat intelligence
- Future work: add ground-truth labels, precision/recall evaluation, graph relationships, partitioned Parquet, larger datasets and a dashboard

## How to describe this on a CV (after running and understanding it)
**Security Telemetry Analytics (independent portfolio):** Implemented a reproducible Python/SQLite pipeline generating synthetic authentication, process and network events; developed SQL queries to surface suspicious patterns and report daily operational KPIs; validated expected scenarios with automated tests. *Educational simulation, not production security experience.*
