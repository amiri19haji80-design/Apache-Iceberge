cd ~/work/core
cat > profile_meetdate.py <<'PY'
import os, sys, re, yaml
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.engines.spark_session import SparkSessionManager
BASE = "pipelines/projects/interactions"
tasks = yaml.safe_load(open(f"{BASE}/tasks.yaml"))["tasks"]
t = next(x for x in tasks if x.get("transform", {}).get("sql_file", "").endswith("crm_plus/fact_meeting.sql")
         or (x["name"] == "fact_meeting" and x.get("metadata", {}).get("domain") == "crm_plus"))
sqlp = f"{BASE}/{t['transform']['sql_file']}"
print("TASK:", t["name"], "| SQL:", sqlp)
for i, l in enumerate(open(sqlp), 1):
    if re.search(r"meeting_date|to_date|to_timestamp|date_format|unix_timestamp", l, re.I):
        print(f"  {i}: {l.rstrip()}")
lines = []
for l in open("main.py", encoding="utf-8"):
    if "executor.run(" in l: break
    lines.append(l)
ns = {"__name__": "x"}; exec("".join(lines), ns); ex = ns["executor"]
m = SparkSessionManager(secret_resolver=ex._secret_resolver, mapping_resolver=ex._mapping,
    spark_config=None, enable_clickhouse_catalog=False, resource_config=None, external_s3_buckets=[])
with m.session(layer="beta", source_name="profile") as spark:
    for s in t["transform"]["sources"]:
        df = spark.table(s["table"])
        cols = [c for c, ty in df.dtypes if re.search(r"date|start|end|time", c, re.I)]
        print(f"\n== {s['alias']} ({s['table']})  rows={df.count():,}")
        print("   types:", [(c, ty) for c, ty in df.dtypes if c in cols])
        if cols:
            df.select(*cols).where(" OR ".join(f"`{c}` IS NOT NULL" for c in cols)).show(5, False)
PY
python profile_meetdate.py > prof5.log 2>&1; grep -vE "WARN|SLF4J|WARNING|Setting|adjust|INFO|Stage" prof5.log
