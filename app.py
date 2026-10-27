import os 
import test 

cd ~/work/core
cat > create_empty.py <<'PY'
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
sql = open("pipelines/projects/interactions/sql/interactions/fact_all_contact_participants.sql").read()
with m.session(layer="beta", source_name="ddl_create") as spark:
    spark.table("polaris.beta.trusted.crm_plus.fact_contact_participants_agg").createOrReplaceTempView("fact_client_ptcpt_agg")
    spark.table("polaris.beta.trusted.crm_plus.fact_all_bnp_participants").createOrReplaceTempView("fact_all_bnp_participants")
    df = spark.sql(sql).limit(0)
    df.writeTo("polaris.beta.trusted.crm_plus.fact_all_contact_participants").tableProperty("format-version","3").create()
    print("created, columns:", len(df.columns))
PY
python create_empty.py
