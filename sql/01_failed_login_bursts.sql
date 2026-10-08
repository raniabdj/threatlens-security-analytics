-- High failure counts per source IP/user/hour (heuristic, not proof of compromise).
SELECT user_id, src_ip, substr(event_time,1,13) AS hour_utc,
       COUNT(*) AS failed_logins
FROM events
WHERE event_type='login' AND outcome='failure'
GROUP BY user_id, src_ip, substr(event_time,1,13)
HAVING COUNT(*) >= 5
ORDER BY failed_logins DESC;
