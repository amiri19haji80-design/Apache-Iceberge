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
with m.session(layer="beta", source_name="find") as spark:
    for sub in [r[0] for r in spark.sql("SHOW NAMESPACES IN polaris.beta").collect()]:
        for dom in [r[0] for r in spark.sql(f"SHOW NAMESPACES IN polaris.beta.{sub}").collect()]:
            for r in spark.sql(f"SHOW TABLES IN polaris.beta.{sub}.{dom}").collect():
                if "crm_interactions" in r.tableName:
                    print("FOUND:", f"polaris.beta.{sub}.{dom}.{r.tableName}")
PY
python findtable.py > find.log 2>&1; grep -E "FOUND|Error|Exception" find.log
