"use client";

import { useCallback, useRef, useState } from "react";

import type { CvAttachment } from "@/lib/onboarding-session";

const ACCEPTED_TYPES = ["application/pdf"];
const ACCEPTED_EXTENSIONS = [".pdf"];
const MAX_BYTES = 5 * 1024 * 1024;

type CvDropzoneProps = {
  attachment: CvAttachment | null;
  onAttach: (attachment: CvAttachment) => void;
  onRemove: () => void;
};

function isAcceptedFile(file: File): boolean {
  const lower = file.name.toLowerCase();
  return (
    ACCEPTED_TYPES.includes(file.type) ||
    ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext))
  );
}

function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      if (typeof result !== "string") {
        reject(new Error("Failed to read file."));
        return;
      }
      const base64 = result.split(",")[1];
      if (!base64) {
        reject(new Error("Failed to encode file."));
        return;
      }
      resolve(base64);
    };
    reader.onerror = () => reject(new Error("Failed to read file."));
    reader.readAsDataURL(file);
  });
}

export function CvDropzone({ attachment, onAttach, onRemove }: CvDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      if (!isAcceptedFile(file)) {
        setError("Unsupported format. Use PDF.");
        return;
      }
      if (file.size > MAX_BYTES) {
        setError("File too large. Maximum 5 MB.");
        return;
      }

      setBusy(true);
      try {
        const dataBase64 = await readFileAsBase64(file);
        const mimeType =
          file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
            ? "application/pdf"
            : file.type;
        onAttach({
          filename: file.name,
          size: file.size,
          mimeType,
          dataBase64,
        });
      } catch {
        setError("Could not attach the resume.");
      } finally {
        setBusy(false);
      }
    },
    [onAttach],
  );

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragOver(false);
      const file = event.dataTransfer.files[0];
      if (file) void handleFile(file);
    },
    [handleFile],
  );

  if (attachment) {
    return (
      <div
        className="mt-2 flex items-center justify-between rounded-md border border-border bg-surface-elevated px-4 py-3"
        data-testid="cv-attachment"
      >
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-text-primary">
            {attachment.filename}
          </p>
          <p className="text-xs text-text-muted">
            {(attachment.size / 1024).toFixed(0)} KB · attached (not analyzed yet)
          </p>
        </div>
        <button
          type="button"
          data-testid="cv-remove"
          onClick={onRemove}
          className="ml-3 shrink-0 text-sm text-text-muted hover:text-warning"
        >
          Remove
        </button>
      </div>
    );
  }

  return (
    <div className="mt-2">
      <div
        role="button"
        tabIndex={0}
        data-testid="cv-dropzone"
        onDragOver={(event) => {
          event.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-md border border-dashed px-4 py-8 text-center transition ${
          dragOver
            ? "border-accent bg-accent/5"
            : "border-border bg-surface-elevated hover:border-accent/40"
        } ${busy ? "pointer-events-none opacity-60" : ""}`}
      >
        <p className="text-sm font-medium text-text-primary">
          Drop your resume here
        </p>
        <p className="mt-1 text-xs text-text-muted">
          or click to choose · PDF · up to 5 MB
        </p>
        <p className="mt-2 text-[11px] text-text-muted">
          Optional — we'll use it to personalize your trail soon
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        data-testid="cv-file-input"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleFile(file);
          event.target.value = "";
        }}
      />
      {error && (
        <p className="mt-2 text-sm text-warning" data-testid="cv-error">
          {error}
        </p>
      )}
    </div>
  );
}
