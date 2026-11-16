#!/usr/bin/env bash
# Dump the database to a timestamped file, check it is readable, delete old dumps.
# Usage: DATABASE_URL=postgresql://user:pass@host/db bash scripts/backup.sh [dir]
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set}"
dir="${1:-backups}"
keep_days="${KEEP_DAYS:-14}"

mkdir -p "$dir"
file="$dir/checkin-$(date -u +%Y%m%dT%H%M%SZ).dump"

# Write to a temporary name first so a failed dump never looks like a good one,
# and remove that temporary file however the script exits.
trap 'rm -f "$file.partial"' EXIT
pg_dump --format=custom --no-owner --no-privileges --file="$file.partial" "$DATABASE_URL"
pg_restore --list "$file.partial" > /dev/null
mv "$file.partial" "$file"
echo "backup written: $file ($(du -h "$file" | cut -f1))"

find "$dir" -name 'checkin-*.dump' -mtime +"$keep_days" -print -delete
