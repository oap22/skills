# Zed config reference (macOS, Java/JavaFX + C/C++)

Substitute `<JDK_HOME>`, `<JFX_DIR>`, `<MainClass>`. Verified against Zed's docs and
`zed-extensions/java` v6.8.x in September 2026.

## Paths

| File | Location |
|---|---|
| `settings.json`, `keymap.json`, `tasks.json` | `~/.config/zed/` |
| global `debug.json` | `~/Library/Application Support/Zed/debug.json` (usually not grantable to an agent) |
| project overrides | `<project>/.zed/{settings,tasks,debug}.json` |
| installed extensions | `~/Library/Application Support/Zed/extensions/installed/` |
| `zed` CLI | `/Applications/Zed.app/Contents/MacOS/cli` |

`.vscode/launch.json` is read as a fallback when `.zed/debug.json` is absent.

## settings.json

```jsonc
{
  "auto_install_extensions": { "java": true },

  "languages": {
    "Java": { "tab_size": 4, "format_on_save": "on" },
    "C++":  { "tab_size": 4, "format_on_save": "on" },
    "C":    { "tab_size": 4, "format_on_save": "on" }
  },

  "lsp": {
    "jdtls": {
      "settings": {
        "java_home": "<JDK_HOME>",        // JDK 21+ to RUN jdtls itself
        "jdk_auto_download": false,        // else it pulls its own Corretto
        "min_memory": "1G",
        "max_memory": "2G",
        "lombok_support": false
      },
      "initialization_options": {
        "settings": {
          "java": {
            // IntelliJ "Global Library" equivalent. Required for projects
            // with no pom.xml/build.gradle, or javafx.* will not resolve.
            "project": {
              "referencedLibraries": ["lib/**/*.jar", "<JFX_DIR>/lib/*.jar"]
            },
            // IntelliJ "Project SDK" equivalent.
            "configuration": {
              "runtimes": [
                { "name": "JavaSE-25", "path": "<JDK_HOME>", "default": true }
              ],
              "updateBuildConfiguration": "interactive"
            },
            "format": { "enabled": true },
            "signatureHelp": { "enabled": true },
            "completion": { "importOrder": ["java", "javax", "javafx", "com", "org"] },
            "inlayHints": { "parameterNames": { "enabled": "literals" } }
          }
        }
      }
    },
    "clangd": {
      "arguments": [
        "--background-index",
        "--clang-tidy",
        "--header-insertion=never",
        "--completion-style=detailed"
      ]
    }
  }
}
```

`runtimes[].name` must be an execution-environment id: `JavaSE-1.8`, `JavaSE-11`,
`JavaSE-17`, `JavaSE-21`, `JavaSE-25`.

## `<project>/.zed/debug.json` — JavaFX

Adapter name comes from the extension's `extension.toml` (`[debug_adapters.Java]`).

```jsonc
[
  {
    "label": "<App> (JavaFX)",
    "adapter": "Java",
    "request": "launch",
    "mainClass": "<MainClass>",
    "modulePaths": ["<JFX_DIR>/lib"],
    "vmArgs": ["--add-modules=javafx.controls,javafx.fxml", "--enable-native-access=javafx.graphics"],
    "cwd": "$ZED_WORKTREE_ROOT",
    "stopOnEntry": false
  },
  {
    "label": "Attach to JVM (port 5005)",
    "adapter": "Java",
    "request": "attach",
    "hostName": "localhost",
    "port": 5005
  }
]
```

Put the JavaFX path in `modulePaths`, never in `vmArgs`. The adapter does not shell-parse
`vmArgs`, so a quoted path (`--module-path \"...\"`, copied from an IntelliJ
`VM_PARAMETERS` string) reaches the JVM with the quote characters included and fails with
`FindException: Module javafx.controls not found`. The adapter also builds its own module
path, and a second one passed through `vmArgs` can conflict with it.

Launch options: `mainClass`, `projectName`, `args`, `vmArgs`, `classPaths`
(`$Auto`/`$Runtime`/`$Test`), `modulePaths`, `cwd`, `env`, `stopOnEntry`.

