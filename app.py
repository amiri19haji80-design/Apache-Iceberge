$errs = @()
$TY = "projects\interactions\tasks.yaml"; $DG = "dags\crm_interactions.yaml"; $SQ = "projects\interactions"
$tl = Get-Content $TY
$tasks = $tl | ? { $_ -notmatch '^\s*#' } | % { if($_ -match '^\s*-\s*name:\s*(\S+)'){ $Matches[1] } }
$sqlf  = $tl | ? { $_ -notmatch '^\s*#' } | % { if($_ -match '^\s*sql_file:\s*(\S+)'){ $Matches[1] } }

# tasks.yaml
if(Select-String $TY 'check-ordering' -Quiet){ $errs += "tasks.yaml still has check-ordering" }
$tasks | Group-Object | ? Count -gt 1 | % { $errs += "duplicate task: $($_.Name)" }
foreach($n in 'm360_ntlogin','fact_union_meeting_bnp_participants_crm_ce','fact_union_event_bnp_participants_crm_ce','fact_union_meeting_contact_participants_crm_ce','fact_union_event_contact_participants_crm_ce','crm_interactions','crm_interactions_gold'){ if($tasks -notcontains $n){ $errs += "task missing/commented: $n" } }
$sqlf | ? { -not (Test-Path "$SQ\$_") } | % { $errs += "sql_file not found: $_" }

# crm_interactions sources + gold sql
$i0 = [array]::FindIndex([string[]]$tl, [Predicate[string]]{ param($x) $x -match '^\s*-\s*name:\s*crm_interactions\s*$' })
$blk = @(); for($k=$i0+1; $k -lt $tl.Count -and $tl[$k] -notmatch '^\s*-\s*name:'; $k++){ $blk += $tl[$k] }
$bt = $blk -join "`n"
foreach($s in 'permissions_client360','permissions_user_supervisors','m360_ntlogin'){ if($bt -notmatch $s){ $errs += "crm_interactions task missing source $s" } }
$gold = if($bt -match 'sql_file:\s*(\S+)'){ "$SQ\$($Matches[1])" }
foreach($c in 'm360_ntlogin','cia_permissions','permissions_user_supervisors','contact_email_address','is_contact_c_suits','contact_location'){ if(-not (Select-String $gold $c -Quiet)){ $errs += "gold sql ($gold) missing $c" } }

# contact SQL
foreach($f in 'fact_contact_participants_list','fact_contact_participants_agg'){ foreach($c in 'corporate_email_address','contact_location','c_suit'){ if(-not (Select-String "$SQ\sql\interactions\$f.sql" $c -Quiet)){ $errs += "$f.sql missing $c" } } }
if(Select-String "$SQ\sql\interactions\fact_all_contact_participants.sql" 'bp\.corporate_email_address' -Quiet){ $errs += "fact_all_contact_participants.sql still has bp.corporate_email_address" }

# DAG: only the new edges, checked against tasks.yaml
if(-not (Select-String $DG 'sources\.apex\.\*' -Quiet)){ $errs += "DAG missing alpha_apex group" }
Select-String $DG 'edge:\s*"([^"]+)"' | % { $_.Matches.Groups[1].Value } | ? { $_ -match 'm360|_crm_ce >>|>> projects\.interactions\.fact_union_.*_crm_ce|permissions_' } | % {
  foreach($side in ($_ -split '>>')){ $s = $side.Trim()
    if($s -match '^projects\.interactions\.(\w+)$' -and $tasks -notcontains $Matches[1]){ $errs += "edge uses unknown task: $s" }
    if($s -match '^sources\.(\w+)\.(\w+)$' -and -not (Test-Path "sources\$($Matches[1])\$($Matches[2])\app.yaml")){ $errs += "edge uses unknown source: $s" } } }

# stray helper files
Get-ChildItem -Recurse -File -Include main.py,create_empty.py,drop*.py,recreate.py,ch_tool.py,findtable.py -EA 0 | % { $errs += "do not commit: $($_.Name)" }

""; if($errs.Count -eq 0){ Write-Host "ALL GOOD - commit and raise the PR ($($tasks.Count) tasks checked)" -ForegroundColor Green } else { Write-Host "$($errs.Count) real issue(s):" -ForegroundColor Red; $errs | % { Write-Host " - $_" -ForegroundColor Red } }
