"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { API_BASE } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Order } from "@/types/api";

export default function OrdersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => api.get<Order[]>("/orders"),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">発注管理</h1>
        <Link
          href="/orders/new"
          className="rounded bg-brand px-3 py-2 text-sm text-white hover:bg-brand-light"
        >
          + 発注書作成
        </Link>
      </div>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">発注番号</th>
                <th>品目ID</th>
                <th>仕入先ID</th>
                <th className="text-right">数量</th>
                <th>ステータス</th>
                <th>納期</th>
                <th>PDF</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((o) => (
                <tr key={o.id} className="border-t">
                  <td className="py-2 font-mono">{o.order_no}</td>
                  <td>{o.item_id}</td>
                  <td>{o.supplier_id ?? "-"}</td>
                  <td className="text-right">{o.quantity}</td>
                  <td>{o.status}</td>
                  <td>{o.expected_at ?? "-"}</td>
                  <td>
                    <a
                      href={`${API_BASE}/orders/${o.id}/pdf`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-brand hover:underline"
                    >
                      ダウンロード
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table></div>
        )}
      </Card>
    </div>
  );
}
