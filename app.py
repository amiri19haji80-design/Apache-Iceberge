import os
import test


WITH
old AS (
  SELECT toYYYYMM(interaction_date) AS ym, interaction_source AS src, uniqExact(call_id) AS calls
  FROM s3(factory,
          url = 'https://ecs-s3-fr-dev-direct.eu.net.intra/fr-dev-s3-v2-factory/staging/gold/crm_interactions/**',
          format = 'PARQUET')
  WHERE _path NOT LIKE '%spark-staging%' AND _path NOT LIKE '%_temporary%'
    AND interaction_date >= '2024-01-01' AND interaction_date <= today()
  GROUP BY 1, 2
),
new AS (
  SELECT toYYYYMM(interaction_date) AS ym, interaction_source AS src, uniqExact(call_id) AS calls
  FROM gamma.crm_interactions_gold
  WHERE interaction_date >= '2024-01-01' AND interaction_date <= today()
  GROUP BY 1, 2
)
SELECT COALESCE(o.ym, n.ym) AS ym, COALESCE(o.src, n.src) AS src,
       o.calls AS nucleus, n.calls AS core, n.calls - o.calls AS diff
FROM old o
FULL OUTER JOIN new n ON o.ym = n.ym AND o.src = n.src
ORDER BY ym, src;
