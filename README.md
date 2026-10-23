# Grok Bot for Arch

Build an Arch Linux package from an official Grok Bot download, then upgrade through pacman. Tested on Omarchy, x86_64.

[Get started](https://tools.danimoya.com/grok-bot/) · [Download the updater](https://github.com/danimoya/grok-bot-arch/releases/latest) · [Report an issue](https://github.com/danimoya/grok-bot-arch/issues)

```text
Official RPM / DEB → inspect app version → makepkg → local Arch package → pacman
```

This community tool packages the upstream desktop app. It is independently maintained by [Daniel Moya](https://github.com/danimoya), with no affiliation or endorsement from Omarchy, Arch Linux, Cursor, or xAI. The MIT license covers this tool; Grok Bot retains its upstream license and subscription requirements.

## Quick start

Install build prerequisites on an up-to-date Arch system:

```bash
sudo pacman -S --needed base-devel libarchive python git
```

Clone and inspect the source:

```bash
git clone https://github.com/danimoya/grok-bot-arch.git
cd grok-bot-arch
less bin/grok-bot-update
```

Download the **Linux x64 RPM or DEB** from the [official download page](https://cursor.com/download/bot). Then build and install:

```bash
python3 bin/grok-bot-update --install
```

The default chooses the newest completed `grok-bot*.rpm` or `.deb` in `~/Downloads` by modification time. To choose a specific download:

```bash
python3 bin/grok-bot-update ~/Downloads/grok-bot-0.75.3-1.x86_64.rpm --install
```

Run as your normal user. Only the final pacman operation requests administrator access and transaction confirmation. Restart Grok Bot after upgrading.

## Options

| Command | Result |
| --- | --- |
| `python3 bin/grok-bot-update` | Build from the latest local download; no installation |
| `python3 bin/grok-bot-update --install` | Build, then offer installation through pacman |
| `python3 bin/grok-bot-update --check` | Read the official current-version feed; no app download or installation |
| `python3 bin/grok-bot-update FILE --output ~/my-build` | Save build output to a fresh directory |

Output defaults to `~/Downloads/grok-bot-arch/VERSION/`: the Arch package, generated PKGBUILD, and build-info.json containing the source filename, SHA-256, and tool version. Existing outputs are preserved; choose a fresh `--output` directory for another build.

## What gets checked

The updater reads the version from the application's bundled ASAR metadata, checks the x86_64 ELF header, rejects unsafe archive paths, and refuses an input version equal to or older than the installed package. It snapshots and hashes the input, then uses makepkg without stripping upstream binaries. RPM build-id links and foreign package-manager configuration are excluded; the app, desktop entry, and icons are retained.

Only use downloads you trust from upstream. The recorded SHA-256 identifies your build input; it is not independent publisher authentication. No Grok Bot binaries are distributed in this repository or its releases. The updater does not enable an automatic Arch repository: rerun it with a newer upstream download when you want to update. The upstream release feed is [documented here](https://docs.x.ai/grok-bot/deployment).

## Codex skill

The included [skill](skills/grok-bot-update/SKILL.md) describes this workflow for a coding agent. Keep the repository clone available, then install the skill:

```bash
mkdir -p ~/.codex/skills/grok-bot-update
cp skills/grok-bot-update/SKILL.md ~/.codex/skills/grok-bot-update/SKILL.md
```

Ask your agent to use `grok-bot-update` to upgrade from your chosen download. The skill also works as readable instructions for other agents; discovery conventions differ by agent.

## Verification and removal

```bash
pacman -Q grok-bot
pacman -Qk grok-bot
sudo pacman -R grok-bot
```

Removal leaves personal app data in your home directory. Remove the copied skill directory separately if you no longer want the agent instructions.

Validated locally with upstream RPM 0.75.3 and DEB 0.75.2. Packaging checks do not establish that every Grok Bot feature works on every desktop. See [validation details](docs/VALIDATION.md).

Run the regression suite with `python3 -m unittest discover -s tests -v`. Contributions with reproducible failures, distro details, and upstream versions are welcome. Please exclude tokens, account data, and private logs from reports.

## More Omarchy projects by Daniel Moya

- [Google Drive integration](https://github.com/danimoya/omarchy-google-drive) — integration work for your Omarchy desktop.
- [Animated screensaver](https://github.com/danimoya/omarchy-animated-screensaver) — animation for your desktop's idle moments.
- [Monitor mirror](https://github.com/danimoya/omarchy-monitor-mirror) — monitor mirroring for Omarchy.

Each project has its own release status and setup instructions. If this updater helps, a GitHub star makes it easier for others to discover, and a useful issue helps improve it.
