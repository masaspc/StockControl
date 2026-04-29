"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  onScan: (text: string) => void;
  onError?: (e: Error) => void;
}

export function BarcodeScanner({ onScan, onError }: Props) {
  const containerId = "tbn-ims-scanner";
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);
  const [manual, setManual] = useState("");

  useEffect(() => {
    if (!active) return;
    let scanner: { stop: () => Promise<void>; clear: () => void } | null = null;
    let cancelled = false;

    (async () => {
      try {
        const { Html5Qrcode } = await import("html5-qrcode");
        const instance = new Html5Qrcode(containerId);
        scanner = instance as unknown as typeof scanner;
        await instance.start(
          { facingMode: "environment" },
          { fps: 10, qrbox: { width: 250, height: 150 } },
          (decoded: string) => {
            if (cancelled) return;
            navigator.vibrate?.(100);
            onScan(decoded);
          },
          undefined,
        );
      } catch (e) {
        if (!cancelled) {
          onError?.(e instanceof Error ? e : new Error(String(e)));
          setActive(false);
        }
      }
    })();

    return () => {
      cancelled = true;
      scanner?.stop().catch(() => {});
      scanner?.clear?.();
    };
  }, [active, onScan, onError]);

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setActive((v) => !v)}
          className="rounded bg-brand px-3 py-1 text-sm text-white hover:bg-brand-light"
        >
          {active ? "スキャン停止" : "カメラでスキャン"}
        </button>
        <input
          className="flex-1 rounded border border-slate-300 px-3 py-1 text-sm"
          placeholder="または手動入力"
          value={manual}
          onChange={(e) => setManual(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && manual) {
              onScan(manual);
              setManual("");
            }
          }}
        />
      </div>
      {active && (
        <div
          id={containerId}
          ref={ref}
          className="overflow-hidden rounded border bg-black"
          style={{ minHeight: 240 }}
        />
      )}
    </div>
  );
}
