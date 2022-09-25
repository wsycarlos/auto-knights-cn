function Get-DebugDataPath() {
    Param (
        [int]$BackupCount = 0
    )
    if ($BackupCount -eq 0) {
        return "debug"
    }
    return "debug.$BackupCount"
}
    
function Backup-DebugData() {
    Param (
        [int]$MaxBackupCount
    )
            
    for ($i = $MaxBackupCount; $i -ge 0; $i--) {
        $path = Get-DebugDataPath $i
        if (Test-Path $path) {
            if ($i -eq $MaxBackupCount) {
                [void](New-Item -Force -ItemType Directory trash.local)
                Move-Item $path trash.local/$((Get-Date).Ticks)
            }
            else {
                Move-Item $path (Get-DebugDataPath ($i + 1))
            }
        }
    }
    [void](New-Item -ItemType Directory (Get-DebugDataPath))
}

Backup-DebugData -MaxBackupCount 3
