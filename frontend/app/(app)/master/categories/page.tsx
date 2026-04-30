"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Item } from "@/types/api";

export default function CategoriesPage() {
  const qc = useQueryClient();
  const [renameModal, setRenameModal] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const { data: items, isLoading } = useQuery({
    queryKey: ["items", "all"],
    queryFn: () => api.get<Item[]>("/items?active=true"),
  });

  const categories: { name: string; count: number }[] = [];
  if (items) {
    const map = new Map<string, number>();
    for (const item of items) {
      const cat = item.category ?? "（未分類）";
      map.set(cat, (map.get(cat) ?? 0) + 1);
    }
    for (const [name, count] of map.entries()) {
      categories.push({ name, count });
    }
    categories.sort((a, b) => a.name.localeCompare(b.name, "ja"));
  }

  const renameMut = useMutation({
    mutationFn: async ({ from, to }: { from: string; to: string }) => {
      const targets = (items ?? []).filter((i) => (i.category ?? "（未分類）") === from);
      await Promise.all(
        targets.map((i) =>
          api.put<Item>(`/items/${i.id}`, { category: to === "（未分類）" ? null : to })
        )
      );
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["items"] });
      setRenameModal(null);
    },
    onError: (e: Error) => setErr(e.message),
  });

  function openRename(cat: string) {
    setNewName(cat === "（未分類）" ? "" : cat);
    setErr(null);
    setRenameModal(cat);
  }

  function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (!renameModal) return;
    renameMut.mutate({ from: renameModal, to: newName || "（未分類）" });
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">カテゴリ管理</h1>
      <p className="text-sm text-slate-500">
        カテゴリは品目マスタの「カテゴリ」フィールドで管理されます。
        品目を追加・編集する際にカテゴリを設定してください。
      </p>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-slate-500">
              <tr>
                <th className="py-2">カテゴリ名</th>
                <th className="text-right">品目数</th>
                <th className="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.name} className="border-t">
                  <td className="py-2 font-medium">{cat.name}</td>
                  <td className="text-right">
                    <Link
                      href={`/master/items?category=${encodeURIComponent(cat.name === "（未分類）" ? "" : cat.name)}`}
                      className="text-brand hover:underline"
                    >
                      {cat.count} 件
                    </Link>
                  </td>
                  <td className="text-right">
                    <button
                      onClick={() => openRename(cat.name)}
                      className="rounded px-2 py-1 text-xs text-brand hover:bg-brand/10"
                    >
                      名称変更
                    </button>
                  </td>
                </tr>
              ))}
              {categories.length === 0 && (
                <tr>
                  <td colSpan={3} className="py-8 text-center text-slate-500">
                    カテゴリがありません。
                    <Link href="/master/items/new" className="ml-1 text-brand hover:underline">
                      品目を追加
                    </Link>
                    してカテゴリを設定してください。
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </Card>

      {renameModal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold">カテゴリ名称変更</h2>
            <p className="mb-3 text-sm text-slate-500">
              「{renameModal}」に属する全品目のカテゴリを変更します。
            </p>
            {err && <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{err}</div>}
            <form onSubmit={handleRename} className="space-y-3">
              <label className="block text-xs text-slate-500">新しいカテゴリ名
                <input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="空白にすると未分類になります"
                  className="mt-1 block w-full rounded border px-3 py-2 text-sm font-normal"
                />
              </label>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setRenameModal(null)}
                  className="rounded border px-4 py-2 text-sm">キャンセル</button>
                <button type="submit"
                  className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
                  変更
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
