#!/usr/bin/env bash
# TBN-IMS 本番デプロイスクリプト

set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> git pull"
git pull origin main

echo "==> docker compose build & up"
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "==> alembic upgrade head"
docker exec tbn-ims-api alembic upgrade head

echo "==> health check"
sleep 3
curl -fsS http://localhost/api/health || {
    echo "Health check failed"
    exit 1
}

echo "==> Deploy completed."
