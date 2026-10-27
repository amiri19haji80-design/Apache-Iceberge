import os 
import test 

cd ~/work/core
cat > findtable.py <<'PY'
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
def walk(spark, nsname):
    for r in spark.sql(f"SHOW TABLES IN polaris.{nsname}").collect():
        if "crm_interactions" in r.tableName:
            print("FOUND:", f"polaris.{nsname}.{r.tableName}")
    for r in spark.sql(f"SHOW NAMESPACES IN polaris.{nsname}").collect():
        walk(spark, r[0])
with m.session(layer="beta", source_name="find") as spark:
    walk(spark, "beta")
PY
python findtable.py > find.log 2>&1; grep -E "FOUND|Error|Exception" find.log
