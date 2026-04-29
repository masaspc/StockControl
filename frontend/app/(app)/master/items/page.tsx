"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Item } from "@/types/api";

export default function ItemsPage() {
  const [q, setQ] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["items", q],
    queryFn: () =>
      api.get<Item[]>(`/items${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">品目マスタ</h1>
        <Link
          href="/master/items/new"
          className="rounded bg-brand px-3 py-2 text-sm text-white hover:bg-brand-light"
        >
          + 新規登録
        </Link>
      </div>

      <Card>
        <input
          className="mb-4 w-full max-w-md rounded border px-3 py-2 text-sm"
          placeholder="検索（品目コード・名称・バーコード）"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">コード</th>
                <th>名称</th>
                <th>カテゴリ</th>
                <th>管理</th>
                <th className="text-right">発注点</th>
                <th>状態</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((it) => (
                <tr key={it.id} className="border-t">
                  <td className="py-2 font-mono">
                    <Link href={`/master/items/${it.id}`} className="text-brand hover:underline">
                      {it.code}
                    </Link>
                  </td>
                  <td>{it.name}</td>
                  <td>{it.category ?? "-"}</td>
                  <td>{it.manage_type === "serial" ? "シリアル" : "数量"}</td>
                  <td className="text-right">
                    {it.order_point} {it.unit}
                  </td>
                  <td>{it.is_active ? "有効" : "無効"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
