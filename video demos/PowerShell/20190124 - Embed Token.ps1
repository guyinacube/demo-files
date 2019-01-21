

# Power BI Embedded Playground
# https://microsoft.github.io/PowerBI-JavaScript/demo/

# Invoke-PowerBIRestMethod Documentation
# https://docs.microsoft.com/powershell/module/microsoftpowerbimgmt.profile/invoke-powerbirestmethod?view=powerbi-ps

# GenerateToken for Reports in a Group
# https://docs.microsoft.com/rest/api/power-bi/embedtoken/reports_generatetokeningroup


# Sign in with a user that has admin rights to App Workspace
Login-PowerBI

# Regular Report

$url = "https://api.powerbi.com/v1.0/myorg/groups/e5a6343a-4491-4ae9-9d94-3091b859e0c8/reports/9476c6ef-8092-47ea-8d3d-cd2af4c49c6f/GenerateToken"

#{
#  "accessLevel": "View"
#}

$body = "{ 'accessLevel': 'View' }"

$response = Invoke-PowerBIRestMethod -Url $url -Body $body -Method Post

$response

$json = $response | ConvertFrom-Json
$json.token

## RLS Report

$urlRLS = "https://api.powerbi.com/v1.0/myorg/groups/cce066ba-09fd-41ef-9c29-64f6c5aa5d38/reports/8bd7a1ff-709d-4307-bcbb-6e33d91e126a/GenerateToken"

#{
#  "accessLevel": "View",
#  "identities": [
#    {
#      "username": "johndoe@guyinacube.com",
#      "roles": [
#        "United States"
#      ],
#      "datasets": [
#        "cfafbeb1-8037-4d0c-896e-a46fb27ff229"
#      ]
#    }
#  ]
#}

$bodyRLS = "{'accessLevel': 'View', 'identities': [{'username': 'johndoe@guyinacube.com','roles': ['United States'],'datasets': ['cfafbeb1-8037-4d0c-896e-a46fb27ff229']}]}"

$responseRLS = Invoke-PowerBIRestMethod -Url $urlRLS -Body $bodyRLS -Method Post

$responseRLS

$jsonRLS = $responseRLS | ConvertFrom-Json
$jsonRLS.token

