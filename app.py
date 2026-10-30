import os
import test



if mode == "latest":
    q = f"SELECT max(interaction_date), uniqExact(call_id) FROM {GOLD} WHERE interaction_date >= '2026-01-01'"
    print("  latest / ytd calls:", cp.command(q))
