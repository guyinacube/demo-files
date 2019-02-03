while($true)
{

    $ComputerCPU = (Get-WmiObject  -Class win32_processor -ErrorAction Stop | Measure-Object -Property LoadPercentage -Average | Select-Object Average).Average

    $ComputerMemory = Get-WmiObject  -Class win32_operatingsystem -ErrorAction Stop
    $Memory = ((($ComputerMemory.TotalVisibleMemorySize - $ComputerMemory.FreePhysicalMemory)*100)/ $ComputerMemory.TotalVisibleMemorySize)
    $RoundMemory = [math]::Round($Memory, 2)

    $Date = Get-Date -DisplayHint Date -Format MM/dd/yyyy

    $Time = Get-Date -DisplayHint Time -Format HH:MM:ss

    #$RoundMemory
    #$ComputerCPU 
    #$Date
    #$Time

    $endpoint = "https://api.powerbi.com/beta/a7502f9c-15b1-4eae-a9bc-d3311a46aaf7/datasets/27cb708d-edc1-4856-bd53-6371218099b6/rows?key=HsJocycMmC%2BTHOoLcq6bvcPLhrcbEfSQFaKj5X3eF0%2Fyu1sRSInaP%2BRaqoqrIXuJwpQuQh0hjcurg%2BMLG8WljQ%3D%3D"
    $payload = @{
    "Date" =$Date
    "Time" =$Time
    "CPU" = $ComputerCPU
    "Memory" = $RoundMemory
    }
    Invoke-RestMethod -Method Post -Uri "$endpoint" -Body (ConvertTo-Json @($payload))



}