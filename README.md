# Arris Modem Scraper (TG2482A)

Lightweight scraper to capture status and event tables from an ARRIS TG2482A
modem and store them as CSV for later analysis.

## What It Captures

- Status:
  - Downstream
  - Upstream
- Events:
  - DOCSIS
  - MTA

Each run adds a `Timestamp_Extraccion` to preserve history.

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`

## Configuration

Edit `config/config.yaml`:

```yaml
PULL_INTERVAL: 600
STATUS_URL: "http://192.168.100.1/cgi-bin/status_cgi"
EVENT_URL: "http://192.168.100.1/cgi-bin/event_cgi"
OUTPUT_DIR: "./data"
```

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python arris_status_scraper.py
```

CSV files are saved to `./data/`.

## Docker

### Build

```bash
docker build -t arris-status-scraper .
```

### Run

```bash
docker run --rm \
  -v "$(pwd)/config:/app/config" \
  -v "$(pwd)/data:/app/data" \
  arris-status-scraper
```

## Docker Compose

Example using `BASE_DIR` for mounts:

```bash
BASE_DIR=/path/to/base docker compose up -d --build
```

The `docker-compose.yml` already includes these bind mounts:

- `${BASE_DIR}/config:/app/config`
- `${BASE_DIR}/data:/app/data`

## Notes

- If the modem HTML changes, the table order may change.
- Events are deduplicated ignoring `Timestamp_Extraccion`.
