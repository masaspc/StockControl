"use client";

import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

export default function InPage() {
  const [itemId, setItemId] = useState("");
  const [toLocationId, setToLocationId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [serialNos, setSerialNos] = useState("");
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    try {
      const serials = serialNos
        .split(/[\s,]+/)
        .map((s) => s.trim())
        .filter(Boolean);
      await api.post("/transactions/in", {
        item_id: Number(itemId),
        to_location_id: Number(toLocationId),
        quantity,
        serial_nos: serials.length ? serials : undefined,
        note: note || undefined,
      });
      setMsg("入庫を登録しました");
      setSerialNos("");
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">入庫処理</h1>
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Input label="品目ID" value={itemId} onChange={setItemId} required />
            <Input
              label="入庫先ロケーションID"
              value={toLocationId}
              onChange={setToLocationId}
              required
            />
            <Input
              label="数量（数量管理品目）"
              type="number"
              value={String(quantity)}
              onChange={(v) => setQuantity(Number(v))}
            />
          </div>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">
              シリアル番号 (改行/カンマ区切り、シリアル管理品目用)
            </span>
            <textarea
              className="w-full rounded border border-slate-300 px-3 py-2"
              rows={4}
              value={serialNos}
              onChange={(e) => setSerialNos(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">備考</span>
            <input
              className="w-full rounded border border-slate-300 px-3 py-2"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </label>
          <button className="rounded bg-brand px-4 py-2 text-white hover:bg-brand-light">
            入庫を登録
          </button>
          {msg && <div className="rounded bg-green-50 p-3 text-sm text-green-700">{msg}</div>}
          {err && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{err}</div>}
        </form>
      </Card>
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
  type = "text",
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium">{label}</span>
      <input
        type={type}
        required={required}
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
