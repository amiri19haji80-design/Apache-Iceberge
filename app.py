import os 
import test 

cd ~/work/core
cat > ch_tool.py <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.clickhouse.control_plane import ControlPlane
from core.clickhouse.failover import resolve_clickhouse_host
try:
    from core.engines.pandas_session import PandasSessionManager
except ImportError:
    from core.engines.pandas_session_manager import PandasSessionManager

DB, TABLE = "gamma", "crm_interactions_gold"
mode = sys.argv[1] if len(sys.argv) > 1 else "check"
APPLY = "--apply" in sys.argv

lines = []
for l in open("main.py", encoding="utf-8"):
    if "executor.run(" in l: break
    lines.append(l)
ns = {"__name__": "x"}; exec("".join(lines), ns); ex = ns["executor"]
env = str(getattr(ex, "_environment", getattr(ex, "environment", "DEV"))).upper()
if "DEV" not in env:
    sys.exit(f"Refusing: DEV only (got {env})")

session = PandasSessionManager(ex._secret_resolver, mapping_resolver=ex._mapping)
chs = session.storage().clickhouse
cp = ControlPlane(host=resolve_clickhouse_host(chs), port=chs.http_port,
    username=chs.username, password=ex._secret_resolver.resolve(chs.secret_ref),
    cluster=chs.cluster_name, distributed_ddl_timeout_s=chs.distributed_ddl_timeout_s)

exists = cp.table_exists(DB, TABLE)
print(f"env={env} cluster={cp.cluster} table={DB}.{TABLE} exists={exists}"
      + (f" rows={cp.count(DB, TABLE)}" if exists else ""))

if mode == "drop":
    sql = f"DROP TABLE IF EXISTS {DB}.{TABLE} ON CLUSTER '{cp.cluster}' SYNC"
    print(("RUNNING: " if APPLY else "WOULD RUN: ") + sql)
    if APPLY:
        cp.execute_ddl(sql)
        print("dropped. exists now:", cp.table_exists(DB, TABLE))

if mode == "check" and exists:
    q = f"""SELECT count(),
      countIf(m360_uids != ''), countIf(m360_employeename != ''),
      countIf(cia_permission_username != ''), countIf(user_supervisors_user != ''),
      countIf(contact_email_address != ''), countIf(contact_location != ''),
      countIf(is_contact_c_suits != '')
    FROM {DB}.{TABLE}"""
    names = ["total", "m360_uids", "m360_employeename", "cia_permission_username",
             "user_supervisors_user", "contact_email_address", "contact_location", "is_contact_c_suits"]
    for n, v in zip(names, cp.command(q)):
        print(f"{n:28} {v}")
PY
