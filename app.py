import os 
import test 

cd ~/work/core
grep -n "class \|def \|cluster" src/core/clickhouse/control_plane.py | head -40
grep -rn "ControlPlane(" src/core --include=*.py | grep -v "^src/core/clickhouse/control_plane.py" | head -5
