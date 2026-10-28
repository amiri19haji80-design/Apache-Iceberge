import os 



if mode == "profile":
    q = f"""SELECT interaction_source, interaction_type, uniqExact(call_id) AS calls,
                   min(last_crm_update_date) AS first, max(last_crm_update_date) AS last
            FROM {GOLD} GROUP BY 1, 2 ORDER BY 1, 2"""
    for r in cp.client().query(q).result_rows:
        print("  ", r)




python ch_tool.py profile > ch.log 2>&1; grep -vE "WARN|SLF4J|WARNING|Setting|adjust" ch.log


cat > profile_iceberg.py <<'PY'
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
    for t in ["polaris.beta.trusted.crm_plus.fact_all_interactions",
              "polaris.beta.post_trusted.interactions.crm_interactions"]:
        print("==", t)
        try:
            spark.sql(f"SELECT interaction_source, interaction_type, count(DISTINCT call_id) calls FROM {t} GROUP BY 1,2 ORDER BY 1,2").show(50, False)
        except Exception as e:
            print("ERR", str(e)[:300])
PY
python profile_iceberg.py > prof.log 2>&1; grep -vE "WARN|SLF4J|WARNING|Setting|adjust|INFO" prof.log



Thanks Carlos, good catch. What's in ClickHouse today is a DEV test load and it's about 10 days old, but the gap is too big to be only that: most CRM Plus interactions seem to be missing. I'm tracing where they drop out and will reload the full data. One question: which filter or client did you use on both dashboards? I want to compare the same numbers.
