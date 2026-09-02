---
name: swe2410-java-setup
description: Verify, install, or repair the Java JDK + JavaFX + IntelliJ setup required by MSOE SWE 2410 (and other taylorial.com-based courses) on Windows. Use when the user asks to check their Java/JavaFX versions, says a JavaFX lab won't run or won't compile, mentions "module-path"/"JavaFX not configured"/"unresolved SDK" errors, is starting a new lab from swe2410-*.gitlab.io, or needs to upgrade to a new JDK/JavaFX version for the course.
---

# SWE 2410 Java + JavaFX setup (Windows)

Gets a Windows machine onto the exact JDK and JavaFX versions the course requires, wires
up IntelliJ, and proves it works by actually running a JavaFX app.

## Step 1 — Read the required versions (never hardcode them)

**The course bumps these every term. Always re-read the source of truth.**

The lab pages (`https://swe2410-9315a1.gitlab.io/lab1/` etc.) deliberately do *not* state
versions — they defer to the instructor's install page:

    https://taylorial.com/tools/java/

Fetch that page and extract the current JDK and JavaFX versions. Version strings appear as
`jdk-<VER>` and `javafx-sdk-<VER>` in the install paths. A quick extraction:

```powershell
$r = Invoke-WebRequest -Uri 'https://taylorial.com/tools/java/' -UseBasicParsing
$t = $r.Content -replace '<[^>]+>',' ' -replace '\s+',' '
[regex]::Matches($t,'(?i)(jdk-|javafx-sdk-)[0-9][0-9.]*') | ForEach-Object { $_.Value } | Sort-Object -Unique
```

That page also carries the canonical VM options string and the IntelliJ click-path, and it
footnotes that you should substitute whatever patch version you actually downloaded.

## Step 2 — Survey what's installed

Run `scripts/check-setup.ps1`. It reports installed JDKs, JavaFX SDKs, `JAVA_HOME`, the
`java`/`javac` on PATH, and every relevant IntelliJ config value. Diff that against Step 1.

## Step 3 — Install

Downloads (substitute the version from Step 1; `latest` is correct for Oracle):

- JDK: `https://download.oracle.com/java/<MAJOR>/latest/jdk-<MAJOR>_windows-x64_bin.msi`
- JavaFX: `https://download2.gluonhq.com/openjfx/<VER>/openjfx-<VER>_windows-x64_bin-sdk.zip`

**Oracle's `latest` will usually be a higher patch than the tutorial names** (e.g. tutorial
says 25.0.2, Oracle ships 25.0.4.1). That is expected and fine — the tutorial explicitly
says to use the version you actually downloaded. Just keep every path consistent afterward.

Installation needs elevation and the user is typically an admin but *not* elevated.
**Batch all elevated work into ONE script and launch it with a single
`Start-Process pwsh -Verb RunAs -Wait`** so the user clicks one UAC prompt instead of four.
That script should:

1. `msiexec /i <jdk msi> /qn /norestart` — silent JDK install
2. Copy the unzipped `javafx-sdk-<VER>` into `C:\Program Files\Java\`
3. Create the compatibility junction (see below)
4. `[Environment]::SetEnvironmentVariable('JAVA_HOME', <jdk path>, 'Machine')`
5. Write a log to disk so the unelevated session can read the outcome

### The javafx-sdk-N junction (important)

The course's own starter zips hardcode `javafx-sdk-25` (**no patch suffix**) in their run
configurations, while the tutorial tells students to use `javafx-sdk-25.0.2`. Rather than
pick one, create a directory junction so both resolve:

```powershell
New-Item -ItemType Junction -Path 'C:\Program Files\Java\javafx-sdk-<MAJOR>' `
         -Target 'C:\Program Files\Java\javafx-sdk-<FULLVER>'
```

Any project the student unzips then works regardless of which convention it uses, with no
per-lab hand-editing of VM options.

