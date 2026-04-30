"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Transaction } from "@/types/api";

export default function HistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["history"],
    queryFn: () => api.get<Transaction[]>("/history"),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">履歴照会</h1>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">日時</th>
                <th>種別</th>
                <th>品目ID</th>
                <th>シリアル</th>
                <th className="text-right">数量</th>
                <th>From</th>
                <th>To</th>
                <th>担当</th>
                <th>工事番号</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((t) => (
                <tr key={t.id} className="border-t">
                  <td className="py-2">{new Date(t.created_at).toLocaleString("ja-JP")}</td>
                  <td>{t.tx_type}</td>
                  <td>{t.item_id}</td>
                  <td>{t.serial_item_id ?? "-"}</td>
                  <td className="text-right">{t.quantity}</td>
                  <td>{t.from_location_id ?? "-"}</td>
                  <td>{t.to_location_id ?? "-"}</td>
                  <td>{t.operator_id}</td>
                  <td>{t.work_order_no ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        )}
      </Card>
    </div>
  );
}
