---
name: clion-run-input
description: Switch a CLion CMake run configuration between reading stdin from a file and reading it interactively from the console. Use when the user says a program "uses sample.in", wants to "stop using the sample input file", "type input by hand", "run it interactively instead of redirecting", or wants to "set input via a file" / "redirect input from a file" for a CLion target.
---

# CLion run-configuration stdin redirect

A C++ program that reads via `cin` doesn't reference any input file in its own
source — the file only gets fed to it because CLion's run configuration for that
target has stdin redirection turned on. To change how a target gets its input,
edit the run configuration, not the code.

## Where it lives

CLion stores per-target run configs in `.idea/workspace.xml` at the project root,
under `<component name="RunManager">`, as `<configuration type="CMakeRunConfiguration" ...>`
elements — one per target, matched by `TARGET_NAME`. `workspace.xml` is normally
local/gitignored, so edits here only affect the machine you're on.

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

1. Find `.idea/workspace.xml` in the project root (`find <project-root> -maxdepth 1 -iname workspace.xml`, or `Grep` for `RunManager`).
2. Grep that file for the target name (e.g. `TrackingFluids`) to locate its `<configuration ...>` line under `RunManager`. Ignore the separate `CMakeRunConfigurationManager` block earlier in the file — that one doesn't carry stdin settings.
3. To switch **to interactive typing**: set `REDIRECT_INPUT="false"` and delete the `REDIRECT_INPUT_PATH="..."` attribute entirely (a leftover path with `REDIRECT_INPUT="false"` is harmless but confusing — remove it).
4. To switch **to reading from a file**: set `REDIRECT_INPUT="true"` and add `REDIRECT_INPUT_PATH="$PROJECT_DIR$/<relative/path/to/file>"` right after it. Use CLion's `$PROJECT_DIR$` macro rather than an absolute path so the config stays portable.
5. Tell the user to reopen/rerun the configuration in CLion (or just hit Run again) — no CLion restart needed, but if CLion has the workspace already open it may need the run configuration re-selected to pick up the file change.

## Rules

- Never edit the source `.cpp`/`.cmake` files to solve this — a program reading `cin` correctly has nothing to change; the input source is purely a run-config setting.
- Don't confuse this with the `CMakeRunConfigurationManager` `<config projectName=... targetName=.../>` entries earlier in the file — those just register the target for the CMake tool window and have no stdin fields.
- If no `<configuration>` block exists yet for the target (first run), CLion generates one automatically the first time the target is run from the IDE; edit it after that first run rather than hand-authoring the whole block.
