"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Item } from "@/types/api";

export default function NewItemPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    code: "",
    name: "",
    category: "",
    maker: "",
    model_no: "",
    manage_type: "quantity" as "quantity" | "serial",
    unit: "個",
    order_point: 0,
    order_unit: 1,
    barcode: "",
  });
  const [err, setErr] = useState<string | null>(null);

  function update<K extends keyof typeof form>(k: K, v: (typeof form)[K]) {
    setForm({ ...form, [k]: v });
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const payload = { ...form };
      Object.keys(payload).forEach((k) => {
        const key = k as keyof typeof payload;
        if (payload[key] === "") {
          // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
          delete (payload as Record<string, unknown>)[key];
        }
      });
      const created = await api.post<Item>("/items", payload);
      router.push(`/master/items/${created.id}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">品目 新規登録</h1>
      <Card>
        <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
          <Field label="品目コード *" value={form.code} onChange={(v) => update("code", v)} required />
          <Field label="名称 *" value={form.name} onChange={(v) => update("name", v)} required />
          <Field label="カテゴリ" value={form.category} onChange={(v) => update("category", v)} />
          <Field label="メーカー" value={form.maker} onChange={(v) => update("maker", v)} />
          <Field label="型番" value={form.model_no} onChange={(v) => update("model_no", v)} />
          <label className="block text-sm">
            <span className="mb-1 block font-medium">管理タイプ *</span>
            <select
              className="w-full rounded border px-3 py-2"
              value={form.manage_type}
              onChange={(e) =>
                update("manage_type", e.target.value as "serial" | "quantity")
              }
            >
              <option value="quantity">数量管理</option>
              <option value="serial">シリアル管理</option>
            </select>
          </label>
          <Field label="単位" value={form.unit} onChange={(v) => update("unit", v)} />
          <Field
            label="発注点"
            type="number"
            value={String(form.order_point)}
            onChange={(v) => update("order_point", Number(v))}
          />
          <Field
            label="発注単位"
            type="number"
            value={String(form.order_unit)}
            onChange={(v) => update("order_unit", Number(v))}
          />
          <Field label="バーコード" value={form.barcode} onChange={(v) => update("barcode", v)} />
          <div className="md:col-span-2">
            <button className="rounded bg-brand px-4 py-2 text-white hover:bg-brand-light">
              登録
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

function Field({
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
        className="w-full rounded border px-3 py-2"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
