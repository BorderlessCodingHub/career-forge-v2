"use client";

import { useEffect, useId, useRef, useState } from "react";

export type SelectOption<T extends string = string> = {
  value: T;
  label: string;
};

type SelectProps<T extends string> = {
  id?: string;
  value: T | "";
  options: SelectOption<T>[];
  placeholder?: string;
  onChange: (value: T | "") => void;
  "data-testid"?: string;
  className?: string;
};

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      aria-hidden
      className={`h-4 w-4 shrink-0 text-text-muted transition-transform ${open ? "rotate-180" : ""}`}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}

export function Select<T extends string>({
  id,
  value,
  options,
  placeholder = "Selecione…",
  onChange,
  "data-testid": testId,
  className = "",
}: SelectProps<T>) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();

  const selectedLabel =
    options.find((option) => option.value === value)?.label ?? placeholder;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectValue = (next: T | "") => {
    onChange(next);
    setOpen(false);
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <button
        type="button"
        id={id}
        data-testid={testId}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listboxId}
        onClick={() => setOpen((current) => !current)}
        className={`flex w-full items-center justify-between rounded-md border border-border bg-surface-elevated px-4 py-3 text-left text-sm outline-none ring-accent focus:ring-2 ${
          value ? "text-text-primary" : "text-text-muted"
        }`}
      >
        <span>{selectedLabel}</span>
        <ChevronIcon open={open} />
      </button>

      {open && (
        <ul
          id={listboxId}
          role="listbox"
          aria-labelledby={id}
          className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border border-border bg-surface-elevated py-1 shadow-lg"
        >
          <li role="presentation">
            <button
              type="button"
              role="option"
              aria-selected={value === ""}
              data-testid={testId ? `${testId}-placeholder` : undefined}
              onClick={() => selectValue("")}
              className={`w-full px-4 py-2.5 text-left text-sm transition hover:bg-accent/10 ${
                value === "" ? "text-accent" : "text-text-muted"
              }`}
            >
              {placeholder}
            </button>
          </li>
          {options.map((option) => (
            <li key={option.value} role="presentation">
              <button
                type="button"
                role="option"
                aria-selected={value === option.value}
                data-testid={testId ? `${testId}-option-${option.value}` : undefined}
                onClick={() => selectValue(option.value)}
                className={`w-full px-4 py-2.5 text-left text-sm transition hover:bg-accent/10 ${
                  value === option.value
                    ? "bg-accent/10 text-accent"
                    : "text-text-primary"
                }`}
              >
                {option.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
