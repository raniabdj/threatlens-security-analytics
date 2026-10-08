-- KPI framework: event volume and authentication failure rate by UTC date.
SELECT substr(event_time,1,10) AS day_utc, COUNT(*) AS total_events,
 SUM(CASE WHEN event_type='login' THEN 1 ELSE 0 END) AS login_events,
 SUM(CASE WHEN event_type='login' AND outcome='failure' THEN 1 ELSE 0 END) AS failed_logins,
 ROUND(100.0*SUM(CASE WHEN event_type='login' AND outcome='failure' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN event_type='login' THEN 1 ELSE 0 END),0),2) AS failure_rate_pct
FROM events GROUP BY substr(event_time,1,10) ORDER BY day_utc;
