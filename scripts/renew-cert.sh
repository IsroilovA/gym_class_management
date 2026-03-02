#!/usr/bin/env bash
# -------------------------------------------------------------------
# Renew Let's Encrypt certificates for this stack.
# Usage:
#   ./scripts/renew-cert.sh
#   ./scripts/renew-cert.sh --dry-run
# -------------------------------------------------------------------
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.prod}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml)
DATA_PATH="./certbot"
DRY_RUN=0

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--dry-run]" >&2
  exit 1
fi

CERTBOT_ARGS=(renew)
if [[ "$DRY_RUN" == "1" ]]; then
  CERTBOT_ARGS+=(--dry-run)
else
  CERTBOT_ARGS+=(--quiet)
fi

# Stop nginx so certbot standalone can bind port 80 for renewal.
echo ">>> Stopping nginx for renewal..."
"${COMPOSE[@]}" stop nginx

echo ">>> Running certbot ${CERTBOT_ARGS[*]}"
docker run --rm -p 80:80 \
  -v "$(pwd)/$DATA_PATH/conf:/etc/letsencrypt" \
  certbot/certbot "${CERTBOT_ARGS[@]}"

echo ">>> Starting nginx back up..."
"${COMPOSE[@]}" start nginx

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Renewal check complete"
