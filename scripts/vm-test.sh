#!/usr/bin/env bash
# Boots the built ISO in QEMU so you can try it before touching real hardware.
#
#   scripts/vm-test.sh                 # UEFI, with a blank 32 GB disk to install onto
#   scripts/vm-test.sh --bios          # legacy BIOS instead of UEFI
#   scripts/vm-test.sh path/to.iso
#
# Needs qemu-system-x86_64 (and the "ovmf" package for UEFI). Uses KVM when
# available; without it the VM still works but is several times slower.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

FIRMWARE=uefi
ISO=""
for arg in "$@"; do
    case "$arg" in
        --bios) FIRMWARE=bios ;;
        --uefi) FIRMWARE=uefi ;;
        *) ISO="$arg" ;;
    esac
done
[ -n "$ISO" ] || ISO="$(ls -1 out/*.iso 2>/dev/null | head -n1 || true)"
[ -f "$ISO" ] || { echo "error: no ISO found; build one with ./build.sh" >&2; exit 1; }

DISK="${ULTRON_VM_DISK:-out/vm-disk.qcow2}"
mkdir -p "$(dirname "$DISK")"
[ -f "$DISK" ] || qemu-img create -f qcow2 "$DISK" 32G >/dev/null

ARGS=(-machine q35 -smp 4 -m 8192 -cdrom "$ISO"
      -drive "file=$DISK,if=virtio,format=qcow2"
      -device virtio-vga -display gtk -usb -device usb-tablet
      -netdev user,id=n0 -device virtio-net-pci,netdev=n0
      -device ich9-intel-hda -device hda-duplex)
if [ -w /dev/kvm ]; then ARGS+=(-accel kvm -cpu host); else ARGS+=(-accel tcg,thread=multi -cpu max); fi
if [ "$FIRMWARE" = uefi ]; then
    for fw in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/ovmf/OVMF.fd /usr/share/edk2/ovmf/OVMF_CODE.fd; do
        [ -f "$fw" ] && { ARGS+=(-drive "if=pflash,format=raw,readonly=on,file=$fw"); break; }
    done
fi
# Boot the USB/CD first only while the disk is still empty.
ARGS+=(-boot menu=on,order=cd)
exec qemu-system-x86_64 "${ARGS[@]}"
