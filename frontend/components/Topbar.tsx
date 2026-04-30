"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { fetchMe, logout } from "@/lib/auth";

interface Props {
  onMenuClick?: () => void;
}

export function Topbar({ onMenuClick }: Props) {
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
    <header className="flex h-14 shrink-0 items-center justify-between border-b bg-white px-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded p-2 hover:bg-slate-100 md:hidden"
          aria-label="メニュー"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="text-sm text-slate-500 hidden sm:block">在庫管理システム v2.0</span>
      </div>
      <div className="flex items-center gap-2 text-sm">
        {me ? (
          <>
            <span className="hidden sm:block text-slate-700">{me.display_name}</span>
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              {me.role}
            </span>
            <button
              onClick={onLogout}
              className="rounded border px-3 py-1 text-sm hover:bg-slate-50"
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
