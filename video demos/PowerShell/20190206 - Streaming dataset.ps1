$endpoint = "[your endpoint here]"

while ($true) {

    $ComputerCPU = (Get-WmiObject  -Class win32_processor -ErrorAction Stop | Measure-Object -Property LoadPercentage -Average | Select-Object Average).Average

    $ComputerMemory = Get-WmiObject  -Class win32_operatingsystem -ErrorAction Stop
    $UsedMemory = $ComputerMemory.TotalVisibleMemorySize - $ComputerMemory.FreePhysicalMemory
    $Memory = (($UsedMemory / $ComputerMemory.TotalVisibleMemorySize) * 100)
    $RoundMemory = [math]::Round($Memory, 2)

    $DateTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")

    #$RoundMemory
    #$ComputerCPU 
    #$DateTime

    $payload = @{
        "DateTime" = $DateTime
        "CPU"      = $ComputerCPU
        "Memory"   = $RoundMemory
    }
    Invoke-RestMethod -Method Post -Uri "$endpoint" -Body (ConvertTo-Json @($payload))

    Write-Host "DateTime: " $DateTime " CPU: " $ComputerCPU " Memory: " $RoundMemory
    
    Start-Sleep 2
}
