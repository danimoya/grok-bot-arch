---
name: grok-bot-update
description: Build and optionally install an Arch Linux package from a local official Grok Bot RPM or DEB, including updates from Downloads on Omarchy.
---

# Update Grok Bot on Arch

Use the repository's `bin/grok-bot-update` helper as a normal user. Locate the repository from the current workspace or ask for its location if unavailable; do not assume the helper is bundled beside an independently copied skill.

- Read `pacman -Qi grok-bot` and inspect completed `grok-bot*.rpm` or `.deb` downloads. Honor the user's chosen file or download date. Exclude `.part` files and previously repacked Arch packages.
- Run `python3 bin/grok-bot-update /absolute/path/to/download.rpm` to build only. With no path, it selects the newest completed RPM or DEB by modification time in `~/Downloads`.
- The helper snapshots the input, rejects unsafe archive paths, reads the version from the bundled ASAR, verifies x86_64 ELF architecture, refuses an equal or older version, hashes the source, builds with makepkg, and saves the Arch package, PKGBUILD, and build-info.json under `~/Downloads/grok-bot-arch/VERSION/`. An existing output requires a fresh `--output` directory.
- When the user requests installation or upgrade, add `--install`. Only the pacman step uses sudo/pkexec. Observe the execution environment's approval rules; do not bypass failed authentication.
- Use `--check` only when current upstream release information is needed. It reads the official release feed and does not download or install anything.
- After installation, confirm `pacman -Q grok-bot` and `pacman -Qk grok-bot`. Tell the user to restart the app. Do not terminate active sessions or claim GUI verification unless performed.

The helper supports stable x86_64 builds only. Use official downloads from https://cursor.com/download/bot. The locally computed SHA-256 records input consistency; it is not independent publisher authentication. Preserve the original download and user data, Chromium sandbox settings, upstream desktop integration, and the privilege boundary around pacman. See the repository README for prerequisites and removal.
