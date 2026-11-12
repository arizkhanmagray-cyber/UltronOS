#!/usr/bin/env bash
# Builds the Ultron OS ISO on any Linux machine that has Docker (or Podman).
#
#   ./build.sh                         # release build (xz, smallest ISO)
#   ULTRON_COMPRESSION=zstd ./build.sh # ~3x faster, ISO ~15% larger
#
# The result lands in ./out/. Needs ~20 GB of free disk and a network
# connection; takes 30-60 minutes on a 4-core machine.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# Already on Debian 13 as root? Then build natively, no container needed.
if [ "$(id -u)" -eq 0 ] && grep -qs '^VERSION_CODENAME=trixie$' /etc/os-release \
   && [ -z "${ULTRON_FORCE_CONTAINER:-}" ]; then
    exec ./scripts/build-iso.sh
fi

ENGINE="${ULTRON_ENGINE:-}"
if [ -z "${ENGINE}" ]; then
    if command -v docker >/dev/null 2>&1; then ENGINE=docker
    elif command -v podman >/dev/null 2>&1; then ENGINE=podman
    else
        echo "error: need Docker or Podman (or run scripts/build-iso.sh as root on Debian 13)" >&2
        exit 1
    fi
fi

mkdir -p out
# live-build needs chroot + mount, hence --privileged. The named volume keeps
# the downloaded packages between runs, so rebuilds are much faster.
exec "${ENGINE}" run --rm --privileged \
    -v "${PWD}:/src" \
    -v "${ULTRON_CACHE_VOLUME:-ultronos-build}:/var/tmp/ultron-build" \
    -e ULTRON_VERSION="${ULTRON_VERSION:-1.0}" \
    -e ULTRON_COMPRESSION="${ULTRON_COMPRESSION:-xz}" \
    -e ULTRON_OUT=/src/out \
    ${ULTRON_MIRROR:+-e ULTRON_MIRROR="${ULTRON_MIRROR}"} \
    debian:trixie /src/scripts/build-iso.sh
