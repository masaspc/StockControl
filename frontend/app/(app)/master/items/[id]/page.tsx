"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Item } from "@/types/api";

export default function ItemDetailPage({ params }: { params: { id: string } }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["item", params.id],
    queryFn: () => api.get<Item>(`/items/${params.id}`),
  });

  if (isLoading) return <div>読み込み中...</div>;
  if (error)
    return <div className="rounded bg-red-50 p-4 text-red-700">{(error as Error).message}</div>;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{data.name}</h1>
      <Card>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <Row label="品目コード">{data.code}</Row>
          <Row label="管理タイプ">{data.manage_type}</Row>
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
