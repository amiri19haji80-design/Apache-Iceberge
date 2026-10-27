import os 
import test 

cd ~/work/core
grep -rn "overwritePartitions\|createOrReplace\|tableExists\|table_exists" src/core/ --include=*.py | grep -v test | head -30
