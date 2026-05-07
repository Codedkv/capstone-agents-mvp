"use client";
import { useState } from "react";
import { validateKey, type ValidateKeyResult } from "@/lib/api";

export type KeyStatus =
  | "idle"
  | "validating"
  | "valid"
  | "invalid"
  | "rate_limited"
  | "error";

export interface KeyInputProps {
  status: KeyStatus;
  onChange: (key: string, status: KeyStatus, message?: string) => void;
}

export function KeyInput({ status, onChange }: KeyInputProps) {
  const [value, setValue] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const handleTest = async () => {
    if (!value || value.length < 30) {
      setMessage("Key looks too short — Gemini keys are ~39 characters.");
      onChange(value, "invalid");
      return;
    }
    setMessage(null);
    onChange(value, "validating");
    try {
      const res: ValidateKeyResult = await validateKey(value);
      if (res.valid) {
        onChange(value, "valid");
        setMessage(null);
      } else if (res.reason === "rate_limited") {
        onChange(value, "rate_limited", "Key works but is rate-limited. You can still try.");
        setMessage("Key valid but currently rate-limited. Try later.");
      } else if (res.reason === "invalid_key") {
        onChange(value, "invalid", "Google rejected this key.");
        setMessage("Google rejected this key as invalid.");
      } else {
        onChange(value, "error", res.detail || res.reason);
        setMessage(`Validation failed: ${res.reason}${res.detail ? ` — ${res.detail}` : ""}`);
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      onChange(value, "error", msg);
      setMessage(`Network error: ${msg}`);
    }
  };

  const indicator = (() => {
    switch (status) {
      case "valid":
        return <span className="text-[var(--success)]">✓ valid</span>;
      case "invalid":
        return <span className="text-[var(--error)]">✗ invalid</span>;
      case "rate_limited":
        return <span style={{ color: "var(--accent)" }}>⚠ rate-limited</span>;
      case "validating":
        return <span className="text-[var(--muted)]">checking…</span>;
      case "error":
        return <span className="text-[var(--error)]">error</span>;
      default:
        return null;
    }
  })();

  return (
    <div className="card p-5">
      <div className="flex items-baseline justify-between mb-3">
        <span className="label-mono">step 1 · gemini api key</span>
        {indicator}
      </div>
      <div className="flex gap-2 items-stretch">
        <input
          type="password"
          autoComplete="off"
          spellCheck={false}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            if (status !== "idle") onChange(e.target.value, "idle");
            setMessage(null);
          }}
          placeholder="AIza…"
          className="flex-1 px-3 py-2 rounded-lg bg-[var(--surface-2)] border border-[var(--border-strong)] focus:border-[var(--accent)] focus:outline-none font-mono text-sm"
        />
        <button
          type="button"
          onClick={handleTest}
          disabled={status === "validating" || !value}
          className="btn-ghost"
        >
          {status === "validating" ? "Testing…" : "Test connection"}
        </button>
      </div>
      <p className="mt-3 text-[13px] text-[var(--muted)] leading-relaxed">
        Get a free key at{" "}
        <a
          href="https://aistudio.google.com/app/apikey"
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-[var(--foreground)]"
        >
          aistudio.google.com/app/apikey
        </a>
        . Your key is sent to our backend only for the duration of the run, never stored.
      </p>
      {message && (
        <p className="mt-2 text-[13px]" style={{ color: status === "valid" ? "var(--success)" : "var(--error)" }}>
          {message}
        </p>
      )}
    </div>
  );
}
