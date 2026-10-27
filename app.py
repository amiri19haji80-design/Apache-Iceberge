import os 


$nuc  = "$HOME\OneDrive - BNP Paribas\Desktop\Repos\factory"
$core = "$HOME\OneDrive - BNP Paribas\Desktop\Pipelines_final\pipelines"
Get-ChildItem "$nuc\2_silver\crm" -Recurse -File -Filter fact_all_contact_participants.sql | ForEach-Object { $_.FullName }
$c = Get-ChildItem "$core\projects" -Recurse -File -Filter fact_all_contact_participants.sql | Select-Object -First 1
$n = Get-ChildItem "$nuc\2_silver\crm" -Recurse -File -Filter fact_all_contact_participants.sql | Select-Object -First 1
code --diff $n.FullName $c.FullName
