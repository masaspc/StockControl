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
  { href: "/master/locations", label: "ロケーション" },
  { href: "/settings/users", label: "ユーザー管理" },
  { href: "/settings", label: "設定" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-56 shrink-0 bg-brand-dark text-white">
      <div className="flex h-14 items-center justify-center border-b border-white/10 font-bold">
        TBN-IMS
      </div>
      <nav className="p-2">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={
                "block rounded px-3 py-2 text-sm transition " +
                (active
                  ? "bg-brand-light font-semibold"
                  : "hover:bg-white/10")
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
