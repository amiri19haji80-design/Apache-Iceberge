import os
import test


SELECT currentUser(), hostName(), version();

SHOW DATABASES;

SELECT database, name, total_rows
FROM system.tables
WHERE database NOT IN ('system', 'INFORMATION_SCHEMA', 'information_schema')
ORDER BY database, name
LIMIT 300;
