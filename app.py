import os 
import test 



cd ~/work/core/pipelines/projects/interactions
grep -rn -i "to_date\|to_timestamp" sql/ | grep -i "MMM"




-- line 4
TO_DATE(SUBSTR(meeting_date, 1, 11), 'dd-MMM-yyyy') AS meeting_date,
-- line 23
TO_DATE(SUBSTR(created, 1, 11), 'dd-MMM-yyyy') AS created,
-- line 24
TO_DATE(SUBSTR(last_upd, 1, 11), 'dd-MMM-yyyy') AS last_upd,



