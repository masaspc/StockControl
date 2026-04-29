"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

interface User {
  id: number;
  ad_account: string;
  display_name: string;
  email: string | null;
  role: string;
  is_active: boolean;
  last_login: string | null;
}

export default function UsersPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: () => api.get<User[]>("/users"),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">ユーザー管理</h1>
      <Card>
        {error && (
          <div className="rounded bg-red-50 p-3 text-sm text-red-700">
            {(error as Error).message}
          </div>
        )}
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">ADアカウント</th>
                <th>表示名</th>
                <th>メール</th>
                <th>ロール</th>
                <th>状態</th>
                <th>最終ログイン</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="py-2 font-mono">{u.ad_account}</td>
                  <td>{u.display_name}</td>
                  <td>{u.email ?? "-"}</td>
                  <td>{u.role}</td>
                  <td>{u.is_active ? "有効" : "無効"}</td>
                  <td>
                    {u.last_login
                      ? new Date(u.last_login).toLocaleString("ja-JP")
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
