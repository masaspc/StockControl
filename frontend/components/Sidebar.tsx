"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/dashboard", label: "ダッシュボード" },
  { href: "/stocks", label: "在庫一覧" },
  { href: "/serials", label: "シリアル検索" },
  { href: "/transactions/in", label: "入庫" },
  { href: "/transactions/out", label: "出庫" },
  { href: "/transactions/return", label: "返却" },
  { href: "/orders", label: "発注管理" },
  { href: "/stocktake", label: "棚卸" },
  { href: "/history", label: "履歴" },
  { href: "/master/items", label: "品目マスタ" },
  { href: "/master/categories", label: "カテゴリ管理" },
  { href: "/master/locations", label: "ロケーション" },
  { href: "/settings/users", label: "ユーザー管理" },
  { href: "/settings", label: "設定" },
];

interface Props {
  onClose?: () => void;
}

export function Sidebar({ onClose }: Props) {
  const pathname = usePathname();
  return (
    <aside className="flex h-full w-56 shrink-0 flex-col bg-brand-dark text-white">
      <div className="flex h-14 items-center justify-between border-b border-white/10 px-4 font-bold">
        <span>TBN-IMS</span>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded p-1 hover:bg-white/10 md:hidden"
            aria-label="メニューを閉じる"
          >
            ✕
          </button>
        )}
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        {NAV.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={
                "block rounded px-3 py-2 text-sm transition " +
                (active ? "bg-brand-light font-semibold" : "hover:bg-white/10")
              }
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
