# TBN-IMS 在庫管理システム — プロジェクト仕様書

> **Claude Code 用プロジェクトコンテキストファイル**
> このファイルはClaude Codeが常時参照するプロジェクト仕様です。
> 実装・修正・追加作業の前に必ず本ファイルを確認してください。

---

## 0. 基本情報

| 項目 | 内容 |
|---|---|
| システム名 | TBN-IMS（Tokyo Bay Network Inventory Management System） |
| 発注元 | 東京ベイネットワーク株式会社 総務部システム課 |
| 本番URL | `https://www.mszapps.com/` |
| ホスティング | ConoHa VPS（Ubuntu 24.04 LTS） |
| リポジトリ | GitHub（プライベート） |
| 版数 | v2.0（2026/04/29） |

---

## 1. 技術スタック

### インフラ

```
ConoHa VPS
├── Ubuntu 24.04 LTS
└── Docker Compose
    ├── tbn-ims-proxy   Nginx 1.26-alpine   ポート 80/443（SSL終端）
    ├── tbn-ims-web     Node.js 20-alpine    ポート 3000（Next.js）
    ├── tbn-ims-api     Python 3.12-slim     ポート 8000（FastAPI）
    └── tbn-ims-db      PostgreSQL 16-alpine ポート 5432（内部のみ）
```

### フロントエンド

- Next.js 14（App Router）
- TypeScript 5.x / Tailwind CSS 3.x
- Html5-QRCode（バーコードスキャン）
- TanStack React Query 5.x / Zustand 4.x

### バックエンド

- Python 3.12 / FastAPI 0.111.x
- SQLAlchemy 2.0 / Alembic 1.13
- Pydantic 2.x / python-jose / ldap3 / aiosmtplib / ReportLab 4.x

### データベース

- PostgreSQL 16
- Alembic マイグレーション管理
- pg_dump 日次バックアップ（cron + ConoHa オブジェクトストレージ・7世代）

### SSL / Web

- Nginx リバースプロキシ + SSL終端
- Let's Encrypt（Certbot）自動更新

---

## 2. ディレクトリ構造

```
tbn-ims/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── CLAUDE.md
│
├── frontend/          # Next.js アプリ
├── backend/           # FastAPI アプリ
├── nginx/             # Nginx 設定
└── scripts/           # 運用スクリプト
```

詳細はリポジトリのディレクトリツリーを参照。

---

## 3. 環境変数

`.env.example` をコピーして `.env` を作成。シークレットは絶対に Git にコミットしない。

主要キー:

- `APP_ENV` / `APP_URL` / `SECRET_KEY` / `ACCESS_TOKEN_EXPIRE_MINUTES`
- `POSTGRES_*`
- `LDAP_SERVER` / `LDAP_BASE_DN` / `LDAP_BIND_DN` / `LDAP_BIND_PASSWORD`
- `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM`
- `CONOHA_OS_*`

---

## 4. データベース設計

主要テーブル:

- `items` 品目マスタ（serial / quantity 管理タイプ）
- `locations` ロケーション（自己参照階層、site/area/shelf/vehicle/person/customer）
- `stocks` 数量在庫
- `serial_items` シリアル在庫（status: in_stock / checked_out / disposed / lost）
- `transactions` 入出庫ログ（in / out / return / transfer / adjust）
- `orders` 発注（PO-YYMM-NNN 採番）
- `suppliers` 仕入先
- `users` ユーザー（AD連携、role: admin / manager / operator / viewer）
- `alert_settings` 発注点アラート設定

詳細SQL定義は `backend/alembic/versions/0001_initial.py` を参照。

---

## 5. API エンドポイント

ベースURL: `https://www.mszapps.com/api/v1`

主要グループ:

- `auth` ログイン / リフレッシュ / ログアウト / me
- `items` 品目マスタ CRUD
- `stocks` 在庫照会・サマリ・アラート
- `serials` シリアル管理・履歴
- `transactions` 入庫 / 出庫 / 返却 / 移動 / 履歴
- `locations` ロケーション CRUD（ツリー）
- `orders` 発注（承認 / 完了 / PDF出力）
- `stocktake` 棚卸セッション
- `users` / `suppliers` / `dashboard`

