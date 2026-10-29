import os
import tedt


python ch_tool.py drop --apply --table=gamma.crm_interactions_partitioned_gold --table=staging_gamma.crm_interactions_partitioned_gold__crm_interactions_partitioned_gold > ch.log 2>&1; grep -E "exists|dropped|Error" ch.log
