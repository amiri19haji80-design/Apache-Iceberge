import test
import os 


$nuc  = "$HOME\OneDrive - BNP Paribas\Desktop\Repos\factory"
$core = "$HOME\OneDrive - BNP Paribas\Desktop\Pipelines_final\pipelines"
$cg = Get-ChildItem "$core\projects" -Recurse -File -Filter crm_interactions.sql | Where-Object { $_.FullName -match 'gamma' } | Select-Object -First 1
$cg.FullName
code --diff "$nuc\3_gold\crm\sql\crm_interactions.sql" $cg.FullName
