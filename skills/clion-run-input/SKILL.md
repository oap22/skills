---
name: clion-run-input
description: "Switch a CLion CMake run configuration between stdin from a file and interactive console input. Use for \"stop using sample.in\", \"type input by hand\", or \"redirect input from a file\" on a CLion target."
---

# CLion run-configuration stdin redirect

Stdin redirection is a property of the CLion run configuration, not the source.
To change how a target gets its input, edit the run configuration, not the code.

## Where it lives

CLion stores per-target run configs in `.idea/workspace.xml` at the project root,
under `<component name="RunManager">`, as `<configuration type="CMakeRunConfiguration" ...>`
elements — one per target, matched by `TARGET_NAME`. `workspace.xml` is normally
local/gitignored, so edits here only affect the machine you're on. A config with
"Store as project file" on lives in its own file instead (`.idea/runConfigurations/*.xml`
or `*.run.xml`, often committed), with the same attributes; editing it reaches teammates.

Redirect-from-file looks like:

```xml
<configuration name="TrackingFluids" type="CMakeRunConfiguration" factoryName="Application"
    REDIRECT_INPUT="true" REDIRECT_INPUT_PATH="$PROJECT_DIR$/lab01/sample.in"
    ELEVATE="false" USE_EXTERNAL_CONSOLE="false" EMULATE_TERMINAL="false"
    PASS_PARENT_ENVS_2="true" PROJECT_NAME="..." TARGET_NAME="TrackingFluids"
    CONFIG_NAME="Debug" RUN_TARGET_PROJECT_NAME="..." RUN_TARGET_NAME="TrackingFluids">
```

Interactive-console looks like the same element with `REDIRECT_INPUT="false"` and
no `REDIRECT_INPUT_PATH` attribute at all.

## Steps

1. Find `.idea/workspace.xml` (`find <project-root> -maxdepth 2 -path '*/.idea/workspace.xml'`). If it is missing, ask which directory CLion opened.
2. Search that file, plus any shared config files above, for the target name (e.g. `TrackingFluids`) to locate its `<configuration ...>` line under `RunManager`. Ignore the separate `CMakeRunConfigurationManager` block earlier in the file — that one doesn't carry stdin settings.
3. To switch **to interactive typing**: set `REDIRECT_INPUT="false"` and delete the `REDIRECT_INPUT_PATH="..."` attribute entirely (a leftover path with `REDIRECT_INPUT="false"` is harmless but confusing — remove it).
4. To switch **to reading from a file**: confirm the file exists; if the target or file is ambiguous, list the candidates and ask once. Then set `REDIRECT_INPUT="true"` and add `REDIRECT_INPUT_PATH="$PROJECT_DIR$/<relative/path/to/file>"` right after it. Use `$PROJECT_DIR$` rather than an absolute path so the config stays portable; a bare relative path resolves against the config's Working directory, not the project root. `$FilePrompt$` asks for a file on every run.
5. Re-read the file to confirm the edit, and report the file, configuration name, and old and new `REDIRECT_INPUT`/`REDIRECT_INPUT_PATH` values. Ask the user to check **Redirect input from** in Run > Edit Configurations before running; if it does not match, an open CLion kept its in-memory copy, so set it in that dialog instead.

## Gotchas

- If no `<configuration>` block exists yet for the target (first run), CLion generates one automatically the first time the target is run from the IDE; edit it after that first run rather than hand-authoring the whole block.
