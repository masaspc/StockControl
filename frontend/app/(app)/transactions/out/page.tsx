"use client";

import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

export default function OutPage() {
  const [itemId, setItemId] = useState("");
  const [fromLocationId, setFromLocationId] = useState("");
  const [toLocationId, setToLocationId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [serialItemId, setSerialItemId] = useState("");
  const [workOrderNo, setWorkOrderNo] = useState("");
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    try {
      await api.post("/transactions/out", {
        item_id: Number(itemId),
        from_location_id: Number(fromLocationId),
        to_location_id: toLocationId ? Number(toLocationId) : undefined,
        quantity,
        serial_item_id: serialItemId ? Number(serialItemId) : undefined,
        work_order_no: workOrderNo || undefined,
        note: note || undefined,
      });
      setMsg("出庫を登録しました");
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">出庫処理</h1>
      <Card>
        <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
          <Field label="品目ID" value={itemId} setValue={setItemId} required />
          <Field
            label="出庫元ロケーションID"
            value={fromLocationId}
            setValue={setFromLocationId}
            required
          />
          <Field
            label="持出し先ロケーションID（任意）"
            value={toLocationId}
            setValue={setToLocationId}
          />
          <Field
            label="数量"
            value={String(quantity)}
            setValue={(v) => setQuantity(Number(v))}
            type="number"
          />
          <Field
            label="シリアル品ID（シリアル管理品目）"
            value={serialItemId}
            setValue={setSerialItemId}
          />
          <Field
            label="工事番号"
            value={workOrderNo}
            setValue={setWorkOrderNo}
          />
          <div className="md:col-span-2">
            <Field label="備考" value={note} setValue={setNote} />
          </div>
          <div className="md:col-span-2">
            <button className="rounded bg-brand px-4 py-2 text-white hover:bg-brand-light">
              出庫を登録
            </button>
          </div>
          {msg && (
            <div className="md:col-span-2 rounded bg-green-50 p-3 text-sm text-green-700">
              {msg}
            </div>
          )}
          {err && (
            <div className="md:col-span-2 rounded bg-red-50 p-3 text-sm text-red-700">
              {err}
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}

function Field({
  label,
  value,
  setValue,
  type = "text",
  required,
}: {
  label: string;
  value: string;
  setValue: (v: string) => void;
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
        onChange={(e) => setValue(e.target.value)}
      />
    </label>
  );
}
