import test 
import os
import io

Select-String -Path "$nuc\2_silver\crm\crm_ce\interactions\app.json" -Pattern '"crm_ce_fact_union_|"path"|"tableName"|"query"|"partitionColumns"|"sourceName"' | ForEach-Object { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() }