OpenAPI: `https://www.mszapps.com/api/docs` (開発環境のみ)

---

## 6. 認証・権限

| ロール | 主な権限 |
|---|---|
| `admin` | 全機能・ユーザー管理・発注承認 |
| `manager` | 入出庫・発注申請・棚卸・マスタ編集 |
| `operator` | 出庫・返却・自分の持出し在庫確認 |
| `viewer` | 在庫照会のみ |

認証フロー: AD/LDAP バインド → DB から role 取得 → JWT 発行 → HttpOnly Cookie 保存。
有効期限 480 分（8時間）、リフレッシュトークンで延長。

---

## 7. 画面一覧

| ID | パス | 画面名 | 最小ロール |
|---|---|---|---|
| SCR-001 | `/login` | ログイン | - |
| SCR-002 | `/dashboard` | ダッシュボード | viewer |
| SCR-003 | `/master/items` | 品目マスタ | manager |
| SCR-004 | `/master/items/[id]` | 品目詳細 | manager |
| SCR-005 | `/master/locations` | ロケーション管理 | admin |
| SCR-006 | `/stocks` | 在庫一覧 | viewer |
| SCR-007 | `/serials` | シリアル検索 | operator |
| SCR-008 | `/transactions/in` | 入庫処理 | manager |
| SCR-009 | `/transactions/out` | 出庫処理 | operator |
| SCR-010 | `/transactions/return` | 返却処理 | operator |
| SCR-011 | `/orders` | 発注管理 | manager |
| SCR-012 | `/orders/new` | 発注書作成 | manager |
| SCR-013 | `/stocktake` | 棚卸 | manager |
| SCR-014 | `/history` | 履歴照会 | manager |
| SCR-015 | `/settings/users` | ユーザー管理 | admin |
| SCR-016 | `/settings` | システム設定 | admin |

---

## 8. バーコードスキャン

`html5-qrcode` でブラウザカメラAPI完結。JAN(1D) / QR(2D) 対応。
PCでは手動入力にフォールバック。スキャン成功時にバイブ・ビープ。

---

## 9. メール通知

`aiosmtplib` 非同期送信。Jinja2 テンプレート（HTML/テキスト）。
発注点割れ検知タイミング: 出庫・返却・棚卸調整コミット後。FastAPI `BackgroundTasks` で非同期送信。
再通知は在庫回復後に再度下回った場合のみ。

---

## 10. PDF生成

ReportLab 4.x + IPAexゴシック（Dockerイメージに同梱）。`StreamingResponse` でクライアントに返却。

---

## 11. デプロイ

```bash
# 初回
git clone ...
cp .env.example .env  # 編集
sudo certbot certonly --standalone -d www.mszapps.com -d mszapps.com
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker exec tbn-ims-api alembic upgrade head
docker exec tbn-ims-api python scripts/create_admin.py

# 通常デプロイ
./scripts/deploy.sh
```

バックアップ: `/etc/cron.d/tbn-ims-backup` で日次 02:00。

---

## 12. コーディング規約

- Python: Ruff フォーマット、型ヒント必須、`async def` + `AsyncSession`
- TypeScript: Prettier + ESLint、`any` 禁止、関数コンポーネント、サーバーコンポーネント優先
- コミット: `feat:` / `fix:` / `chore:` / `docs:` プレフィックス
- 環境変数はコード直書き禁止

---

## 13. 注意事項・既知の制約

- PostgreSQL は外部ポート非公開
- LDAP パスワード月次変更で翌日再ログインが必要
- iOS Safari カメラスキャンは iOS 16 以上
- IPAexゴシック フォントは Docker イメージ同梱
- 既存 EIP（C# ASP.NET MVC）と完全独立、SQL Server 影響なし
- SMTPリレー設定変更時は `SMTP_*` 環境変数のみ修正

---

*最終更新: 2026年4月29日 / 東京ベイネットワーク株式会社 総務部システム課*
