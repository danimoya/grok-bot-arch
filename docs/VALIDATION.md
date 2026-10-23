# Validation — updater v0.1.0

Validated on 2026-10-23 on an x86_64 Omarchy machine.

- Full local RPM build: Grok Bot 0.75.3, source SHA-256 `171c38d01377b7da2c3772c2cb1ad0f7fc749c2df4d2253052de9a02e2cfe9a8`. Generated package metadata reports `grok-bot 0.75.3-1`, x86_64.
- Full local DEB build: Grok Bot 0.75.2, source SHA-256 `06ba5ee6432bcbe417be1cb208e863e03988ad9996c39a1ecf2b85633e00505e`. Generated package metadata reports `grok-bot 0.75.2-1`, x86_64.
- Both builds exercised the actual helper's source snapshot, extraction, ASAR metadata inspection, PKGBUILD generation, and makepkg path. The validation harness supplied an older installed-version response (`0.71.2-1`) because 0.75.3 was already installed. Neither validation build performed an install or downgrade.
- Earlier local system upgrade to Grok Bot 0.75.3 completed through pacman; `pacman -Qk grok-bot` reported 177 files and zero missing. This upgrade preceded publication of the reusable helper; it does not independently test the helper's interactive sudo/pkexec handoff.
- Regression suite: 10 tests covering source selection, archive path traversal, symlink extraction escape, shell interpolation rejection, ASAR versions and truncation, persistent counters, fixed redirects, HEAD/preview exclusion, source-label allowlisting, and unavailable public stats endpoints.
- Skill frontmatter validation passed.
- Official release-feed check returned 0.75.3 with RPM and DEB URLs.

Not established by these checks: every Grok Bot GUI feature, clean-machine installation on vanilla Arch, ARM support, or a supported release of the three related Omarchy mods. Their repositories retain their own development status and release checklists.
