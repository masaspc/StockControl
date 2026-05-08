"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Item } from "@/types/api";

export default function ItemDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Partial<Item>>({});
  const [err, setErr] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["item", params.id],
    queryFn: () => api.get<Item>(`/items/${params.id}`),
  });

  const updateMut = useMutation({
    mutationFn: (body: Partial<Item>) => api.put<Item>(`/items/${params.id}`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["item", params.id] });
      qc.invalidateQueries({ queryKey: ["items"] });
      setEditing(false);
    },
    onError: (e: Error) => setErr(e.message),
  });

  function startEdit() {
    if (!data) return;
    setForm({ ...data });
    setErr(null);
    setEditing(true);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    updateMut.mutate(form);
  }

  if (isLoading) return <div>読み込み中...</div>;
  if (error) return <div className="rounded bg-red-50 p-4 text-red-700">{(error as Error).message}</div>;
  if (!data) return null;

  if (editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <button onClick={() => setEditing(false)} className="text-sm text-slate-500 hover:text-slate-700">← 戻る</button>
          <h1 className="text-2xl font-bold">品目編集</h1>
        </div>
        {err && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{err}</div>}
        <Card>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4 text-sm">
            <Field label="品目コード *">
              <input required value={form.code ?? ""}
                onChange={(e) => setForm({ ...form, code: e.target.value })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="品目名 *">
              <input required value={form.name ?? ""}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="カテゴリ">
              <input value={form.category ?? ""}
                onChange={(e) => setForm({ ...form, category: e.target.value || null })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="管理タイプ *">
              <select value={form.manage_type ?? "quantity"}
                onChange={(e) => setForm({ ...form, manage_type: e.target.value as Item["manage_type"] })}
                className="w-full rounded border px-3 py-2">
                <option value="quantity">数量管理</option>
                <option value="serial">シリアル管理</option>
              </select>
            </Field>
            <Field label="メーカー">
              <input value={form.maker ?? ""}
                onChange={(e) => setForm({ ...form, maker: e.target.value || null })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="型番">
              <input value={form.model_no ?? ""}
                onChange={(e) => setForm({ ...form, model_no: e.target.value || null })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="単位 *">
              <input required value={form.unit ?? ""}
                onChange={(e) => setForm({ ...form, unit: e.target.value })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="バーコード">
              <input value={form.barcode ?? ""}
                onChange={(e) => setForm({ ...form, barcode: e.target.value || null })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="発注点">
              <input type="number" min="0" value={form.order_point ?? 0}
                onChange={(e) => setForm({ ...form, order_point: Number(e.target.value) })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="発注単位">
              <input type="number" min="1" value={form.order_unit ?? 1}
                onChange={(e) => setForm({ ...form, order_unit: Number(e.target.value) })}
                className="w-full rounded border px-3 py-2" />
            </Field>
            <Field label="状態">
              <select value={form.is_active ? "true" : "false"}
                onChange={(e) => setForm({ ...form, is_active: e.target.value === "true" })}
                className="w-full rounded border px-3 py-2">
                <option value="true">有効</option>
                <option value="false">無効</option>
              </select>
            </Field>
            <div className="col-span-2 flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setEditing(false)}
                className="rounded border px-4 py-2 text-sm">キャンセル</button>
              <button type="submit"
                className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
                保存
              </button>
            </div>
          </form>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-sm text-slate-500 hover:text-slate-700">← 戻る</button>
          <h1 className="text-2xl font-bold">{data.name}</h1>
        </div>
        <button onClick={startEdit}
          className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
          編集
        </button>
      </div>
      <Card>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <Row label="品目コード">{data.code}</Row>
          <Row label="管理タイプ">{data.manage_type === "serial" ? "シリアル管理" : "数量管理"}</Row>
          <Row label="カテゴリ">{data.category ?? "-"}</Row>
          <Row label="メーカー">{data.maker ?? "-"}</Row>
          <Row label="型番">{data.model_no ?? "-"}</Row>
          <Row label="単位">{data.unit}</Row>
          <Row label="発注点">{data.order_point}</Row>
          <Row label="発注単位">{data.order_unit}</Row>
          <Row label="バーコード">{data.barcode ?? "-"}</Row>
          <Row label="状態">{data.is_active ? "有効" : "無効"}</Row>
        </dl>
      </Card>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <>
      <dt className="text-slate-500">{label}</dt>
      <dd>{children}</dd>
    </>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs text-slate-500">{label}</label>
      <div className="mt-1">{children}</div>
    </div>
  );
}
