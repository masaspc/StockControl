"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Order } from "@/types/api";

export default function NewOrderPage() {
  const router = useRouter();
  const [itemId, setItemId] = useState("");
  const [supplierId, setSupplierId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [expectedAt, setExpectedAt] = useState("");
  const [note, setNote] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const created = await api.post<Order>("/orders", {
        item_id: Number(itemId),
        supplier_id: supplierId ? Number(supplierId) : undefined,
        quantity,
        expected_at: expectedAt || undefined,
        note: note || undefined,
      });
      router.push(`/orders`);
      router.refresh();
      void created;
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">発注書作成</h1>
      <Card>
        <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
          <F label="品目ID *" value={itemId} setValue={setItemId} required />
          <F label="仕入先ID" value={supplierId} setValue={setSupplierId} />
          <F
            label="数量 *"
            value={String(quantity)}
            setValue={(v) => setQuantity(Number(v))}
            type="number"
            required
          />
          <F label="希望納期" value={expectedAt} setValue={setExpectedAt} type="date" />
          <div className="md:col-span-2">
            <F label="備考" value={note} setValue={setNote} />
          </div>
          <div className="md:col-span-2">
            <button className="rounded bg-brand px-4 py-2 text-white hover:bg-brand-light">
              発注を申請
            </button>
          </div>
          {err && (
            <div className="md:col-span-2 rounded bg-red-50 p-3 text-sm text-red-700">{err}</div>
          )}
        </form>
      </Card>
    </div>
  );
}

function F({
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
        className="w-full rounded border px-3 py-2"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </label>
  );
}
