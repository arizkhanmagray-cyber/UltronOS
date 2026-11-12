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
| GitHub Actions workflow builds the `xz` ISO and uploads it as an artifact | pass, 17 min, 2.48 GB |
| ISO boots, legacy BIOS, themed boot menu | pass |
| Live session reaches the desktop; top bar, dock, rail, wallpaper as designed | pass |
| Installer starts by itself in the live session | pass |
| Installer: language → region → keyboard → *Erase disk* → account → summary → install | pass, all 31 jobs |
| Installed system boots from disk (BIOS/MBR), themed GRUB, boot dot | pass |
| Sign-in animation, then login with the password chosen in the installer | pass |
| Installed system: identifies as Ultron OS, no live/installer packages left, no failed units, zram active, apt sources clean | pass |
| Glass auto-off under software rendering (`ultron-glass` reports "software rendering", solid theme applied) | pass |
| Glass on with blur (forced on in the VM) | pass, see caveat below |
| `.exe`: 32-bit program runs through `ultron-run-windows` | pass |
| `.exe` opened from the file manager: file manager asks "Execute?", then the trust prompt appears | pass |
| `.msi` path: self-built test MSI installs through `msiexec` | pass |
| `.deb` opened from the file manager: confirm → installed by apt → success message; installed program runs | pass (live session, where no password is asked; see below) |
| File associations: `.deb`, `.AppImage`, `.rpm`, `.run` → `ultron-install-file`; Flatpak files → Discover | pass |
| ISO boots under UEFI with **Secure Boot enforced** (`mokutil`: "SecureBoot enabled") | pass |
| Installer on UEFI: creates a 512 MB EFI partition, completes ("All done") | pass |
| Installed system boots under UEFI + Secure Boot through its own GRUB to the sign-in screen | pass |

## Numbers (installed system, 4 GB VM, software rendering)

- Idle desktop after login: about 1.5 GB used, zram swap untouched. Software
  rendering inflates this; expect less with a real GPU driver.
- Boot: not meaningful under emulation (54 s in the VM).
- Installed size: about 7 GB (1.8 GB of that is Wine).
- ISO: 2.64 GB with `zstd`, 2.48 GB with `xz`.

## Known issue found during testing

**KWin crashes when blur runs on llvmpipe under an emulated AVX2 CPU**
(QEMU TCG with `-cpu max`). The crash is inside Mesa's JIT-compiled code, and
it disappears with an emulated CPU that has no AVX (`-cpu Nehalem`). It is
most likely a QEMU emulation defect rather than an Ultron or KDE one, and it
cannot occur with a real GPU driver. It is nevertheless the reason
`ultron-glass` exists in `auto` mode: without a 3D driver the system never
asks the CPU to blur. If you test in QEMU without KVM, use `-cpu Nehalem`.

## Bugs found and fixed by these tests

- Boot menu fell back to text mode (wrong font path in the GRUB config).
- Window frame showed tick marks along its edges (stroked SVG hairlines get a
  padded bounding box; redrawn as filled shapes).
- File manager opened with every side panel visible (a config override had
  suppressed its first-run defaults).
- `hwclock` missing from the image (separate package in Debian 13).
- Kernel command line carried `splash` twice.
- Display blanked during a long install in the live session.
- `.deb` installs failed silently: `pkexec` is a separate package in Debian 13
  and was not in the image, and the handler treated that as a cancel.

## Not tested

- The password prompt of the `.deb` installer on an **installed** system. The
  live session grants admin rights without a password, so the prompt itself
  was not exercised there.
- AppImage and `.run` files beyond their file association.
- Logging in and reaching the desktop on the UEFI-installed system (verified
  up to the sign-in screen; the login itself was verified on the BIOS install,
  which shares everything after the bootloader).
- **Any physical hardware.** Wi-Fi during install, suspend/resume, laptops
  with NVIDIA graphics, HiDPI screens and fractional scaling, touchpads.
- *Install alongside* (shrinking Windows) and *Replace a partition*.
- Printing, Bluetooth, Flatpak installs from Discover (the VM had no general
  internet access).
- Real-world Windows software in Wine beyond the two cases above.
- Booting the `xz` ISO produced by GitHub Actions (it built successfully;
  the local boot and install tests used `zstd` builds of the same tree).

## How to repeat

```sh
ULTRON_COMPRESSION=zstd ./build.sh      # fast build
scripts/vm-test.sh                      # UEFI, blank 32 GB disk attached
scripts/vm-test.sh --bios               # legacy BIOS
```

With KVM available the whole cycle (boot, install, reboot) takes a few minutes.
