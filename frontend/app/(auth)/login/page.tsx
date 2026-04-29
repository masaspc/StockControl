"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [adAccount, setAdAccount] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(adAccount, password);
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm rounded-lg bg-white p-8 shadow"
      >
        <h1 className="mb-1 text-2xl font-bold text-brand">TBN-IMS</h1>
        <p className="mb-6 text-sm text-slate-500">在庫管理システム</p>

        <label className="mb-3 block text-sm">
          <span className="mb-1 block font-medium">ADアカウント</span>
          <input
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
            value={adAccount}
            onChange={(e) => setAdAccount(e.target.value)}
            required
            autoFocus
          />
        </label>

        <label className="mb-4 block text-sm">
          <span className="mb-1 block font-medium">パスワード</span>
          <input
            type="password"
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && (
          <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-brand py-2 text-white hover:bg-brand-light disabled:opacity-50"
        >
          {loading ? "認証中..." : "ログイン"}
        </button>
      </form>
    </div>
  );
}
