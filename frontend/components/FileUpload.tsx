"use client";
import { useRef, useState } from "react";

const ALLOWED_EXTS = [".csv", ".xlsx", ".xls", ".json"];
const MAX_BYTES = 50 * 1024 * 1024;

export interface FileUploadProps {
  disabled: boolean;
  selected: File | null;
  onSelect: (file: File | null, error?: string) => void;
}

export function FileUpload({ disabled, selected, onSelect }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file: File | undefined | null) => {
    if (!file) return;
    const ext = file.name.includes(".")
      ? file.name.slice(file.name.lastIndexOf(".")).toLowerCase()
      : "";
    if (!ALLOWED_EXTS.includes(ext)) {
      onSelect(null, `Unsupported file type: ${ext || "(none)"}. Allowed: ${ALLOWED_EXTS.join(", ")}`);
      return;
    }
    if (file.size > MAX_BYTES) {
      onSelect(null, `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB (max 50MB)`);
      return;
    }
    onSelect(file);
  };

  return (
    <div className="card p-5">
      <div className="flex items-baseline justify-between mb-3">
        <span className="label-mono">step 2 · upload data</span>
        {selected && (
          <span className="text-[var(--success)] text-[13px]">
            ✓ {selected.name} · {(selected.size / 1024).toFixed(1)} KB
          </span>
        )}
      </div>
      <div
        className="dropzone p-8 text-center cursor-pointer"
        data-dragging={dragging}
        data-disabled={disabled}
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (disabled) return;
          handleFile(e.dataTransfer.files?.[0]);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={ALLOWED_EXTS.join(",")}
          disabled={disabled}
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <p className="text-base">
          {dragging ? "Release to upload" : "Drop CSV / XLSX / JSON here"}
        </p>
        <p className="mt-2 text-[13px] text-[var(--muted)]">
          or click to browse · max 50 MB
        </p>
      </div>
    </div>
  );
}
