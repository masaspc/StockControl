"use client";

import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

export default function ReturnPage() {
  const [itemId, setItemId] = useState("");
  const [toLocationId, setToLocationId] = useState("");
  const [serialItemId, setSerialItemId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    try {
      await api.post("/transactions/return", {
        item_id: Number(itemId),
        to_location_id: Number(toLocationId),
        serial_item_id: serialItemId ? Number(serialItemId) : undefined,
        quantity,
        note: note || undefined,
      });
      setMsg("返却を登録しました");
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">返却処理</h1>
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <L label="品目ID">
              <input
                required
                className="w-full rounded border px-3 py-2"
                value={itemId}
                onChange={(e) => setItemId(e.target.value)}
              />
            </L>
            <L label="返却先ロケーションID">
              <input
                required
                className="w-full rounded border px-3 py-2"
                value={toLocationId}
                onChange={(e) => setToLocationId(e.target.value)}
              />
            </L>
            <L label="シリアル品ID（シリアル管理品目）">
              <input
                className="w-full rounded border px-3 py-2"
                value={serialItemId}
                onChange={(e) => setSerialItemId(e.target.value)}
              />
            </L>
            <L label="数量">
              <input
                type="number"
                className="w-full rounded border px-3 py-2"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
              />
            </L>
          </div>
          <L label="備考">
            <input
              className="w-full rounded border px-3 py-2"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </L>
          <button className="rounded bg-brand px-4 py-2 text-white hover:bg-brand-light">
            返却を登録
          </button>
          {msg && <div className="rounded bg-green-50 p-3 text-sm text-green-700">{msg}</div>}
          {err && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{err}</div>}
        </form>
      </Card>
    </div>
  );
}

function L({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium">{label}</span>
      {children}
    </label>
  );
}
