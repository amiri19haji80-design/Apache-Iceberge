cd ~/work/core/pipelines/projects/interactions
F=sql/$(python -c "import yaml;print(next(t for t in yaml.safe_load(open('tasks.yaml'))['tasks'] if t['name']=='fact_all_interactions')['transform']['sql_file'].split('sql/',1)[1])")
echo "FILE: $F"
grep -n -i "union\|'CRM\|'Eventogy\|join\|where\|interaction_source\| on " "$F"




cd ~/work/core
cat > profile_labels.py <<'PY'
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
    for t in ["polaris.beta.trusted.crm_plus.dim_meeting_sub_type", "polaris.beta.trusted.crm_plus.dim_meeting_tags"]:
        print("==", t)
        cols = spark.table(t).columns
        print("columns:", cols)
        if "interaction_source" in cols:
            spark.sql(f"SELECT interaction_source, substr(call_id,1,2) prefix, count(*) n FROM {t} GROUP BY 1,2 ORDER BY 3 DESC").show(20, False)
PY
python profile_labels.py > prof3.log 2>&1; grep -vE "WARN|SLF4J|WARNING|Setting|adjust|INFO|Stage" prof3.log





$nuc = "$HOME\OneDrive - BNP Paribas\Desktop\Repos\factory"
Get-ChildItem "$nuc\2_silver\crm" -Recurse -Filter fact_all_interactions.sql | % { "FILE: $($_.FullName)"; Select-String $_.FullName -Pattern "union|'CRM|'Eventogy|join|where|interaction_source| on " | % { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() } }
