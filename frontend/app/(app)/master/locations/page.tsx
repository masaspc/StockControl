"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Location, LocationTreeNode } from "@/types/api";

const LOC_TYPES = ["site", "area", "shelf", "vehicle", "person", "customer"] as const;
const LOC_LABELS: Record<string, string> = {
  site: "拠点", area: "エリア", shelf: "棚", vehicle: "車両", person: "個人", customer: "顧客",
};

interface Form { code: string; name: string; loc_type: string; parent_id: string; }
const EMPTY: Form = { code: "", name: "", loc_type: "shelf", parent_id: "" };

export default function LocationsPage() {
  const qc = useQueryClient();
  const [modal, setModal] = useState<"create" | "edit" | null>(null);
  const [editing, setEditing] = useState<Location | null>(null);
  const [form, setForm] = useState<Form>(EMPTY);
  const [err, setErr] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["locations"],
    queryFn: () => api.get<LocationTreeNode[]>("/locations"),
  });

  const createMut = useMutation({
    mutationFn: (body: object) => api.post<Location>("/locations", body),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["locations"] }); setModal(null); },
    onError: (e: Error) => setErr(e.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, body }: { id: number; body: object }) =>
      api.put<Location>(`/locations/${id}`, body),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["locations"] }); setModal(null); },
    onError: (e: Error) => setErr(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.delete<void>(`/locations/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["locations"] }),
  });

  function openCreate() {
    setForm(EMPTY); setEditing(null); setErr(null); setModal("create");
  }
  function openEdit(loc: Location) {
    setForm({ code: loc.code, name: loc.name, loc_type: loc.loc_type, parent_id: String(loc.parent_id ?? "") });
    setEditing(loc); setErr(null); setModal("edit");
  }
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const body = { ...form, parent_id: form.parent_id ? Number(form.parent_id) : null };
    if (modal === "create") createMut.mutate(body);
    else if (editing) updateMut.mutate({ id: editing.id, body });
  }

  const allLocs: Location[] = [];
  function flatten(nodes: LocationTreeNode[]) {
    for (const n of nodes) { allLocs.push(n); flatten(n.children); }
  }
  flatten(data ?? []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">ロケーション管理</h1>
        <button onClick={openCreate}
          className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
          + 新規追加
        </button>
      </div>
      <Card>
        {isLoading ? <div>読み込み中...</div> : (
          <ul className="text-sm">
            {(data ?? []).map((node) => (
              <TreeRow key={node.id} node={node} depth={0}
                onEdit={openEdit}
                onDelete={(id) => { if (confirm("削除しますか？")) deleteMut.mutate(id); }} />
            ))}
            {data?.length === 0 && (
              <li className="py-8 text-center text-slate-500">ロケーションがありません</li>
            )}
          </ul>
        )}
      </Card>

      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold">
              {modal === "create" ? "ロケーション追加" : "ロケーション編集"}
            </h2>
            {err && <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{err}</div>}
            <form onSubmit={handleSubmit} className="space-y-3">
              <label className="block text-xs text-slate-500">コード *
                <input required value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                  className="mt-1 block w-full rounded border px-3 py-2 text-sm font-normal" />
              </label>
              <label className="block text-xs text-slate-500">名称 *
                <input required value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="mt-1 block w-full rounded border px-3 py-2 text-sm font-normal" />
              </label>
              <label className="block text-xs text-slate-500">種別 *
                <select value={form.loc_type}
                  onChange={(e) => setForm({ ...form, loc_type: e.target.value })}
                  className="mt-1 block w-full rounded border px-3 py-2 text-sm font-normal">
                  {LOC_TYPES.map((t) => <option key={t} value={t}>{LOC_LABELS[t]}</option>)}
                </select>
              </label>
              <label className="block text-xs text-slate-500">親ロケーション
                <select value={form.parent_id}
                  onChange={(e) => setForm({ ...form, parent_id: e.target.value })}
                  className="mt-1 block w-full rounded border px-3 py-2 text-sm font-normal">
                  <option value="">なし</option>
                  {allLocs
                    .filter((l) => !editing || l.id !== editing.id)
                    .map((l) => (
                      <option key={l.id} value={l.id}>{l.code} — {l.name}</option>
                    ))}
                </select>
              </label>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setModal(null)}
                  className="rounded border px-4 py-2 text-sm">キャンセル</button>
                <button type="submit"
                  className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
                  {modal === "create" ? "追加" : "更新"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function TreeRow({ node, depth, onEdit, onDelete }: {
  node: LocationTreeNode;
  depth: number;
  onEdit: (loc: Location) => void;
  onDelete: (id: number) => void;
}) {
  const LOC_LABELS: Record<string, string> = {
    site: "拠点", area: "エリア", shelf: "棚", vehicle: "車両", person: "個人", customer: "顧客",
  };
  return (
    <li>
      <div className="flex items-center gap-2 border-b py-2" style={{ paddingLeft: depth * 20 }}>
        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs">
          {LOC_LABELS[node.loc_type] ?? node.loc_type}
        </span>
        <span className="font-mono text-slate-500">{node.code}</span>
        <span className="flex-1 font-medium">{node.name}</span>
        <button onClick={() => onEdit(node)}
          className="rounded px-2 py-1 text-xs text-brand hover:bg-brand/10">編集</button>
        <button onClick={() => onDelete(node.id)}
          className="rounded px-2 py-1 text-xs text-red-600 hover:bg-red-50">削除</button>
      </div>
      {node.children.length > 0 && (
        <ul>
          {node.children.map((c) => (
            <TreeRow key={c.id} node={c} depth={depth + 1} onEdit={onEdit} onDelete={onDelete} />
          ))}
        </ul>
      )}
    </li>
  );
}
