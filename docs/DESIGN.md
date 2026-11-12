# Design notes

Why Ultron OS is built the way it is. Read this before changing the foundations.

## It is a remix, on purpose

Writing a kernel, drivers, a graphics stack and an app ecosystem is thousands of
person-years. Every desktop Linux system people actually use (Ubuntu, Mint,
elementary, Zorin, SteamOS) is a remix of a base distribution. Ultron OS takes
Debian 13 for the base and spends its own effort where it is visible: the
desktop, the defaults and the installer.

**Debian stable** was chosen over Ubuntu and Arch because it changes slowly
(a themed desktop breaks when the desktop underneath is updated weekly), has no
snap or account tie-ins to strip out, and ships the official `live-build`
tooling that produces the ISO.

## KDE Plasma, not GNOME

The reference mock-up looks like a GNOME rice, but GNOME can only get there
through third-party shell extensions that break on every GNOME release, and it
cannot blur ordinary app windows at all. Plasma does every element natively and
through plain config files:

| Element in the mock-up | How it is done |
|---|---|
| Top bar with logo, workspaces, status icons, clock, power | a Plasma panel: Kickoff (icon set to the U), Pager, System Tray, Digital Clock, Lock/Logout |
| Floating dock | a Plasma panel in *fit content* + *floating* mode with an Icons-Only Task Manager |
| Left launcher rail | a second floating panel with launcher icons |
| Frosted glass | KWin blur + background contrast; Kvantum makes Qt app windows translucent |
| Traffic-light buttons | a custom Aurorae window decoration (`assets/aurorae/gen_aurorae.py`) |
| Monochrome look | "Ultron Dark" colour scheme, Papirus icons with graphite folders |

Plasma is also lighter than its reputation: a fresh session idles below 1.5 GB.

The dock and the rail both use "dodge windows", so they slide away instead of
taking space from maximised windows. That matters on 1366x768 laptop screens,
which are common in the 8 GB / 4-core class.

## How defaults are applied

Nothing is written into a user's home directory at build time. Defaults come
from three layers that Plasma already understands:

1. `/etc/xdg/*` (kdeglobals, kwinrc, …): system-wide fallbacks. A user's own
   settings always win, and a "Reset to defaults" in System Settings returns to
   the Ultron look rather than to stock Breeze.
2. The global theme `org.ultronos.desktop`: its `layout.js` creates the panels
   on a user's first login.
3. Theme data in `/usr/share` (colour scheme, decoration, wallpaper, Kvantum).

The Kvantum theme and the grey folder icons are **derived at build time** from
packaged upstream themes (hook `6010-ultron-theme`) rather than copied into the
repository. Upstream fixes flow in on the next build, and the repository stays
small and licence-clean.

## Staying upgradable

- `/usr/lib/os-release` is replaced through `dpkg-divert`, so Debian's
  `base-files` updates never overwrite the Ultron identity.
- `VERSION_CODENAME` stays `trixie` and `ID_LIKE=debian`, so third-party
  install scripts that ask "which Debian is this?" keep working.
- The apt pin that keeps the image lean exists only during the build and is
  deleted by the last hook. Nothing restricts what users install later.

## The installer

Calamares copies the live system to disk (`unpackfs`) instead of installing
packages one by one, which is why an install takes minutes and needs no
network. The flow is trimmed to six screens. Decisions worth knowing:

- **No pre-selected disk action.** The person must choose *Erase*, *Alongside*
  or *Replace* themselves.
- **One admin account**, no separate root password (like Windows and macOS).
- **No swap partition** by default; zram covers it. A swap file is offered.
- **GRUB for both firmware types.** The image carries `grub-pc-bin` and
  `grub-efi-amd64-bin` plus Debian's signed shim/GRUB, so one ISO installs on
  BIOS and UEFI without a network connection.
- **The EFI boot entry is called `debian`.** Debian's Secure-Boot-signed GRUB
  binary looks for its configuration in `EFI/debian/` and nowhere else. Using
  a different id works with Secure Boot off and drops to a `grub>` prompt with
  it on. Renaming it properly requires Ultron-signed boot binaries, which in
  turn requires getting a shim signed by Microsoft.
- **Encryption is off** in 1.0. The LUKS path needs extra packages in the
  image and a tested unlock flow; shipping it untested would risk people's data.
- After copying, `finalize-install` deletes the installer and live-only files,
  and the `packages` module removes `live-boot`, `live-config` and Calamares.

## Software files

Stock Plasma opens a double-clicked `.deb` in the archive viewer, which is
useless to someone who has never seen a terminal. `ultron-install-file` takes
over the package MIME types:

- `.deb` goes through `apt-get install ./file.deb` (not `dpkg -i`), so
  dependencies resolve. The root half is a small helper started with `pkexec`
  under its own polkit action, which gives a readable password prompt. The
  helper copies the file to a root-owned directory first, so it cannot be
  swapped between the confirmation and the install, and refreshes the package
  lists when they are missing (a fresh install ships without them).
- Flatpak files stay with Discover, which already handles them well.
- AppImages are run, not installed; `libfuse2t64` is shipped because most
  AppImages still need FUSE 2.
- `.run` installers open in a terminal on purpose: they are interactive.
- `.rpm` gets an explanation instead of an `alien` conversion that works
  sometimes and breaks systems the rest of the time.

Discover could have been made the `.deb` handler instead. A dedicated handler
was chosen because its flow is two clicks and a password with a definite
success or failure message, and because it is testable.

There is no "install without asking" mode and there will not be one.

## Windows programs

Wine 10 from Debian is preinstalled, including the 32-bit half (`wine32:i386`
plus 32-bit Mesa), because most installers and nearly all MSI custom actions
are still 32-bit. That costs about 320 MB of ISO size and pushes a release
build past GitHub's 2 GiB release-asset limit, which is why the ISO is offered
as a workflow artifact.

`.exe`/`.msi` are associated with `ultron-run-windows` rather than with Wine
directly, for three reasons: it asks once per file before running something
that has full access to the user's home; it routes `.msi` through `msiexec`;
and it turns Wine's silent failures into a plain-language message that points
to native apps and Bottles. Debian deliberately ships Wine without any file
association; adding one is a convenience-versus-safety trade made on purpose
here, with the prompt as the mitigation.

## Naming

"Ultron" is also the name of a Marvel character, and Marvel holds trademarks on
it. For a personal or hobby project that is unlikely to matter. Before
distributing publicly, charging for it, or registering a domain, check the
trademark situation or pick a name you can own.

The visual style is inspired by macOS but uses no Apple artwork, icons, fonts or
wallpapers.

## Roadmap

1. Test on real hardware (Intel, AMD, an NVIDIA laptop, a 4 GB machine).
2. Package the theme as `.deb` files in a small apt repository so installed
   systems receive theme updates.
3. A purpose-built control-centre popup (media, toggles, sliders) to replace
   the stock system tray popup.
4. Custom Plasma panel SVGs with larger corner radii.
5. Encrypted installs.
6. Light variant of the theme.
