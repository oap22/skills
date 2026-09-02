<#
  Reports the current Java / JavaFX / IntelliJ state for MSOE SWE 2410.
  Read-only - changes nothing. Compare its output against taylorial.com/tools/java/.
#>
$ErrorActionPreference = 'SilentlyContinue'

function Section($t) { Write-Output ""; Write-Output "=== $t ===" }

Section 'JDKs installed'
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
  Where-Object { $_.DisplayName -match 'Java|JDK' } |
  Select-Object DisplayName, DisplayVersion, PSChildName | Format-Table -AutoSize

Section 'C:\Program Files\Java'
Get-ChildItem 'C:\Program Files\Java' -Force |
  Select-Object Mode, Name, @{n='JunctionTarget';e={$_.Target}} | Format-Table -AutoSize

Section 'Active toolchain'
$jc = Get-Command java  -ErrorAction SilentlyContinue
$cc = Get-Command javac -ErrorAction SilentlyContinue
Write-Output "java  path : $(if($jc){$jc.Source}else{'NOT ON PATH'})"
Write-Output "java  ver  : $(if($jc){(& java -version 2>&1)[0]}else{'-'})"
Write-Output "javac ver  : $(if($cc){(& javac -version 2>&1)}else{'NOT ON PATH'})"
$jhProc = $env:JAVA_HOME
$jhMach = [Environment]::GetEnvironmentVariable('JAVA_HOME','Machine')
if     ($jhProc)            { Write-Output "JAVA_HOME  : $jhProc" }
elseif ($jhMach)            { Write-Output "JAVA_HOME  : $jhMach  (set machine-wide; this shell predates it - reopen your terminal)" }
else                        { Write-Output "JAVA_HOME  : (unset)" }

Section 'JavaFX SDKs'
$found = $false
Get-ChildItem 'C:\Program Files\Java' -Directory -Force |
  Where-Object { $_.Name -match 'javafx-sdk' } | ForEach-Object {
    $found = $true
    $n = (Get-ChildItem "$($_.FullName)\lib" -Filter *.jar -ErrorAction SilentlyContinue).Count
    Write-Output "$($_.Name)  ->  $n jars in lib"
  }
if (-not $found) { Write-Output '!! no JavaFX SDK found' }

Section 'IntelliJ configuration'
$cfgRoot = Get-ChildItem "$env:APPDATA\JetBrains" -Directory |
           Where-Object { $_.Name -match '^IntelliJIdea' } | Sort-Object Name -Descending | Select-Object -First 1
if (-not $cfgRoot) {
  Write-Output '(no IntelliJ config found)'
} else {
  $opt = Join-Path $cfgRoot.FullName 'options'
  Write-Output "config dir : $($cfgRoot.Name)"
  Write-Output "IDE running: $(if((Get-Process idea64,idea -ErrorAction SilentlyContinue)){'YES - CLOSE IT before editing config'}else{'no (safe to edit)'})"

  Write-Output "-- registered SDKs (jdk.table.xml)"
  $t = Join-Path $opt 'jdk.table.xml'
  if (Test-Path $t) {
    ([xml](Get-Content $t -Raw)).application.component.jdk |
      ForEach-Object { Write-Output "   name='$($_.name.value)'  ->  $($_.homePath.value)" }
  } else { Write-Output '   (none)' }

  Write-Output "-- global 'javafx' library (applicationLibraries.xml)"
  $a = Join-Path $opt 'applicationLibraries.xml'
  if (Test-Path $a) {
    $roots = Select-String -Path $a -Pattern '<root url="file://([^"]+)"' -AllMatches |
             ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value }
    if ($roots) {
      $roots | Sort-Object -Unique | ForEach-Object { Write-Output "   $_" }
      if (($roots | Measure-Object).Count -gt ($roots | Sort-Object -Unique | Measure-Object).Count) {
        Write-Output "   (note: duplicate roots present - worth collapsing)"
      }
    } else { Write-Output '   (no roots)' }
  } else { Write-Output '   (file absent)' }

  Write-Output "-- new-project defaults (project.default.xml)"
  $d = Join-Path $opt 'project.default.xml'
  if (Test-Path $d) {
    (Select-String -Path $d -Pattern 'languageLevel="[^"]*" project-jdk-name="[^"]*"').Matches.Value |
      ForEach-Object { Write-Output "   $_" }
    $vm = (Select-String -Path $d -Pattern 'VM_PARAMETERS" value="([^"]*)"').Matches
    if ($vm) {
      $s = $vm[0].Groups[1].Value -replace '&quot;','"'
      Write-Output "   VM options: $s"
      if ($s -notmatch 'enable-native-access') { Write-Output "   !! missing --enable-native-access=javafx.graphics" }
    } else { Write-Output '   VM options: (none set)' }
  } else { Write-Output '   (file absent)' }
}

Section 'Reminder'
Write-Output 'Required versions change each term - confirm against https://taylorial.com/tools/java/'
