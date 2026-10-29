import os
import tedt


git status --short
git log --oneline -3
"--- local vs pushed:"; git rev-parse HEAD origin/fix/crm-ce-task-name
"--- PR diff (only CRM files expected):"; git diff --stat origin/dev...HEAD
"--- leftover conflict markers:"; git grep -n -E "^(<<<<<<<|>>>>>>>|=======$)" -- projects sources dags
"--- permissions_client360:"; Get-Content sources\cia\permissions_client360\sql\permissions_client360.sql




Select-String projects\interactions\tasks.yaml -Pattern 'timeParserPolicy|batch_size' | % { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim() }




git add projects/interactions/tasks.yaml
git commit -m "Fix : CRM Plus date parsing and ClickHouse batch size"
git push
