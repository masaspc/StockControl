"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, StatCard } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { DashboardData } from "@/types/api";

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardData>("/dashboard"),
  });

  if (isLoading) return <div>読み込み中...</div>;
  if (error)
    return (
      <div className="rounded bg-red-50 p-4 text-red-700">
        ダッシュボード取得失敗: {(error as Error).message}
      </div>
    );
  if (!data) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">ダッシュボード</h1>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="登録品目数" value={data.total_items} />
        <StatCard label="ロケーション数" value={data.total_locations} />
        <StatCard label="シリアル品 総数" value={data.total_serials} />
        <StatCard label="アラート品目" value={data.alert_count} />
        <StatCard label="未完了発注" value={data.pending_orders} />
        <StatCard label="本日の入庫" value={data.today_in} />
        <StatCard label="本日の出庫" value={data.today_out} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title={`発注点アラート (${data.alerts.length})`}>
          {data.alerts.length === 0 ? (
            <div className="text-sm text-slate-500">アラートはありません。</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-slate-500">
                <tr>
                  <th className="py-1">品目コード</th>
                  <th>品目名</th>
                  <th className="text-right">在庫</th>
                  <th className="text-right">発注点</th>
                </tr>
              </thead>
              <tbody>
                {data.alerts.map((a) => (
                  <tr key={a.item_id} className="border-t">
                    <td className="py-1 font-mono">{a.item_code}</td>
                    <td>{a.item_name}</td>
                    <td className="text-right text-red-600">
                      {a.current_qty} {a.unit}
                    </td>
                    <td className="text-right">
                      {a.order_point} {a.unit}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>

        <Card title="最新トランザクション">
          {data.recent_transactions.length === 0 ? (
            <div className="text-sm text-slate-500">取引履歴はありません。</div>
          ) : (
            <ul className="divide-y text-sm">
              {data.recent_transactions.map((t) => (
                <li key={t.id} className="flex items-center justify-between py-2">
                  <div>
                    <span className="mr-2 rounded bg-slate-100 px-2 py-0.5 text-xs">
                      {t.tx_type}
                    </span>
                    <span>{t.item_name}</span>
                    <span className="ml-2 text-slate-500">×{t.quantity}</span>
                  </div>
                  <div className="text-xs text-slate-500">
                    {t.operator_name ?? "-"} /{" "}
                    {new Date(t.created_at).toLocaleString("ja-JP")}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
