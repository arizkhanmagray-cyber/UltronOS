# Test log

What has actually been run, on what, and what has not. Update this file when
you test on new hardware.

## Environment

All tests so far ran in QEMU 8.2 **without hardware virtualisation** (TCG
emulation), 4 virtual cores, standard VGA, software rendering (Mesa llvmpipe).
That is a much slower and less forgiving environment than a real PC, and it
exercises none of the real GPU, Wi-Fi, audio, suspend or touchpad drivers.

## Results

| Test | Result |
|---|---|
| ISO builds from a clean tree (`scripts/build-iso.sh`, zstd) | pass, ~8 min with a warm package cache, ~15 min cold |
| ISO boots, legacy BIOS, themed boot menu | pass |
| Live session reaches the desktop; top bar, dock, rail, wallpaper as designed | pass |
| Installer starts by itself in the live session | pass |
| Installer: language → region → keyboard → *Erase disk* → account → summary → install | pass, all 31 jobs |
| Installed system boots from disk (BIOS/MBR), themed GRUB, boot dot | pass |
| Sign-in animation, then login with the password chosen in the installer | pass |
| Installed system: identifies as Ultron OS, no live/installer packages left, no failed units, zram active, apt sources clean | pass |
| Glass auto-off under software rendering (`ultron-glass` reports "software rendering", solid theme applied) | pass |
| Glass on with blur (forced on in the VM) | pass, see caveat below |
| `.exe` double-click path: 32-bit program through `ultron-run-windows` | pass |
| `.msi` path: self-built test MSI installs through `msiexec` | pass |
| UEFI boot and install | see "UEFI" below |

## Numbers (installed system, 4 GB VM, software rendering)

- Idle desktop after login: about 1.5 GB used, zram swap untouched. Software
  rendering inflates this; expect less with a real GPU driver.
- Boot: not meaningful under emulation (54 s in the VM).
- Installed size: about 7 GB (1.8 GB of that is Wine).

## Known issue found during testing

**KWin crashes when blur runs on llvmpipe under an emulated AVX2 CPU**
(QEMU TCG with `-cpu max`). The crash is inside Mesa's JIT-compiled code, and
it disappears with an emulated CPU that has no AVX (`-cpu Nehalem`). It is
most likely a QEMU emulation defect rather than an Ultron or KDE one, and it
cannot occur with a real GPU driver. It is nevertheless the reason
`ultron-glass` exists in `auto` mode: without a 3D driver the system never
asks the CPU to blur. If you test in QEMU without KVM, use `-cpu Nehalem`.

## Not tested

- **Any physical hardware.** Wi-Fi during install, suspend/resume, laptops
  with NVIDIA graphics, HiDPI screens and fractional scaling, touchpads.
- *Install alongside* (shrinking Windows) and *Replace a partition*.
- Printing, Bluetooth, Flatpak installs from Discover (the VM had no general
  internet access).
- Real-world Windows software in Wine beyond the two cases above.
- The GitHub Actions workflow (written but never executed).
- An `xz`-compressed release build (CI uses it; local tests used `zstd`).

## How to repeat

```sh
ULTRON_COMPRESSION=zstd ./build.sh      # fast build
scripts/vm-test.sh                      # UEFI, blank 32 GB disk attached
scripts/vm-test.sh --bios               # legacy BIOS
```

With KVM available the whole cycle (boot, install, reboot) takes a few minutes.
