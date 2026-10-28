import os 


  # --- Nucleus parity gaps: m360 / CIA / CRM CE participants ---
  - edge: "sources.apex.m360_researchers_referential >> projects.interactions.m360_ntlogin"
  - edge: "sources.cia.permissions_enhanced_refog >> projects.interactions.m360_ntlogin"
  - edge: "sources.cia.permissions_user >> projects.interactions.m360_ntlogin"
  - edge: "projects.interactions.m360_ntlogin >> projects.interactions.crm_interactions"
  - edge: "sources.cia.permissions_client360 >> projects.interactions.crm_interactions"
  - edge: "sources.cia.permissions_user_supervisors >> projects.interactions.crm_interactions"
  - edge: "projects.interactions.fact_bnpp_ptcpt_crm_ce >> projects.interactions.fact_union_meeting_bnp_participants_crm_ce"
  - edge: "projects.interactions.fact_meeting_crm_ce >> projects.interactions.fact_union_meeting_bnp_participants_crm_ce"
  - edge: "projects.interactions.fact_sub_event_attendees_crm_ce >> projects.interactions.fact_union_event_bnp_participants_crm_ce"
  - edge: "projects.interactions.dim_sub_event_crm_ce >> projects.interactions.fact_union_event_bnp_participants_crm_ce"
  - edge: "projects.interactions.dim_emp_info >> projects.interactions.fact_union_event_bnp_participants_crm_ce"
  - edge: "projects.interactions.dim_contact_info >> projects.interactions.fact_union_event_bnp_participants_crm_ce"
  - edge: "projects.interactions.fact_client_ptcpt_crm_ce >> projects.interactions.fact_union_meeting_contact_participants_crm_ce"
  - edge: "projects.interactions.fact_meeting_crm_ce >> projects.interactions.fact_union_meeting_contact_participants_crm_ce"
  - edge: "projects.interactions.dim_contact_info >> projects.interactions.fact_union_meeting_contact_participants_crm_ce"
  - edge: "projects.interactions.fact_sub_event_attendees_crm_ce >> projects.interactions.fact_union_event_contact_participants_crm_ce"
  - edge: "projects.interactions.dim_sub_event_crm_ce >> projects.interactions.fact_union_event_contact_participants_crm_ce"
  - edge: "projects.interactions.dim_contact_info >> projects.interactions.fact_union_event_contact_participants_crm_ce"
  - edge: "projects.interactions.fact_union_meeting_bnp_participants_crm_ce >> projects.interactions.fact_all_bnp_participants"
  - edge: "projects.interactions.fact_union_event_bnp_participants_crm_ce >> projects.interactions.fact_all_bnp_participants"
  - edge: "projects.interactions.fact_union_meeting_contact_participants_crm_ce >> projects.interactions.fact_contact_participants_list"
  - edge: "projects.interactions.fact_union_event_contact_participants_crm_ce >> projects.interactions.fact_contact_participants_list"


