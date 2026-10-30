import os
import test



$nuc = "$HOME\OneDrive - BNP Paribas\Desktop\Repos\factory"
Select-String -Path "$nuc\3_gold\crm\app.json" -Pattern '"crm_interactions"' -Context 0,30 | % { $_.Line; $_.Context.PostContext }
