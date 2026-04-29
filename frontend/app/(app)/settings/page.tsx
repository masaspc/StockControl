import { Card } from "@/components/ui/Card";

export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">システム設定</h1>
      <Card title="システム情報">
        <dl className="grid grid-cols-2 gap-2 text-sm">
          <dt className="text-slate-500">バージョン</dt>
          <dd>v2.0</dd>
          <dt className="text-slate-500">本番URL</dt>
          <dd>https://www.mszapps.com</dd>
        </dl>
      </Card>
      <Card title="関連リンク">
        <ul className="list-disc pl-5 text-sm">
          <li>
            <a className="text-brand hover:underline" href="/api/docs" target="_blank" rel="noreferrer">
              APIドキュメント (開発環境のみ)
            </a>
          </li>
          <li>
            <a className="text-brand hover:underline" href="/settings/users">
              ユーザー管理
            </a>
          </li>
        </ul>
      </Card>
    </div>
  );
}
