"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

interface Session {
  id: number;
  name: string;
  status: string;
  started_at: string;
  closed_at: string | null;
}

export default function StocktakePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["stocktake"],
    queryFn: () => api.get<Session[]>("/stocktake"),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">棚卸</h1>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">ID</th>
                <th>名称</th>
                <th>ステータス</th>
                <th>開始</th>
                <th>終了</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="py-2">{s.id}</td>
                  <td>{s.name}</td>
                  <td>{s.status}</td>
                  <td>{new Date(s.started_at).toLocaleString("ja-JP")}</td>
                  <td>{s.closed_at ? new Date(s.closed_at).toLocaleString("ja-JP") : "-"}</td>
                </tr>
              ))}
              {data && data.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-slate-500">
                    棚卸セッションはありません。
                  </td>
                </tr>
              )}
            </tbody>
          </table></div>
        )}
      </Card>
    </div>
  );
}