C/C++ uses the built-in `CodeLLDB` adapter:

```jsonc
[
  {
    "label": "Debug current binary",
    "adapter": "CodeLLDB",
    "request": "launch",
    "program": "$ZED_WORKTREE_ROOT/build/<binary>",
    "cwd": "$ZED_WORKTREE_ROOT"
  }
]
```

## Running Java: the gutter ▶ and tasks

### Rules learned the hard way

- **Zed expands `$NAME` in task `command`/`args` itself**, before any shell runs. A shell
  variable Zed doesn't know (`JFX=...; javac --module-path "$JFX"`) becomes an empty
  string, and `javac --module-path ""` fails with `error: module not found: javafx.fxml`.
  Put the logic in a script and pass the script only `$ZED_*` variables. Running a task's
  args by hand in bash skips this substitution, so a passing bash test does not prove the
  task works. Only a run from inside Zed does.
- **The Java extension's own ▶ task ("Run Main") cannot run JavaFX.** For projects with no
  pom.xml or build.gradle, it runs `javac -d bin` and `java -cp bin` with no module path,
  and it never copies `.fxml` files.
- **A task tagged `java-main` takes over the ▶.** Zed's precedence is worktree
  `.zed/tasks.json`, then global `~/.config/zed/tasks.json`, then the extension
  (`templates_with_tags` in `crates/editor/src/runnables.rs`). Every ▶ the extension draws
  (main method, main class, implicit class) uses the `java-main` tag.
- **The ▶ binding is cached per open file.** Zed resolves it once and keeps it until the
  buffer changes (`has_cached`). After changing `tasks.json`, reopen the file or restart
  Zed. Otherwise the old task keeps running and the new config looks broken.

### Global runner: install once, every Java project works

`~/.config/zed/java-run.sh`:

```bash
#!/usr/bin/env bash
# Called by the java-main task in ~/.config/zed/tasks.json:
#   bash ~/.config/zed/java-run.sh <worktree-root> <package> <class>
set -euo pipefail

root="$1"; pkg="${2:-}"; cls="$3"
main="${pkg:+$pkg.}$cls"
cd "$root"

if [ -f pom.xml ]; then
    mvn -q compile exec:java -Dexec.mainClass="$main"
    exit
fi
if [ -f build.gradle ] || [ -f build.gradle.kts ]; then
    if [ -x ./gradlew ]; then ./gradlew run; else gradle run; fi
    exit
fi

if [ -d src/main/java ]; then srcdir=src/main/java
elif [ -d src ]; then srcdir=src
else srcdir=.
fi

mkdir -p out
find "$srcdir" -name '*.java' -not -path '*/test/*' -not -path './out/*' > out/sources.txt

fx=()
if grep -rqs --include='*.java' '^import javafx' "$srcdir"; then
    sdk=$(ls -d "$HOME"/Library/Java/javafx-sdk-*/lib 2>/dev/null | sort -V | tail -1 || true)
    if [ -z "$sdk" ]; then
        echo "This project uses JavaFX but no SDK was found at ~/Library/Java/javafx-sdk-*/lib" >&2
        exit 1
    fi
    echo "JavaFX: $sdk"
    fx=(--module-path "$sdk" --add-modules=ALL-MODULE-PATH)
    fxrun=("${fx[@]}" --enable-native-access=javafx.graphics)
fi

# ${a[@]+...} guards empty arrays under set -u on macOS's bash 3.2.
javac ${fx[@]+"${fx[@]}"} -d out @out/sources.txt
rsync -a --exclude='*.java' --exclude='out/' --exclude='.*' "$srcdir"/ out/

echo "--- running $main ---"
exec java ${fxrun[@]+"${fxrun[@]}"} -cp out "$main"
```

The script picks the newest SDK itself, so a new JavaFX version needs no config change.
The `rsync` step copies `.fxml`, `.css`, and images next to the classes. `javac` does not
move resources, and a missing `.fxml` surfaces as a confusing `LoadException` at runtime.

