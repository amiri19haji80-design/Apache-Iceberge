import os 
import test 


Get-ChildItem factory\2_silver\crm -Recurse -Filter app.json | Select-String 'dim_client_hierarchy|dim_coverage_info' | % { "{0}:{1}: {2}" -f $_.Filename, $_.LineNumber, $_.Line.Trim() }
