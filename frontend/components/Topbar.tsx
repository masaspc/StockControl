"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { fetchMe, logout } from "@/lib/auth";

export function Topbar() {
  const router = useRouter();
  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
  });

  async function onLogout() {
    await logout();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="flex h-14 items-center justify-between border-b bg-white px-6">
      <div className="text-sm text-slate-500">在庫管理システム v2.0</div>
      <div className="flex items-center gap-4 text-sm">
        {me ? (
          <>
            <span className="text-slate-700">
              {me.display_name}
              <span className="ml-2 rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                {me.role}
              </span>
            </span>
            <button
              onClick={onLogout}
              className="rounded border px-3 py-1 hover:bg-slate-50"
            >
              ログアウト
            </button>
          </>
        ) : (
          <a href="/login" className="text-brand hover:underline">
            ログイン
          </a>
        )}
      </div>
    </header>
  );
}
