import os 
import test 

cd ~/work/core
cat > recreate.py <<'PY'
import os, sys, yaml
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.engines.spark_session import SparkSessionManager
TASK = sys.argv[1]; BASE = "pipelines/projects/interactions"
t = next(x for x in yaml.safe_load(open(f"{BASE}/tasks.yaml"))["tasks"] if x["name"] == TASK)
table = f"polaris.{t['layer']}.{t['sub_layer'].replace('-','_')}.{t['metadata']['domain']}.{t.get('table_name', TASK)}"
lines = []
for l in open("main.py", encoding="utf-8"):
    if "executor.run(" in l: break
    lines.append(l)
ns = {"__name__": "x"}; exec("".join(lines), ns); ex = ns["executor"]
m = SparkSessionManager(secret_resolver=ex._secret_resolver, mapping_resolver=ex._mapping,
    spark_config=None, enable_clickhouse_catalog=False, resource_config=None, external_s3_buckets=[])
with m.session(layer="beta", source_name="ddl_recreate") as spark:
    for s in t["transform"]["sources"]:
        spark.table(s["table"]).createOrReplaceTempView(s["alias"])
    df = spark.sql(open(f"{BASE}/{t['transform']['sql_file']}").read()).limit(0)
    print("target:", table, "| exists:", spark.catalog.tableExists(table))
    if "--apply" in sys.argv:
        df.writeTo(table).tableProperty("format-version", "3").createOrReplace()
        print("recreated, columns:", len(df.columns))
PY
python recreate.py crm_interactions > rec.log 2>&1; grep -E "target|recreated|Error|Exception" rec.log
