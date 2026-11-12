#!/usr/bin/env bash
# Builds the Ultron OS ISO. Must run as root on Debian 13 (trixie) — either
# natively or inside the container that ./build.sh starts for you.
#
#   ULTRON_VERSION       version string baked into the image   (default 1.0)
#   ULTRON_COMPRESSION   xz (small, slow) | zstd (fast, ~15% bigger) (default xz)
#   ULTRON_WORK          scratch directory, needs ~20 GB       (default /var/tmp/ultron-build)
#   ULTRON_OUT           where the .iso is written             (default <repo>/out)
#   ULTRON_MIRROR        Debian mirror used during the build
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ULTRON_VERSION="${ULTRON_VERSION:-1.0}"
export ULTRON_COMPRESSION="${ULTRON_COMPRESSION:-xz}"
WORK="${ULTRON_WORK:-/var/tmp/ultron-build}"
OUT="${ULTRON_OUT:-${SRC}/out}"

die() { echo "error: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "must run as root (live-build needs chroot and mount)"
. /etc/os-release
[ "${VERSION_CODENAME:-}" = "trixie" ] || die "build host must be Debian 13 (trixie); use ./build.sh to build in a container"

if ! command -v lb >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y --no-install-recommends \
        live-build debootstrap xorriso squashfs-tools mtools dosfstools \
        grub-pc-bin grub-efi-amd64-bin grub-efi-ia32-bin \
        cpio xz-utils zstd rsync ca-certificates
fi

mkdir -p "${WORK}" "${OUT}"
cd "${WORK}"

# Start from a clean tree but keep live-build's package cache (cache/).
if [ -d auto ]; then lb clean || true; fi
mkdir -p auto config
rsync -a --delete "${SRC}/live-build/auto/" auto/
rsync -a --delete "${SRC}/live-build/config/" config/
chmod +x auto/* config/hooks/normal/*.hook.chroot 2>/dev/null || true

lb config
lb build

ISO="$(ls -1 ./*.iso 2>/dev/null | head -n1 || true)"
[ -n "${ISO}" ] || die "live-build finished without producing an ISO — see ${WORK}/build.log"

FINAL="${OUT}/ultronos-${ULTRON_VERSION}-amd64.iso"
mv -f "${ISO}" "${FINAL}"
( cd "${OUT}" && sha256sum "$(basename "${FINAL}")" > "$(basename "${FINAL}").sha256" )
echo
echo "Built: ${FINAL} ($(du -h "${FINAL}" | cut -f1))"
