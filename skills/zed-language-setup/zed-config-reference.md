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
    "vmArgs": "--module-path \"<JFX_DIR>/lib\" --add-modules=javafx.controls,javafx.fxml --enable-native-access=javafx.graphics",
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

## `<project>/.zed/tasks.json` — JavaFX build/run without the debugger

```jsonc
[
  {
    "label": "<App>: run",
    "command": "bash",
    "args": ["-lc", "JFX=\"<JFX_DIR>/lib\"; mkdir -p out && javac --module-path \"$JFX\" --add-modules=javafx.controls,javafx.fxml -d out $(find src -name '*.java') && rsync -a --include='*/' --include='*.fxml' --include='*.css' --exclude='*' src/ out/ && java --module-path \"$JFX\" --add-modules=javafx.controls,javafx.fxml --enable-native-access=javafx.graphics -cp out <MainClass>"],
    "cwd": "$ZED_WORKTREE_ROOT",
    "reveal": "always"
  }
]
```

`.fxml` and `.css` must be copied next to the compiled classes — `javac` does not move
resources, and a missing `.fxml` surfaces as a confusing `LoadException` at runtime.

Task variables: `$ZED_FILE`, `$ZED_DIRNAME`, `$ZED_WORKTREE_ROOT`.

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
