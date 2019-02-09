# Use this script to disable viral signup for your tenant

# Install-Module -name MSOnline


$msolcred = get-credential
connect-msolservice -credential $msolcred


Set-MsolCompanySettings -AllowAdHocSubscriptions $false

Get-MsolCompanyInformation | fl AllowAdHocSubscriptions
