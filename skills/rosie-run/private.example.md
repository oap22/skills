# Private values: rosie-run

Copy this file to `private.local.md` in the same folder and fill in the values. `*.local.md` is gitignored, so the real values stay off the public repo.

| Placeholder | Value |
|---|---|
| `<login-node>` | Fully qualified hostname of the Rosie login node (the `HostName` under `Host rosie` in `~/.ssh/config`) |
| `<cluster-user>` | Owen's Rosie username (the `User` under `Host rosie`) |
| `<cluster-domain>` | Domain segment of the Rosie home path (`/home/<cluster-domain>/<cluster-user>`) |
| `<github-user>` | Owen's GitHub username (the account `ssh -T git@github.com` reports from Rosie) |
