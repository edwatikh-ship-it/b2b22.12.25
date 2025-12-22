# Prompt bootstrap template - copy to new chat
Set-Location D:\b2b
$timestamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
New-Item -ItemType Directory -Force ".\Prompt\$timestamp" | Out-Null
Copy-Item .\Docs\* ".\Prompt\$timestamp\" -Recurse
Copy-Item .\api-contracts.yaml ".\Prompt\$timestamp\"
Get-ChildItem ".\Prompt\$timestamp\" | Select-Object Name
