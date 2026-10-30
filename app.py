import os
import test


SELECT hostName();

SELECT engine, total_rows FROM system.tables
WHERE database = 'gamma' AND name = 'crm_interactions_gold';

SELECT hostName() AS host, count() AS rows
FROM clusterAllReplicas('serving', gamma.crm_interactions_gold)
GROUP BY host ORDER BY host;
