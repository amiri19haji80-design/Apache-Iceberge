import os

sed -n '4,30p' pipelines/projects/interactions/sql/fact_all_interactions.sql


cd ~/work/core
cat > profile_dates.py <<'PY'
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
    for t in ["polaris.beta.trusted.crm_plus.fact_meeting", "polaris.beta.trusted.crm_ce.fact_meeting",
              "polaris.alpha.crm_nas.crm_plus_dim_date_bronze"]:
        df = spark.table(t)
        cols = [(c, ty) for c, ty in df.dtypes if "date" in c.lower() or c.lower() in ("year_value",)]
        print("\n==", t)
        for c, ty in cols:
            r = df.selectExpr(f"count(*) - count(`{c}`) AS nulls", f"cast(min(`{c}`) as string) AS mn", f"cast(max(`{c}`) as string) AS mx").first()
            print(f"  {c:30} {ty:15} nulls={r.nulls:<10} min={r.mn}  max={r.mx}")
PY
python profile_dates.py > prof4.log 2>&1; grep -E "^==|^  " prof4.log
