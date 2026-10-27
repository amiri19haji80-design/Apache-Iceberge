import os 
import test 



import os, sys
_src = os.path.join(os.getcwd(), "src")
if os.path.isdir(os.path.join(_src, "core")) and _src not in sys.path:
    sys.path.insert(0, _src)
from core.engines.spark_session import SparkSessionManager

TABLES = [
    "polaris.beta.trusted.crm_plus.fact_contact_participants_list",
    "polaris.beta.trusted.crm_plus.fact_contact_participants_agg",
    "polaris.beta.trusted.crm_plus.fact_all_contact_participants",
]
APPLY = "--apply" in sys.argv

lines = []
with open("main.py", encoding="utf-8") as fh:
    for line in fh:
        if "executor.run(" in line:
            break
        lines.append(line)
ns = {"__name__": "main_setup"}
exec(compile("".join(lines), "main.py", "exec"), ns)
executor = ns["executor"]
env = getattr(executor, "_environment", getattr(executor, "environment", "DEV"))
if str(env).upper() != "DEV":
    sys.exit(f"Refusing: DEV only (got {env!r})")

manager = SparkSessionManager(
    secret_resolver=executor._secret_resolver, mapping_resolver=executor._mapping,
    spark_config=None, enable_clickhouse_catalog=False,
    resource_config=None, external_s3_buckets=[])
with manager.session(layer="beta", source_name="ddl_drop") as spark:
    for t in TABLES:
        print(("DROP " if APPLY else "WOULD DROP ") + t)
        if APPLY:
            spark.sql(f"DROP TABLE IF EXISTS {t}")
print("done")
