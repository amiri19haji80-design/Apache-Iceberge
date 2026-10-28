import os 
import test 



cd ~/work/core
cat > profile_inputs.py <<'PY'
import os, sys, yaml
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.engines.spark_session import SparkSessionManager
BASE = "pipelines/projects/interactions"
task = next(t for t in yaml.safe_load(open(f"{BASE}/tasks.yaml"))["tasks"] if t["name"] == "fact_all_interactions")
print("sql_file:", task["transform"]["sql_file"])
lines = []
for l in open("main.py", encoding="utf-8"):
    if "executor.run(" in l: break
    lines.append(l)
ns = {"__name__": "x"}; exec("".join(lines), ns); ex = ns["executor"]
m = SparkSessionManager(secret_resolver=ex._secret_resolver, mapping_resolver=ex._mapping,
    spark_config=None, enable_clickhouse_catalog=False, resource_config=None, external_s3_buckets=[])
with m.session(layer="beta", source_name="profile") as spark:
    for s in task["transform"]["sources"]:
        try:
            n = spark.table(s["table"]).count()
            print(f"{n:>12,}  {s['alias']:30} {s['table']}")
        except Exception as e:
            print(f"{'ERR':>12}  {s['alias']:30} {s['table']}  -> {str(e)[:120]}")
PY
python profile_inputs.py > prof.log 2>&1; grep -E "sql_file|^ +[0-9,]+ |ERR" prof.log
grep -n "'CRM\|'Eventogy\|UNION" pipelines/projects/interactions/sql/*/fact_all_interactions.sql
