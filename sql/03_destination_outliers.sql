-- Unusually repeated network destinations per host (simple volume threshold).
SELECT host, destination_ip, COUNT(*) AS connections
FROM events
WHERE event_type='network' AND destination_ip IS NOT NULL
GROUP BY host, destination_ip
HAVING COUNT(*) >= 5
ORDER BY connections DESC;
