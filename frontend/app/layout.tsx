import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "TBN-IMS 在庫管理システム",
  description: "Tokyo Bay Network Inventory Management System",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