Global `~/.config/zed/tasks.json` entry:

```jsonc
{
  "label": "Java: run $ZED_CUSTOM_java_class_name",
  "command": "bash",
  "args": [
    "<HOME>/.config/zed/java-run.sh",
    "$ZED_WORKTREE_ROOT",
    "${ZED_CUSTOM_java_package_name:}",
    "$ZED_CUSTOM_java_class_name"
  ],
  "reveal": "always",
  "allow_concurrent_runs": false,
  "tags": ["java-main"]
}
```

`ZED_CUSTOM_java_package_name` and `ZED_CUSTOM_java_class_name` come from the extension's
`runnables.scm` captures. `${VAR:}` gives an empty default for classes with no package.

Verified on 2026-09-18 with Zed 1.20.2 and `java` extension v6.8.27: the checkers JavaFX
lab (package + fxml), a plain packaged class, and a single-file class with no `src/`.
Maven and Gradle handoff is untested.

### Per-project override (optional)

A project needs its own task only when the global runner guesses wrong, for example a
different source root or a non-JavaFX module. Use the same pattern: a script in `.zed/`,
and a thin task that calls it.

```jsonc
[
  {
    "label": "<App>: run",
    "command": "bash",
    "args": [".zed/<app>.sh", "run"],
    "cwd": "$ZED_WORKTREE_ROOT",
    "reveal": "always",
    "tags": ["java-main"]
  }
]
```

Task variables: `$ZED_FILE`, `$ZED_DIRNAME`, `$ZED_WORKTREE_ROOT`, plus the
`ZED_CUSTOM_*` captures from the language's `runnables.scm`.

## Validating JSONC before trusting it

Zed accepts comments and trailing commas; `json.loads` does not. A malformed block is
silently ignored by Zed rather than reported, so validate every file after writing:

```python
import json, re
def load_jsonc(path):
    s = open(path).read()
    out, in_str, esc, i = [], False, False, 0
    while i < len(s):
        c = s[i]
        if in_str:
            out.append(c)
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
            i += 1; continue
        if c == '"': in_str = True; out.append(c); i += 1; continue
        if c == '/' and i + 1 < len(s) and s[i+1] == '/':
            while i < len(s) and s[i] != '\n': i += 1
            continue
        out.append(c); i += 1
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', "".join(out)))
```

## Install-script skeleton (the user runs this)

```bash
#!/usr/bin/env bash
set -uo pipefail
JFX_VERSION="<VER>"; JFX_DIR="$HOME/Library/Java/javafx-sdk-${JFX_VERSION}"

# 1. JavaFX SDK
curl -fL -o /tmp/javafx.zip \
  "https://download2.gluonhq.com/openjfx/${JFX_VERSION}/openjfx-${JFX_VERSION}_osx-aarch64_bin-sdk.zip"
unzip -q -o /tmp/javafx.zip -d "$HOME/Library/Java"
xattr -dr com.apple.quarantine "$JFX_DIR"     # REQUIRED or natives won't load

# 2. zed CLI (user-owned dir, no sudo)
ln -sf /Applications/Zed.app/Contents/MacOS/cli /opt/homebrew/bin/zed

# 3. shell env (idempotent: grep before appending)
#    export JAVA_HOME="$(/usr/libexec/java_home -v <MAJOR>)"
#    export PATH_TO_FX="$JFX_DIR/lib"

# 4. smoke test: javac a minimal Application subclass against --module-path
```

Make it idempotent and re-runnable; the user will run it more than once.

## Known-good versions observed

| Component | Value |
|---|---|
| JDK | Temurin 25 (`/Library/Java/JavaVirtualMachines/temurin-25.jdk/Contents/Home`) |
| JavaFX | 25.0.2, `~/Library/Java/javafx-sdk-25.0.2` |
| clangd | Apple's, `/usr/bin/clangd`, from Xcode |
| `java` extension | `zed-extensions/java` v6.8.x, id `java` |

Re-verify rather than assuming these are still current.
