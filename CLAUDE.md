# Gramps Syncloud app

Packaging of Gramps Web (ghcr.io/gramps-project/grampsweb) as a Syncloud snap.
Follow the latest porting guide: https://github.com/syncloud/platform/wiki/App-porting-guide

## Conventions applied here
- No comments in code (shell, jsonnet, Go, Python, TS). Rationale goes in commit messages.
- `meta/snap.yaml`: no `confinement`, `plugs` or `slots`; every daemon has `restart-condition: always`,
  `start-timeout: 600s`, `restart-delay: 10s`; runtime subcommands go through `bin/cli <cmd>`.
- Snap hooks are separate Go binaries (`cli/cmd/<hook>`), built `CGO_ENABLED=0` by `cli/build.sh`
  (runs `go test ./...` first). Logic lives in `cli/installer`. The app user is created in the
  install hook; configure writes `$SNAP_DATA/version` last, post-refresh clears it, and every
  launcher calls `bin/wait-for-configure.sh`.
- Bundled runtimes (python from the grampsweb image, redis from the redis image) are launched through
  their own loader: `ld-linux*.so*` from `lib/*-linux-gnu*`, never the host glibc and never `ld-*.so`.
- Internal comms over unix sockets only: gunicorn on `/var/snap/gramps/common/web.socket`, redis on
  `/var/snap/gramps/current/redis.sock`. Logs go to stdout/stderr (journal), never to files.
- Auth is currently LDAP (patched into gramps_webapi by `gramps/build.sh`). Upstream supports OIDC
  (`OIDC_*` in gramps.cfg); moving to Authelia OIDC is the pending modernization step.

## CI (.drone.jsonnet)
- Push trigger only. Every step calls a committed script: `redis/build.sh`, `gramps/build.sh`,
  `cli/build.sh`, `*/test.sh`, `package.sh <app> $DRONE_BUILD_NUMBER` (writes the version file),
  `ci/test.sh <spec> <distro> <app>`, `test/e2e/run.sh <spec>`.
- Matrix: amd64 + arm64, bookworm + buster, one multi-arch image `syncloud/platform-<distro>:<platform>`
  with the `snapd_hold` entrypoint. Buster apt mirrors are gone: never use buster images for build steps.
- Network installs go through `apt.sh` (retry helper).
- UI tests are Playwright in `test/e2e` (image `mcr.microsoft.com/playwright:v1.59.1-jammy`,
  `@playwright/test` pinned to the same version). Upgrade chain: e2e, test-upgrade-prev,
  e2e-before-upgrade, test-upgrade, e2e-after-upgrade. Screenshots go to `artifact/screenshots`.
- Gramps Web UI uses Material 3 web components (`md-*`) inside shadow DOM; Playwright CSS pierces it.
  Specs can be checked locally against a plain `ghcr.io/gramps-project/grampsweb:<version>` container.
- `02-pre-upgrade` runs on the store's released version, so helpers must work on both the released
  UI (24.12 used `mwc-*`/`grampsjs-list-item`) and the new one; check both locally before pushing.
- Publish only from the `stable` branch via `syncloud/store-publisher`.

## Debugging CI
- Builds: `curl -s "http://ci.syncloud.org:8080/api/repos/syncloud/gramps/builds?limit=5"`
- Step log: `curl -s "http://ci.syncloud.org:8080/api/repos/syncloud/gramps/builds/{N}/logs/{stage}/{step}"`
- Artifacts: `http://ci.syncloud.org:8081/files/gramps/{build}-{arch}/`

## Local validation
- `docker run --rm -v $PWD:/drone/src -w /drone/src <step image> ./<step script>` for each build step,
  then run `redis/test.sh`, `gramps/test.sh`, `cli/test.sh` inside `syncloud/platform-{bookworm,buster}:<platform>`
  with `--entrypoint /bin/bash`.
