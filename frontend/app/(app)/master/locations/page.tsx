"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { LocationTreeNode } from "@/types/api";

export default function LocationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["locations"],
    queryFn: () => api.get<LocationTreeNode[]>("/locations"),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">ロケーション管理</h1>
      <Card>
        {isLoading ? (
          <div>読み込み中...</div>
        ) : (
          <ul className="text-sm">
            {(data ?? []).map((node) => (
              <TreeNode key={node.id} node={node} depth={0} />
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function TreeNode({ node, depth }: { node: LocationTreeNode; depth: number }) {
  return (
    <li>
      <div
        className="flex items-center gap-2 border-b py-2"
        style={{ paddingLeft: depth * 20 }}
      >
        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs">{node.loc_type}</span>
        <span className="font-mono text-slate-500">{node.code}</span>
        <span className="font-medium">{node.name}</span>
      </div>
      {node.children.length > 0 && (
        <ul>
          {node.children.map((c) => (
            <TreeNode key={c.id} node={c} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}
