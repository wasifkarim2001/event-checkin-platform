#!/usr/bin/env bash
# Restore a dump made by backup.sh, replacing what is in the target database.
# Usage: DATABASE_URL=postgresql://user:pass@host/db bash scripts/restore.sh FILE
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set}"
file="${1:?usage: restore.sh DUMP_FILE}"

# All or nothing: one transaction, stop at the first error.
pg_restore --clean --if-exists --no-owner --no-privileges \
  --single-transaction --exit-on-error --dbname="$DATABASE_URL" "$file"
echo "restored $file"
