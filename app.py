$nuc  = "$HOME\OneDrive - BNP Paribas\Desktop\Repos\factory"
$core = "$HOME\OneDrive - BNP Paribas\Desktop\Pipelines_final\pipelines"
"=== Pipelines_final crm_ce tables:"; Select-String -Path "$core\projects\interactions\tasks.yaml" -Pattern 'trusted\.crm_ce\.' | ForEach-Object { $_.Line.Trim() } | Sort-Object -Unique
"=== Nucleus crm_ce union tasks:"; Select-String -Path "$nuc\2_silver\crm\crm_ce\interactions\app.json" -Pattern '"crm_ce_fact_union_|"path"|"tableName"|"query"|"partitionColumns"|"sourceName"' | ForEach-Object { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() }
