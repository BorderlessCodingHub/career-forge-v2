"use client";

import type { CountryCode } from "libphonenumber-js";
import { useLocale } from "next-intl";
import { useId, useMemo, useState } from "react";

import { phoneCountries } from "@/lib/phone";

type PhoneFieldProps = {
  country: CountryCode;
  national: string;
  label: string;
  disabled: boolean;
  onCountry: (country: CountryCode) => void;
  onNational: (value: string) => void;
};

export function PhoneField({
  country,
  national,
  label,
  disabled,
  onCountry,
  onNational,
}: PhoneFieldProps) {
  const locale = useLocale();
  const labelId = useId();
  const listId = useId();
  const countries = useMemo(() => phoneCountries(locale), [locale]);
  const selected = countries.find((option) => option.code === country) ?? countries[0];
  const [query, setQuery] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const needle = (query ?? "").trim().toLowerCase();
  const matches = needle
    ? countries.filter((option) => option.label.toLowerCase().includes(needle))
    : countries;

  function choose(code: CountryCode) {
    onCountry(code);
    setQuery(null);
    setOpen(false);
  }

  return (
    <div className="space-y-1">
      <span id={labelId} className="text-sm text-text-secondary">
        {label}
      </span>
      <div className="relative">
        <input
          type="text"
          role="combobox"
          aria-labelledby={labelId}
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          autoComplete="off"
          className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
          value={query ?? selected?.label ?? ""}
          disabled={disabled}
          data-testid="identity-gate-career-forge-phone-country"
          onFocus={() => {
            setQuery("");
            setOpen(true);
          }}
          onBlur={() => {
            setQuery(null);
            setOpen(false);
          }}
          onChange={(event) => {
            setQuery(event.target.value);
            setOpen(true);
          }}
        />
        {open ? (
          <ul
            id={listId}
            role="listbox"
            data-testid="identity-gate-career-forge-phone-countries"
            className="absolute z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-md border border-border bg-surface"
          >
            {matches.map((option) => (
              <li key={option.code} role="presentation">
                <button
                  type="button"
                  role="option"
                  aria-selected={option.code === country}
                  className="block w-full px-3 py-2 text-left text-sm text-text-primary hover:bg-bg"
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => choose(option.code)}
                >
                  {option.label}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
      <input
        type="tel"
        aria-labelledby={labelId}
        autoComplete="tel-national"
        inputMode="tel"
        className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
        value={national}
        disabled={disabled}
        data-testid="identity-gate-career-forge-phone"
        onChange={(event) => onNational(event.target.value)}
      />
    </div>
  );
}
