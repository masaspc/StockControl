#!/usr/bin/env bash
# TBN-IMS データベース日次バックアップ
# cron: 0 2 * * * root /opt/tbn-ims/scripts/backup.sh >> /var/log/tbn-ims-backup.log 2>&1

set -euo pipefail

cd "$(dirname "$0")/.."

# .env から環境変数を読み込み
if [[ -f .env ]]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs -d '\n')
fi

BACKUP_DIR="${BACKUP_DIR:-/opt/tbn-ims/backups}"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
DUMP_FILE="$BACKUP_DIR/tbn_ims_${TIMESTAMP}.sql.gz"

echo "[$(date -u +%FT%TZ)] Starting backup -> $DUMP_FILE"

docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" tbn-ims-db \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --clean --if-exists \
    | gzip -9 > "$DUMP_FILE"

echo "[$(date -u +%FT%TZ)] Backup completed: $(du -h "$DUMP_FILE" | cut -f1)"

# 7 世代保持
find "$BACKUP_DIR" -maxdepth 1 -name 'tbn_ims_*.sql.gz' -type f -printf '%T@ %p\n' \
    | sort -n | head -n -7 | awk '{print $2}' | xargs -r rm -f

# ConoHa オブジェクトストレージへアップロード（任意）
if [[ -n "${CONOHA_OS_ENDPOINT:-}" && -n "${CONOHA_OS_USERNAME:-}" && -n "${CONOHA_OS_CONTAINER:-}" ]]; then
    echo "[$(date -u +%FT%TZ)] Uploading to object storage..."
    # ここに swift / curl コマンドで実装。詳細はConoHaのドキュメント参照
    # 例: swift upload "$CONOHA_OS_CONTAINER" "$DUMP_FILE"
fi

echo "[$(date -u +%FT%TZ)] Done."
