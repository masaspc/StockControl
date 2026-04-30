"use client";

export const dynamic = "force-dynamic";

import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { StockDetail } from "@/types/api";

export default function StocksPage() {
  const params = useSearchParams();
  const alertOnly = params.get("alert") === "true";

  const { data, isLoading } = useQuery({
    queryKey: ["stocks", alertOnly],
    queryFn: () =>
      api.get<StockDetail[]>(`/stocks${alertOnly ? "?alert=true" : ""}`),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">
        在庫一覧 {alertOnly && <span className="text-red-600">(アラートのみ)</span>}
      </h1>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">品目コード</th>
                <th>品目名</th>
                <th>ロケーション</th>
                <th className="text-right">数量</th>
                <th className="text-right">発注点</th>
                <th>状態</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="py-2 font-mono">{s.item_code}</td>
                  <td>{s.item_name}</td>
                  <td>{s.location_name}</td>
                  <td className="text-right">{s.quantity}</td>
                  <td className="text-right">{s.order_point ?? "-"}</td>
                  <td>
                    {s.is_alert ? (
                      <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">
                        要発注
                      </span>
                    ) : (
                      <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">
                        正常
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {data && data.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500">
                    在庫データはありません。
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
