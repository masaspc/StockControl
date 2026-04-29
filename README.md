# TBN-IMS — 在庫管理システム

東京ベイネットワーク株式会社向けの在庫管理システム。Next.js + FastAPI + PostgreSQL on Docker。

本番URL: https://www.mszapps.com/

仕様の詳細は [`CLAUDE.md`](./CLAUDE.md) を参照。

## クイックスタート（開発環境）

```bash
# 1. 環境変数ファイルを作成
cp .env.example .env
# SECRET_KEY や POSTGRES_PASSWORD などを編集

# 2. コンテナ起動
docker compose up -d --build

# 3. DB マイグレーション
docker exec tbn-ims-api alembic upgrade head

# 4. 初期管理者ユーザーを作成
docker exec -it tbn-ims-api python scripts/create_admin.py

# 5. ブラウザでアクセス
# Web:  http://localhost
# API:  http://localhost/api/docs
```

## 本番デプロイ

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker exec tbn-ims-api alembic upgrade head
```

詳細は `scripts/deploy.sh` 参照。

## ディレクトリ構成

```
tbn-ims/
├── frontend/   Next.js 14 (App Router)
├── backend/    FastAPI 0.111
├── nginx/      Nginx + SSL
└── scripts/    バックアップ・デプロイ
```
