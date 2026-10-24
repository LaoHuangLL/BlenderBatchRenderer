# BlenderBatchRenderer - hang diagnosis script
#
# WHEN: the app hangs (frozen window / cannot be closed / system laggy).
# RUN IT WHILE THE PROCESS IS STILL VISIBLE IN TASK MANAGER:
#     powershell -NoProfile -ExecutionPolicy Bypass -File .\diagnose_hang.ps1
#   or with an explicit process name (no .exe):
#     powershell -NoProfile -ExecutionPolicy Bypass -File .\diagnose_hang.ps1 -Name BlenderBatchRenderer_new
#
# WHAT IT ANSWERS:
#   * is the process alive / responding, how many threads and handles
#   * *** TERMINATING-STATE SIGNATURE *** : every thread Windows could kill is
#     already gone and the survivor is executing kernel-mode code. Such a thread
#     is usually stuck inside a display/GPU driver call; nothing in user space can
#     stop it and the process stays visible until reboot.
#   * which GPU driver modules the process has loaded (nvml / nvcuda / nvapi /
#     opengl32 / d3d11 / d3d12 / dxgi / amdadl ...)
#   * thread distribution by State/WaitReason (WaitReason is only valid in State=Wait)
#   * leftover blender.exe, tail of the exit log, GPU driver versions,
#     and recent display-driver / TDR / Application-Hang events.
#
# The report is written next to THIS SCRIPT (never into the current directory,
# which may be a protected folder such as System32), falling back to %TEMP%.
#
# NOTE: pure ASCII on purpose - Windows PowerShell 5.1 reads a BOM-less script as
#       ANSI and would mangle non-ASCII text and file names.

param(
    [string]$Name = "BlenderBatchRenderer_new"
)

$ErrorActionPreference = "Continue"
$report = New-Object System.Collections.Generic.List[string]

function Add-Line([string]$text) {
    $script:report.Add($text)
    Write-Host $text
}

Add-Line "==== BlenderBatchRenderer hang diagnosis ===="
Add-Line ("time  : " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Add-Line ("host  : " + $env:COMPUTERNAME)
Add-Line ("script: " + $PSScriptRoot)
Add-Line ("cwd   : " + (Get-Location))
Add-Line ("os    : " + [System.Environment]::OSVersion.VersionString)
Add-Line ""

# ------------------------------------------------------------------ processes
$procs = @(Get-Process -Name $Name -ErrorAction SilentlyContinue)
if ($procs.Count -eq 0) {
    $procs = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "*BlenderBatch*"
    })
}

