$endpoint = "[your endpoint here]"

while($true)
{

    $ComputerCPU = (Get-WmiObject  -Class win32_processor -ErrorAction Stop | Measure-Object -Property LoadPercentage -Average | Select-Object Average).Average

    $ComputerMemory = Get-WmiObject  -Class win32_operatingsystem -ErrorAction Stop
    $UsedMemory = $ComputerMemory.TotalVisibleMemorySize - $ComputerMemory.FreePhysicalMemory
    $Memory = (($UsedMemory/ $ComputerMemory.TotalVisibleMemorySize)*100)
    $RoundMemory = [math]::Round($Memory, 2)

    $Date = Get-Date -DisplayHint Date -Format MM/dd/yyyy

    $Time = Get-Date -DisplayHint Time -Format HH:mm:ss

    #$RoundMemory
    #$ComputerCPU 
    #$Date
    #$Time

    $payload = @{
    "Date" =$Date
    "Time" =$Time
    "CPU" = $ComputerCPU
    "Memory" = $RoundMemory
    }
    Invoke-RestMethod -Method Post -Uri "$endpoint" -Body (ConvertTo-Json @($payload))

    Write-Host "Date: " $Date " Time: " $Time " CPU: " $ComputerCPU " Memory: " $RoundMemory
    
    sleep 2
}