## Step 4 — Configure IntelliJ

**Close IntelliJ first.** It rewrites these files from memory on exit and will silently
revert your edits. Verify with `Get-Process idea64` and back the files up before writing.

Config lives in `%APPDATA%\JetBrains\IntelliJIdea<YEAR>.<N>\options\`:

| File | What to change |
|---|---|
| `jdk.table.xml` | Add a `<jdk>` entry **named exactly the major version** (`25`) — starter projects reference the SDK by that name |
| `applicationLibraries.xml` | Global library `javafx` → `<VER>\lib`. Collapse duplicate roots; repeated "add library" clicks leave 3+ copies |
| `project.default.xml` | New-project defaults: `languageLevel`/`project-jdk-name`, **and** the `RunManager` VM options template |

VM options template (must match the tutorial exactly):

```
--module-path "C:\Program Files\Java\javafx-sdk-<VER>\lib" --add-modules=javafx.controls,javafx.fxml --enable-native-access=javafx.graphics
```

`--enable-native-access=javafx.graphics` is newer than most existing setups and suppresses a
native-access warning on modern JDKs. Setups carried over from a previous term usually lack it.

**Generate the JDK's module roots from the real JDK — do not copy the previous entry's list.**
Module sets differ between releases:

```powershell
& "$jdkHome\bin\java.exe" --list-modules | ForEach-Object { ($_ -split '@')[0] } | Sort-Object -Unique
```

Build `<classPath>` roots as `jrt://<home>!/<module>` and `<sourcePath>` as
`jar://<home>/lib/src.zip!/<module>`. Use forward slashes in IntelliJ paths. Validate each
file parses as XML afterward (`[xml](Get-Content $f -Raw)`).

## Step 5 — Verify by actually running something

Config that looks right still fails. Compile and launch a real JavaFX app:

```powershell
$fx='C:\Program Files\Java\javafx-sdk-<MAJOR>\lib'
javac --module-path $fx --add-modules=javafx.controls,javafx.fxml -d $out $sources
# copy any .fxml resources next to the classes, then:
java --module-path $fx --add-modules=javafx.controls,javafx.fxml `
     --enable-native-access=javafx.graphics -cp $out <MainClass>
```

Launch it with `Start-Process -PassThru` plus redirected stderr, sleep ~10s, confirm
`HasExited` is false, then stop it. **Success is: window stays up AND stderr is completely
empty.** A stray native-access warning means `--enable-native-access` didn't take.

## Step 6 — Removing an old JDK (only when asked)

1. **Scan for references first**, or you'll break other coursework:
   `grep -rn 'jdk-<OLD>|javafx-sdk-<OLD>|JDK_<OLD>|"<OLD>"' <project roots> --include=*.xml --include=*.iml`
   Migrate any hits to the new version before uninstalling.
2. Remove the stale `<jdk>` entry from `jdk.table.xml`.
3. Get the MSI product code and uninstall silently (elevated):
   ```powershell
   Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
     Where-Object DisplayName -match 'Java|JDK' | Select DisplayName,PSChildName
   msiexec /x '{PRODUCT-CODE}' /qn /norestart
   ```
4. Delete the JavaFX SDK folder (it's just an unzipped directory, no uninstaller).
5. **Re-verify `java -version` after uninstalling** — the shared
   `C:\Program Files\Common Files\Oracle\Java\javapath` shim is MSI-managed and worth
   confirming still resolves to the surviving JDK. Then re-run Step 5.

## Notes

- A leftover `~\.openjfx\cache\<ver>` directory is from Maven/Gradle JavaFX plugins, unrelated
  to the SDK install, and harmless.
- Checkstyle for MSOE: `https://csse.msoe.us/csc1110/MSOE_checkStyle.xml`, configured in the
  CheckStyle-IDEA component of `project.default.xml`.
- Scene Builder is listed on the tutorial page too, but no lab so far requires it.