if ($procs.Count -eq 0) {
    Add-Line ("[!] No process named '" + $Name + "' is running.")
    Add-Line "    => The app already exited: the hang is then NOT a stuck process."
} else {
    foreach ($proc in $procs) {
        Add-Line "----------------------------------------------------------"
        Add-Line ("PROCESS  id=" + $proc.Id + "  name=" + $proc.ProcessName)
        try { Add-Line ("  exe          : " + $proc.Path) } catch { Add-Line "  exe          : <denied>" }
        try { Add-Line ("  started      : " + $proc.StartTime) } catch { Add-Line "  started      : <denied>" }
        try { Add-Line ("  runtime      : " + [string]((Get-Date) - $proc.StartTime)) } catch { }
        try { Add-Line ("  threads      : " + $proc.Threads.Count) } catch { Add-Line "  threads      : <denied>" }
        try { Add-Line ("  handles      : " + $proc.HandleCount) } catch { Add-Line "  handles      : <denied>" }
        try { Add-Line ("  working set  : " + [math]::Round($proc.WorkingSet64 / 1MB, 1) + " MB") } catch { }
        try { Add-Line ("  responding   : " + $proc.Responding) } catch { Add-Line "  responding   : <denied>" }
        try { Add-Line ("  main title   : [" + $proc.MainWindowTitle + "]") } catch { }
        try { Add-Line ("  cpu total    : " + [math]::Round($proc.TotalProcessorTime.TotalSeconds, 1) + " s") } catch { }

        # ---- loaded modules: does this process talk to a GPU driver at all?
        try {
            $allMods = @($proc.Modules)
            Add-Line ("  modules      : " + $allMods.Count)
            $gpuNames = @($allMods |
                Where-Object { $_.ModuleName -match "(?i)nvml|nvcuda|nvapi|nvoglv|opengl32|vulkan|d3d11|d3d12|dxgi|atiumd|amdadl|igdumd" } |
                ForEach-Object { $_.ModuleName })
            if ($gpuNames.Count -gt 0) {
                Add-Line ("  GPU modules  : " + ($gpuNames -join ", "))
                Add-Line "                 (a thread hung inside one of these = unkillable process)"
            } else {
                Add-Line "  GPU modules  : none loaded"
                Add-Line "                 => a GPU driver is NOT what this process is stuck in"
            }
        } catch {
            Add-Line ("  modules      : <denied> " + $_.Exception.Message)
        }

        # ---- threads: State first, WaitReason only when State = Wait
        Add-Line ""
        $threadInfos = @()
        $threadsOk = $true
        try {
            $threadInfos = @($proc.Threads | ForEach-Object {
                $st = "?"
                $rs = "-"
                try { $st = [string]$_.ThreadState } catch { $st = "?" }
                if ($st -eq "Wait") {
                    try { $rs = [string]$_.WaitReason } catch { $rs = "?" }
                }
                $cpu = -1.0
                try { $cpu = [math]::Round($_.TotalProcessorTime.TotalSeconds, 2) } catch { }
                [pscustomobject]@{ Id = $_.Id; State = $st; Reason = $rs; Cpu = $cpu }
            })
        } catch {
            $threadsOk = $false
            Add-Line ("  <cannot enumerate threads: " + $_.Exception.Message + ">")
            Add-Line "  => if even the thread list is denied, the process is most likely"
            Add-Line "     already in the Windows 'terminating' state."
        }

        if ($threadsOk) {
            $waiting = @($threadInfos | Where-Object { $_.State -eq "Wait" })
            $busy = @($threadInfos | Where-Object { $_.State -ne "Wait" -and $_.State -ne "Terminated" })

            Add-Line ("  THREADS: total=" + $threadInfos.Count + "  waiting=" + $waiting.Count + "  not-waiting=" + $busy.Count)
            Add-Line ""
            Add-Line "  grouped by State/WaitReason:"
            $threadInfos | Group-Object { $_.State + "/" + $_.Reason } | Sort-Object Count -Descending | ForEach-Object {
                Add-Line ("    " + $_.Name.PadRight(26) + " x" + $_.Count)
            }

            if ($busy.Count -gt 0) {
                Add-Line ""
                Add-Line "  threads NOT waiting on an event (kernel-mode / spinning):"
                foreach ($th in $busy) {
                    Add-Line ("    id=" + $th.Id + "  state=" + $th.State + "  cpu=" + $th.Cpu + "s")
                }
            }

            Add-Line ""
            # ---- the decisive pattern
            if ($threadInfos.Count -le 2 -and $busy.Count -ge 1) {
                Add-Line "  *** TERMINATING-STATE SIGNATURE ***"
                Add-Line ("  only " + $threadInfos.Count + " thread(s) left, and one of them is not waiting on any event.")
                Add-Line "  Windows has killed every thread it could; the survivor is executing"
                Add-Line "  kernel-mode code, almost always inside a display/GPU driver call."
                Add-Line "  => Unkillable from user space (Task Manager / taskkill /F return"
                Add-Line "     'Access is denied'). Reboot is the only way out."
                Add-Line "  => Next run: keep GPU monitoring OFF (see the config json) and see"
                Add-Line "     whether the hang still happens."
            } elseif ($threadInfos.Count -gt 2 -and $waiting.Count -eq $threadInfos.Count) {
                Add-Line "  Verdict: every thread sits in an ordinary user-mode wait."
                Add-Line "  => the process itself is healthy; the freeze is user-space logic"
                Add-Line "     (a lock, an event, the Qt event loop) or the whole machine."
            } else {
                Add-Line "  Verdict: mixed - see the per-thread list above."
            }
        }

        Add-Line ""
        Add-Line "  Reading guide:"
        Add-Line "    State=Wait + WaitReason=UserRequest/EventPair*/WrQueue -> normal idle thread"
        Add-Line "    State=Running/Transition (WaitReason unavailable)       -> the thread is"
        Add-Line "      executing kernel-mode code (a driver). If that persists while the process"
        Add-Line "      has almost no threads left, it is terminating: reboot only."
    }
}

# ------------------------------------------------------------------ other clues
Add-Line ""
Add-Line "---- blender.exe processes ----"
$bl = @(Get-Process -Name blender -ErrorAction SilentlyContinue)
if ($bl.Count -eq 0) {
    Add-Line "  none running"
} else {
    foreach ($b in $bl) {
        Add-Line ("  id=" + $b.Id + "  cpu=" + [math]::Round($b.TotalProcessorTime.TotalSeconds, 1) + "s  responding=" + $b.Responding)
    }
}

Add-Line ""
Add-Line "---- exit log (tail) ----"
$candidates = New-Object System.Collections.Generic.List[string]
if ($PSScriptRoot) {
    $candidates.Add((Join-Path $PSScriptRoot "BlenderBatchRenderer_exit.log"))
    $parent1 = Split-Path $PSScriptRoot -Parent
    if ($parent1) {
        $candidates.Add((Join-Path $parent1 "BlenderBatchRenderer_exit.log"))
        $parent2 = Split-Path $parent1 -Parent
        if ($parent2) { $candidates.Add((Join-Path $parent2 "BlenderBatchRenderer_exit.log")) }
    }
}
if ($procs.Count -gt 0) {
    try {
        $exeDir = Split-Path $procs[0].Path -Parent
        if ($exeDir) { $candidates.Add((Join-Path $exeDir "BlenderBatchRenderer_exit.log")) }
    } catch { }
}
$candidates.Add((Join-Path ([Environment]::GetFolderPath("Desktop")) "BlenderBatchRenderer_exit.log"))
$candidates.Add((Join-Path ([Environment]::GetFolderPath("UserProfile")) "BlenderBatchRenderer_exit.log"))
$candidates.Add((Join-Path $env:TEMP "BlenderBatchRenderer_exit.log"))

