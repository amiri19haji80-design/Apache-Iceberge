import os



cat > profile_month.py <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.engines.spark_session import SparkSessionManager
lines = []
for l in open("main.py", encoding="utf-8"):
    if "executor.run(" in l: break
    lines.append(l)
ns = {"__name__": "x"}; exec("".join(lines), ns); ex = ns["executor"]
m = SparkSessionManager(secret_resolver=ex._secret_resolver, mapping_resolver=ex._mapping,
    spark_config=None, enable_clickhouse_catalog=False, resource_config=None, external_s3_buckets=[])
with m.session(layer="beta", source_name="profile") as spark:
    spark.sql("""SELECT date_format(interaction_date,'yyyy-MM') AS month,
                        count(*) AS rows_total,
                        count(DISTINCT CASE WHEN interaction_source='CRM+'     THEN call_id END) AS crm_plus,
                        count(DISTINCT CASE WHEN interaction_source='CRM CE'   THEN call_id END) AS crm_ce,
                        count(DISTINCT CASE WHEN interaction_source='Eventogy' THEN call_id END) AS eventogy
                 FROM polaris.gamma.crm_interactions_gold
                 WHERE interaction_date >= '2024-01-01' AND interaction_date < '2026-11-01'
                 GROUP BY 1 ORDER BY 1""").show(40, False)
PY
python profile_month.py > pm.log 2>&1; grep -E "^\|" pm.log
