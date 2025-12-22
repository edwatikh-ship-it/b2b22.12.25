list-endpoints:
    powershell ./tools/list-endpoints.ps1

endpoint-status PATH:
    powershell ./tools/endpoint-status.ps1 {{PATH}}

stub-endpoint PATH:
    powershell ./tools/stub-endpoint.ps1 {{PATH}}