$logFound = $false
foreach ($cand in ($candidates | Select-Object -Unique)) {
    if ($cand -and (Test-Path $cand)) {
        Add-Line ("  file: " + $cand)
        Get-Content $cand -Tail 40 | ForEach-Object { Add-Line ("  " + $_) }
        $logFound = $true
        break
    }
}
if (-not $logFound) {
    Add-Line "  not found. Looked in:"
    foreach ($cand in ($candidates | Select-Object -Unique)) { Add-Line ("    " + $cand) }
    Add-Line "  (the log is written to the app's CURRENT DIRECTORY at exit time)"
}

Add-Line ""
Add-Line "---- GPU / driver ----"
try {
    $vc = @(Get-CimInstance Win32_VideoController -ErrorAction Stop)
    foreach ($v in $vc) {
        Add-Line ("  " + $v.Name + "  driver=" + $v.DriverVersion + "  date=" + $v.DriverDate)
    }
} catch {
    Add-Line "  <could not query Win32_VideoController>"
}

Add-Line ""
Add-Line "---- display driver / TDR / app-hang events (last 7 days) ----"
$evts = @()
try {
    $raw = @(Get-WinEvent -FilterHashtable @{
        LogName      = "System"
        ProviderName = @("Display", "Application Hang", "nvlddmkm")
        StartTime    = (Get-Date).AddDays(-7)
    } -ErrorAction Stop)
    # keep only what matters: 'Display' 4101/4102 = display driver stopped
    # responding and recovered (TDR); 'Application Hang' (any id); nvlddmkm (any id).
    $evts = @($raw | Where-Object {
        ($_.ProviderName -eq "Display" -and ($_.Id -eq 4101 -or $_.Id -eq 4102)) -or
        ($_.ProviderName -eq "Application Hang") -or
        ($_.ProviderName -eq "nvlddmkm")
    } | Sort-Object TimeCreated -Descending)
} catch {
    Add-Line "  <could not read the System event log>"
}
try {
    $nv = @($evts | Where-Object { $_.ProviderName -eq "nvlddmkm" })
    $others = @($evts | Where-Object { $_.ProviderName -ne "nvlddmkm" })
    if ($others.Count -eq 0) {
        Add-Line "  no TDR (Display 4101/4102) and no Application-Hang record in the last 7 days"
    } else {
        foreach ($e in ($others | Select-Object -First 20)) {
            $msg = ""
            try { $msg = ($e.Message -split "`r?`n")[0] } catch { $msg = "" }
            Add-Line ("  " + $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss") + "  id=" + $e.Id + "  " + $e.ProviderName + "  " + $msg)
        }
        Add-Line "  NOTE: provider 'Display' + id 4101 = 'the display driver stopped"
        Add-Line "        responding and has recovered' (TDR) - hard evidence of a driver hang."
    }
    if ($nv.Count -gt 0) {
        Add-Line ""
        Add-Line ("  nvlddmkm (NVIDIA kernel driver) events in the last 7 days: " + $nv.Count)
        $nv | Group-Object Id | Sort-Object Count -Descending | ForEach-Object {
            Add-Line ("    id=" + $_.Name + " x" + $_.Count)
        }
        $last = $nv | Sort-Object TimeCreated -Descending | Select-Object -First 1
        Add-Line ("    most recent: " + $last.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss") + " (id=" + $last.Id + ")")
        $props = @()
        try { $props = @($last.Properties | ForEach-Object { [string]$_.Value }) } catch { }
        if ($props.Count -gt 0) {
            Add-Line ("    its data fields: " + ($props -join " | "))
        }
        Add-Line "    (these are driver-level reports; a burst of them around the time of"
        Add-Line "     the hang points at the display driver, not at this app)"
    }
} catch {
    Add-Line "  <could not read the System event log>"
}

# ------------------------------------------------------------------ save
$outDirs = @()
if ($PSScriptRoot) { $outDirs += $PSScriptRoot }
$outDirs += $env:TEMP
$outDirs += [Environment]::GetFolderPath("Desktop")
$saved = $false
foreach ($d in $outDirs) {
    if (-not $d) { continue }
    $outFile = Join-Path $d "diagnosis_result.txt"
    try {
        $report -join "`r`n" | Out-File -FilePath $outFile -Encoding UTF8 -ErrorAction Stop
        Write-Host ""
        Write-Host ("Saved to: " + $outFile)
        $saved = $true
        break
    } catch { }
}
if (-not $saved) {
    Write-Host ""
    Write-Host "Could not save the report to any location; copy the output above."
}
