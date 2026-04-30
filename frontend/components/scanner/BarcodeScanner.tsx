"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  onScan: (text: string) => void;
}

export function BarcodeScanner({ onScan }: Props) {
  const containerId = "tbn-ims-scanner";
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);
  const [cameraErr, setCameraErr] = useState<string | null>(null);
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
      } catch {
        if (!cancelled) {
          setCameraErr("カメラが利用できません。手動入力をご利用ください。");
          setActive(false);
        }
      }
    })();

    return () => {
      cancelled = true;
      scanner?.stop().catch(() => {});
      scanner?.clear?.();
    };
  }, [active, onScan]);

  function handleToggle() {
    setCameraErr(null);
    setActive((v) => !v);
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleToggle}
          className="rounded bg-brand px-3 py-2 text-sm text-white hover:bg-brand-light"
        >
          {active ? "スキャン停止" : "カメラでスキャン"}
        </button>
        <input
          className="min-w-0 flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
          placeholder="バーコードを手動入力 → Enter"
          value={manual}
          onChange={(e) => setManual(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && manual.trim()) {
              onScan(manual.trim());
              setManual("");
            }
          }}
        />
      </div>
      {cameraErr && (
        <p className="rounded bg-amber-50 px-3 py-2 text-xs text-amber-700">{cameraErr}</p>
      )}
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