Closes the gaps vs latest Nucleus: m360 columns (Carlos's ask), CIA permission/supervisor columns, contact email/location/c-suite, and the missing CRM CE participant rows. Adds 4 CIA + 1 APEX alpha sources, m360_ntlogin and 4 crm_ce union tasks. All tested in Jupyter through to ClickHouse (2.1M rows).




$fail = 0
function Ok($m){ Write-Host "PASS  $m" -ForegroundColor Green }
function Bad($m){ Write-Host "FAIL  $m" -ForegroundColor Red; $script:fail++ }
function Has($f,$p){ (Test-Path $f) -and (Select-String -Path $f -Pattern $p -Quiet) }
$I="projects\interactions"; $S="$I\sql"; $T="$I\tasks.yaml"; $D="dags\crm_interactions.yaml"

Write-Host "`n== 0. Branch" -ForegroundColor Cyan
$br = git branch --show-current; if($br -eq 'fix/crm-ce-task-name'){ Ok "branch $br" } else { Bad "branch is '$br' (expected fix/crm-ce-task-name)" }

Write-Host "`n== 1. New alpha sources" -ForegroundColor Cyan
foreach($t in 'cia\permissions_client360','cia\permissions_user_supervisors','cia\permissions_enhanced_refog','cia\permissions_user','apex\m360_researchers_referential'){
  $n = Split-Path $t -Leaf
  if((Test-Path "sources\$t\app.yaml") -and (Test-Path "sources\$t\sql\$n.sql")){ Ok "sources\$t" } else { Bad "sources\$t missing app.yaml or sql\$n.sql" } }

Write-Host "`n== 2. New SQL files" -ForegroundColor Cyan
$new = "$S\crm_plus\m360_ntlogin.sql","$S\crm_ce\fact_union_meeting_bnp_participants.sql","$S\crm_ce\fact_union_event_bnp_participants.sql","$S\crm_ce\fact_union_meeting_contact_participants.sql","$S\crm_ce\fact_union_event_contact_participants.sql"
foreach($f in $new){ if(Test-Path $f){ Ok $f } else { Bad "missing $f" } }

Write-Host "`n== 3. SQL hygiene" -ForegroundColor Cyan
$plus = Get-ChildItem $S -Recurse -Filter *.sql | Where-Object { (Get-Content $_.FullName -TotalCount 1) -match '^\s*\+' }
if($plus){ $plus | % { Bad "stray '+' on line 1: $($_.FullName.Substring((Get-Location).Path.Length+1))" } } else { Ok "no diff '+' artifacts" }
$bare = Get-ChildItem "$S\crm_ce" -Filter 'fact_union_*.sql' | Select-String -Pattern '(?<!CAST\(\s*)(?<!IS\s)(?<!NOT\s)\bNULL\s+(AS\s+)?(?!END\b|THEN\b|ELSE\b|AND\b|OR\b|FROM\b)\w+\s*,'
if($bare){ $bare | % { Bad "bare NULL $($_.Filename):$($_.LineNumber): $($_.Line.Trim())" } } else { Ok "no bare NULLs in crm_ce union SQL" }

Write-Host "`n== 4. Contact columns + FIC" -ForegroundColor Cyan
foreach($f in "$S\interactions\fact_contact_participants_list.sql","$S\interactions\fact_contact_participants_agg.sql"){
  foreach($c in 'corporate_email_address','contact_location','c_suite'){ if(Has $f $c){ Ok "$(Split-Path $f -Leaf) has $c" } else { Bad "$(Split-Path $f -Leaf) missing $c" } } }
$fac = "$S\interactions\fact_all_contact_participants.sql"
if(Has $fac 'bp\.corporate_email_address'){ Bad "fact_all_contact_participants.sql still has bp.corporate_email_address (duplicate column!)" } else { Ok "fact_all_contact_participants.sql no duplicate email column" }
$adage = Get-ChildItem $S -Recurse -Filter dim_adage_history.sql | Select-Object -First 1
if($adage -and (Has $adage.FullName 'CIB FINANCIAL INSTITUTIONS COVERAGE')){ Ok "dim_adage_history has CIB FIC line" } else { Bad "dim_adage_history missing CIB FIC line" }

Write-Host "`n== 5. tasks.yaml" -ForegroundColor Cyan
$lines = Get-Content $T; $names=@(); $sqls=@()
foreach($l in $lines){ if($l -match '^\s*#'){continue}; if($l -match '^\s*-\s*name:\s*(\S+)'){ $names += $Matches[1] }; if($l -match '^\s*sql_file:\s*(\S+)'){ $sqls += $Matches[1] } }
if(Select-String -Path $T -Pattern 'check-ordering' -Quiet){ Bad "check-ordering still in tasks.yaml" } else { Ok "no check-ordering" }
if(Select-String -Path $T -Pattern "`t" -Quiet){ Bad "TAB characters in tasks.yaml" } else { Ok "no tabs" }
$dup = $names | Group-Object | ? Count -gt 1; if($dup){ $dup | % { Bad "duplicate task name: $($_.Name)" } } else { Ok "no duplicate task names ($($names.Count) active tasks)" }
foreach($n in 'm360_ntlogin','fact_union_meeting_bnp_participants_crm_ce','fact_union_event_bnp_participants_crm_ce','fact_union_meeting_contact_participants_crm_ce','fact_union_event_contact_participants_crm_ce','crm_interactions','crm_interactions_gold'){
  if($names -contains $n){ Ok "task $n active" } else { Bad "task $n missing or commented out" } }
$miss = $sqls | ? { -not (Test-Path "$I\$_") }; if($miss){ $miss | % { Bad "sql_file not found: $_" } } else { Ok "all $($sqls.Count) sql_file paths exist" }
$gi = ($lines | Select-String -Pattern '^\s*-\s*name:\s*crm_interactions\s*$' | Select-Object -First 1).LineNumber
$block=@(); if($gi){ for($j=$gi;$j -lt $lines.Count;$j++){ if($lines[$j] -match '^\s*-\s*name:'){break}; $block += $lines[$j] } }
$gs = ($block | Select-String -Pattern '^\s*sql_file:\s*(\S+)' | Select-Object -First 1).Matches.Groups[1].Value
foreach($src in 'permissions_client360','permissions_user_supervisors','m360_ntlogin'){ if(($block -join "`n") -match $src){ Ok "crm_interactions source $src" } else { Bad "crm_interactions missing source $src" } }

Write-Host "`n== 6. Gold SQL ($gs)" -ForegroundColor Cyan
foreach($c in 'm360_ntlogin','cia_permissions','permissions_user_supervisors','contact_email_address','is_contact_c_suits','contact_location'){ if(Has "$I\$gs" $c){ Ok "gold sql has $c" } else { Bad "gold sql missing $c" } }

Write-Host "`n== 7. DAG" -ForegroundColor Cyan
if((Has $D 'alpha_apex:') -and (Has $D 'sources\.apex\.\*')){ Ok "alpha_apex group" } else { Bad "alpha_apex group missing" }
if(Select-String -Path $D -Pattern "`t" -Quiet){ Bad "TAB characters in DAG yaml" } else { Ok "no tabs" }
function SelOk($s){
  if($s -match '\*'){ return $true }
  if($s -match '^projects\.interactions\.(\w+)$'){ return ($names -contains $Matches[1]) }
  if($s -match '^sources\.(.+)\.(\w+)$'){ $dir='sources\'+($Matches[1] -replace '\.','\'); $nm=$Matches[2]
    if(Test-Path "$dir\$nm\app.yaml"){ return $true }
    if(Test-Path $dir){ return (@(Get-ChildItem $dir -Recurse -Filter app.yaml | Select-String -Pattern "^\s*-\s*name:\s*$nm\s*$").Count -gt 0) } }
  return $false }
$edges = Select-String -Path $D -Pattern 'edge:\s*"([^"]+)"' | % { $_.Matches.Groups[1].Value }
$badE = 0; foreach($e in $edges){ foreach($side in ($e -split '>>')){ $s=$side.Trim(); if(-not (SelOk $s)){ Bad "unknown selector in edge: $s"; $badE++ } } }
if($badE -eq 0){ Ok "all $($edges.Count) edges point to existing tasks" }
foreach($k in 'projects.interactions.m360_ntlogin','sources.apex.m360_researchers_referential','fact_union_event_contact_participants_crm_ce >> projects.interactions.fact_contact_participants_list'){ if(Has $D ([regex]::Escape($k))){ Ok "edge present: $k" } else { Bad "edge missing: $k" } }

Write-Host "`n== 8. Safety" -ForegroundColor Cyan
$stray = Get-ChildItem -Recurse -File -Include main.py,create_empty.py,drop.py,drop_tables.py,recreate.py,ch_tool.py,findtable.py,crm_landing_cleanup.py -ErrorAction SilentlyContinue | ? { $_.FullName -notmatch '\\\.git\\' }
if($stray){ $stray | % { Bad "do not commit: $($_.FullName)" } } else { Ok "no local helper scripts in repo" }
$sec = Get-ChildItem sources\apex,sources\cia,$I,dags -Recurse -File | Select-String -Pattern '(password|passwd|secret)\s*[:=]\s*["'']?\w' -ErrorAction SilentlyContinue
if($sec){ $sec | % { Bad "possible secret: $($_.Filename):$($_.LineNumber)" } } else { Ok "no secrets in changed areas" }
$q = Get-ChildItem sources -Recurse -Filter app.yaml | Select-String -Pattern 'path:\s*"[^"]*$'
if($q){ $q | % { Bad "unclosed quote: $($_.Path):$($_.LineNumber)" } } else { Ok "no unclosed path quotes" }

Write-Host ""
if($fail -eq 0){ Write-Host "==> ALL GOOD - safe to commit and raise the PR" -ForegroundColor Green } else { Write-Host "==> $fail problem(s) - fix the FAIL lines first" -ForegroundColor Red }

