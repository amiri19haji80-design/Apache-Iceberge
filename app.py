import os
import tedt


python ch_tool.py drop --table=gamma.crm_interactions_last_meeting_gold --table=staging_gamma.crm_interactions_last_meeting_gold__crm_interactions_last_meeting_gold --table=gamma.contact_coverage_with_refog_gold --table=staging_gamma.contact_coverage_with_refog_gold__contact_coverage_with_refog_gold > ch.log 2>&1; grep -E "exists|Error" ch.log
