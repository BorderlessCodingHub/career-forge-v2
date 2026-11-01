import {
  getCountries,
  getCountryCallingCode,
  parsePhoneNumberFromString,
  type CountryCode,
} from "libphonenumber-js";

export const DEFAULT_PHONE_COUNTRY: CountryCode = "BR";

export type PhoneCountry = {
  code: CountryCode;
  label: string;
};

export function phoneCountries(locale: string): PhoneCountry[] {
  const names = new Intl.DisplayNames([locale], { type: "region" });
  return getCountries()
    .map((code) => ({
      code,
      label: `${names.of(code) ?? code} +${getCountryCallingCode(code)}`,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, locale));
}

/** Blank is nothing. A national number is E.164 for the selected country, or invalid. */
export function signupPhone(
  country: CountryCode,
  national: string,
): { ok: true; e164: string | null } | { ok: false } {
  const compact = national.replace(/[\s\-()]/g, "");
  if (compact === "") return { ok: true, e164: null };
  const parsed = parsePhoneNumberFromString(compact, country);
  if (!parsed?.isValid() || parsed.country !== country) return { ok: false };
  return { ok: true, e164: parsed.number };
}
