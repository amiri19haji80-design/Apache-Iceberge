cat > count_src.py <<'PY'
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
with m.session(layer="beta", source_name="count") as spark:
    for t in ["polaris.beta.post_trusted.interactions.crm_interactions", "polaris.gamma.crm_interactions_gold"]:
        print(f"{spark.table(t).count():>12,}  {t}")
PY
python count_src.py > cnt.log 2>&1; grep -E "polaris\." cnt.log
