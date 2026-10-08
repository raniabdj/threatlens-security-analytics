-- Successful login after >= 5 failures from the same user/IP in prior 30 minutes.
SELECT s.event_id, s.event_time, s.user_id, s.src_ip,
       (SELECT COUNT(*) FROM events f
        WHERE f.event_type='login' AND f.outcome='failure'
          AND f.user_id=s.user_id AND f.src_ip=s.src_ip
          AND f.event_time BETWEEN strftime('%Y-%m-%dT%H:%M:%S+00:00',s.event_time,'-30 minutes') AND s.event_time) AS preceding_failures
FROM events s
WHERE s.event_type='login' AND s.outcome='success'
  AND (SELECT COUNT(*) FROM events f
       WHERE f.event_type='login' AND f.outcome='failure'
         AND f.user_id=s.user_id AND f.src_ip=s.src_ip
         AND f.event_time BETWEEN strftime('%Y-%m-%dT%H:%M:%S+00:00',s.event_time,'-30 minutes') AND s.event_time) >= 5
ORDER BY preceding_failures DESC;
