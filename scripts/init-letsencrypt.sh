#!/usr/bin/env bash
# -------------------------------------------------------------------
# Issue/expand Let's Encrypt certificate(s) using certbot standalone.
# Run BEFORE starting the production stack for the first time.
# - Idempotent: safe to re-run.
# - Stops nginx if running (port 80 must be free for certbot).
# -------------------------------------------------------------------
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.prod}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"
CERTBOT_DOMAINS="${CERTBOT_DOMAINS:-17102gymclasses.app,www.17102gymclasses.app}"
CERTBOT_STAGING="${CERTBOT_STAGING:-0}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml)
DATA_PATH="./certbot"

if [[ -z "$CERTBOT_EMAIL" ]]; then
  echo "ERROR: CERTBOT_EMAIL is required (set it in $ENV_FILE)." >&2
  exit 1
fi

DOMAINS_CLEAN="${CERTBOT_DOMAINS// /}"
IFS=',' read -r -a DOMAINS <<< "$DOMAINS_CLEAN"
if [[ ${#DOMAINS[@]} -eq 0 || -z "${DOMAINS[0]}" ]]; then
  echo "ERROR: CERTBOT_DOMAINS must include at least one domain." >&2
  exit 1
fi
PRIMARY_DOMAIN="${DOMAINS[0]}"

mkdir -p "$DATA_PATH/conf"

DOMAIN_ARGS=()
for domain in "${DOMAINS[@]}"; do
  if [[ -n "$domain" ]]; then
    DOMAIN_ARGS+=( -d "$domain" )
  fi
done

STAGING_ARGS=()
if [[ "$CERTBOT_STAGING" == "1" ]]; then
  STAGING_ARGS+=( --staging )
fi

# Stop nginx if running — certbot standalone needs port 80.
echo ">>> Stopping nginx (if running) so certbot can bind port 80..."
"${COMPOSE[@]}" stop nginx 2>/dev/null || true

echo ">>> Requesting/expanding certificate '$PRIMARY_DOMAIN' for: ${DOMAINS[*]}"
docker run --rm -p 80:80 \
  -v "$(pwd)/$DATA_PATH/conf:/etc/letsencrypt" \
  certbot/certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$CERTBOT_EMAIL" \
    --cert-name "$PRIMARY_DOMAIN" \
    --keep-until-expiring \
    --expand \
    "${STAGING_ARGS[@]}" \
    "${DOMAIN_ARGS[@]}"

echo ">>> Certificate issued. Start the full stack with:"
echo "    ${COMPOSE[*]} up -d --build"
echo ""
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] init-letsencrypt complete"
