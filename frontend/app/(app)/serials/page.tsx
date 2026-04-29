"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { BarcodeScanner } from "@/components/scanner/BarcodeScanner";
import { api } from "@/lib/api";
import type { SerialItem } from "@/types/api";

export default function SerialsPage() {
  const [results, setResults] = useState<SerialItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function search(q: string) {
    setError(null);
    try {
      const r = await api.get<SerialItem[]>(
        `/serials/search?q=${encodeURIComponent(q)}`,
      );
      setResults(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">シリアル検索</h1>

      <Card title="シリアル番号 / MACアドレスで検索">
        <BarcodeScanner onScan={search} />
      </Card>

      {error && (
        <div className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <Card>
        <table className="w-full text-sm">
          <thead className="text-left text-slate-500">
            <tr>
              <th className="py-2">シリアル番号</th>
              <th>MAC</th>
              <th>ステータス</th>
              <th>状態</th>
              <th>ロケーションID</th>
            </tr>
          </thead>
          <tbody>
            {results.map((s) => (
              <tr key={s.id} className="border-t">
                <td className="py-2 font-mono">{s.serial_no}</td>
                <td className="font-mono">{s.mac_address ?? "-"}</td>
                <td>{s.status}</td>
                <td>{s.condition}</td>
                <td>{s.location_id ?? "-"}</td>
              </tr>
            ))}
            {results.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-slate-500">
                  検索してください
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
