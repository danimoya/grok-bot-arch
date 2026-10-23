# Tools hub operations

The hub serves static assets through a small Python server behind Nginx Proxy Manager. The homepage lists the four public projects; `/grok-bot/` contains the updater walkthrough. `site/server.py` maps fixed download slugs to GitHub URLs, preventing user-supplied redirect destinations.

## Private download records

Download-link GET requests increment SQLite aggregates by UTC date, project, and an allowlisted source label. No visitor identifiers, IP addresses, or cookies are stored in this database. HEAD requests and recognized bot/preview user agents do not increment counts. Bots can evade detection and repeated clicks count again; these are request counts, not unique visitors, completed downloads, or installs.

The SQLite directory is bind-mounted outside the public document root and persists across container replacement. There is no HTTP statistics endpoint. Access reports through the operator's authenticated SSH session:

```bash
ssh dm26 'docker exec grok-bot-tools python3 /app/server.py stats'
ssh dm26 'docker exec grok-bot-tools python3 /app/server.py export' > downloads.csv
```

Campaign examples: `https://tools.danimoya.com/?source=reddit` and `https://tools.danimoya.com/grok-bot/?source=linkedin`. Source labels are propagated to download links by the page script. Labels are coarse, caller supplied, and not independent proof of origin.

For a consistent database backup, use the CLI's SQLite backup operation:

```bash
ssh dm26 'docker exec grok-bot-tools python3 /app/server.py backup --output /data/downloads-backup.sqlite3'
```

Copy that file to your private backup storage. Keep reports and backups out of public repositories. Reverse-proxy logging is separate from the application's private aggregate database.

## Deployment

`site/compose.yaml` runs an unprivileged Python container on the existing external `management-network`; it publishes no direct host port. Its read-only source/document-root mounts are separate from the writable private data mount. Adapt the compose UID/GID to the hosting account before deployment.

Prepare this layout beside compose.yaml:

```text
server.py
compose.yaml
data/                    # owned by the service UID, mode 0700
public/
  index.html             # site/hub.html
  hub.css
  hub.js
  grok-bot/
    index.html           # site/index.html
    style.css
    nerd.css
    app.js
    social.png
```

Point a dedicated NPM host for `tools.danimoya.com` to `http://grok-bot-tools:8080`, obtain its TLS certificate, and force HTTPS. Existing hosts do not need changes. Start with `docker compose up -d`; inspect `docker compose ps`, `/healthz`, the homepage, detail page, and download HEAD responses. A release must exist at the fixed updater download URL before announcing it.

To update, replace only application/public files, preserve `data/`, and restart the container. Export/backup the counter before deployment. To remove the website, disable its dedicated proxy host and stop its compose service; retain the data directory for records.

