import os 
import test 



cd ~/work/core/pipelines/projects/interactions
F=$(grep -A3 "name: fact_all_interactions" tasks.yaml >/dev/null; grep -rl "plus_fact_meeting" sql/ | head -1); echo "FILE: $F"
grep -n -i "union\|interaction_source\|'CRM\|'Eventogy\|plus_fact_meeting\|where\|>= \|<= \|cutoff\|date" "$F"



cd ~/work/core
cat > profile_calls.py <<'PY'
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
    print("== crm_plus.fact_meeting: distinct calls, id prefix, date range")
    spark.sql("""SELECT substr(call_id,1,2) AS prefix, count(DISTINCT call_id) calls
                 FROM polaris.beta.trusted.crm_plus.fact_meeting GROUP BY 1 ORDER BY 2 DESC LIMIT 10""").show(truncate=False)
    print("== fact_all_interactions: id prefix per source")
    spark.sql("""SELECT interaction_source, substr(call_id,1,2) AS prefix, count(DISTINCT call_id) calls
                 FROM polaris.beta.trusted.crm_plus.fact_all_interactions GROUP BY 1,2 ORDER BY 1,3 DESC""").show(50, truncate=False)
PY
python profile_calls.py > prof2.log 2>&1; grep -vE "WARN|SLF4J|WARNING|Setting|adjust|INFO|Stage" prof2.log
