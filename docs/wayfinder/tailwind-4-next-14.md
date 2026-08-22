# CAR-49 — Tailwind CSS 4.1 on Next.js 14.2

**Question:** Can `apps/frontend` (Next 14.2, React 18, Tailwind 3.4.17, PostCSS + autoprefixer, CAR-34 `tailwind.config.ts`) move to Tailwind CSS 4.1 **without** a Next.js major upgrade?

**Snapshot (origin/main):** `next@^14.2.35`, `react@^18.3.1`, `tailwindcss@^3.4.17`, `postcss@^8.5.3`, `autoprefixer@^10.4.21`, `postcss.config.mjs` with `tailwindcss` + `autoprefixer`, `globals.css` with `@tailwind base/components/utilities` then `:root` brand tokens. No `@apply` in `apps/frontend`. Layout uses `next/font/google` (Inter + JetBrains_Mono) with `--font-sans` / `--font-mono`.

---

## Answer

**Yes. Next.js 14.2 is sufficient. A Next major is not a prerequisite.**

Tailwind 4’s Next.js path is the PostCSS plugin `@tailwindcss/postcss` plus `@import "tailwindcss"` in CSS. Next 14 already compiles CSS through PostCSS and already has a `postcss.config.mjs`. Nothing in Tailwind’s or Next’s primary docs requires Next 15+ for that plugin.

The frozen Next **14** Tailwind page still documents the **v3** recipe (`tailwindcss init -p`, `autoprefixer`, `@tailwind` directives) because it was last updated 2023-07-31. Follow Tailwind’s current Next.js / PostCSS guides, not that frozen page.

**Contract to implement (when CAR-50 lands):**

1. Packages: `tailwindcss@^4.1` + `@tailwindcss/postcss` (dev). Keep `postcss`. Remove `autoprefixer` (and `postcss-import` if present).
2. `postcss.config.mjs`: `{ plugins: { "@tailwindcss/postcss": {} } }` — string-key object form (Next 14-safe).
3. `globals.css`: replace `@tailwind base; @tailwind components; @tailwind utilities;` with `@import "tailwindcss";`. Keep CAR-34 `:root { --bg: #121212; … }` as ordinary CSS variables.
4. Theme: prefer `@theme` / `@theme inline` in CSS. JS `tailwind.config.ts` is legacy — load with `@config` only if the upgrade tool cannot migrate it.
5. Run `npx @tailwindcss/upgrade` from `apps/frontend` on a clean tree (Node 20+). Review the diff; hand-fix fonts (`@theme inline`), `bg-dots`, and `@source not` for static Premium HTML.

**No official blocker forces a Next major.** Remaining work is CSS/PostCSS/theme migration, browser floor (Safari 16.4 / Chrome 111 / Firefox 128), and template class renames the upgrade tool mostly handles.

---

## 1. Package / PostCSS / `globals.css` contract

### 1.1 Packages

Tailwind’s Next.js guide and PostCSS guide install the same three packages:

```
npm install tailwindcss @tailwindcss/postcss postcss
```

Sources:

- [Install Tailwind CSS with Next.js](https://tailwindcss.com/docs/guides/nextjs)
- [Installing Tailwind CSS with PostCSS](https://tailwindcss.com/docs/installation/using-postcss) — “the most seamless way to integrate it with frameworks like Next.js and Angular.”

v4.1 uses the same PostCSS client. The v4.1 announcement’s PostCSS upgrade line is:

```
npm install tailwindcss@latest @tailwindcss/postcss@latest
```

Source: [Tailwind CSS v4.1](https://tailwindcss.com/blog/tailwindcss-v4-1)

Current Next.js docs (docs version 16.x) match that pair (`tailwindcss` + `@tailwindcss/postcss`) and the same PostCSS + `@import 'tailwindcss'` CSS. They do not name a minimum Next major for the plugin.

Source: [Next.js — Tailwind CSS](https://nextjs.org/docs/app/guides/tailwind-css) (canonical URL redirects to CSS getting-started; version stamp 16.3.2)

This repo already has `postcss@^8.5.3`. `@tailwindcss/postcss` lists `postcss` and `tailwindcss` as dependencies ([package source](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-postcss/package.json)).

### 1.2 PostCSS config

**v3 (this repo today):**

```js
plugins: {
  tailwindcss: {},
  autoprefixer: {},
}
```

**v4 (official):**

```js
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
export default config;
```

Sources: [Upgrade guide — Using PostCSS](https://tailwindcss.com/docs/upgrade-guide#using-postcss), [Next.js guide](https://tailwindcss.com/docs/guides/nextjs)

In v4 the PostCSS plugin moved out of the `tailwindcss` package into `@tailwindcss/postcss`. Imports and vendor prefixing are built in; **remove `autoprefixer` and `postcss-import`**.

Source: [Upgrade guide — Using PostCSS](https://tailwindcss.com/docs/upgrade-guide#using-postcss)

Compatibility docs: Tailwind “will do things like bundle your imports and add vendor prefixes.”

Source: [Compatibility — Sass, Less, and Stylus](https://tailwindcss.com/docs/compatibility)

**Next 14 interaction:** Next compiles CSS with PostCSS. A custom PostCSS file **completely disables** Next’s default Autoprefixer/`postcss-preset-env` pipeline; that is intended here because Tailwind 4 owns prefixing.

Source: [Next.js 14 — PostCSS](https://nextjs.org/docs/14/pages/building-your-application/configuring/post-css) (version 14.2.35)

Next 14 requires plugins as **strings**, not `require()`:

> Do **not use `require()`** to import the PostCSS Plugins. Plugins must be provided as strings.

It also documents the interoperable object form (`plugins: { 'plugin-name': {} }`). Tailwind’s official Next.js snippet uses that form with `"@tailwindcss/postcss": {}`.

Do **not** copy the function-style API from the plugin README (`import tailwindcss from '@tailwindcss/postcss'` then `plugins: [tailwindcss()]`) into Next 14 — that violates the string-plugin rule.

Source: [`@tailwindcss/postcss` README](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-postcss/README.md) (optional `base` / `optimize` / `transformAssetUrls`; default empty `{}` is enough)

The upgrade tool’s PostCSS migrator rewrites `tailwindcss: {}` → `'@tailwindcss/postcss': {}` and drops `autoprefixer`. This repo’s `postcss.config.mjs` matches the “simple” pattern the migrator targets.

Source: [`migrate-postcss.ts`](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-upgrade/src/codemods/config/migrate-postcss.ts)

### 1.3 CSS entry: `@import "tailwindcss"` vs `@tailwind`

v4 removes `@tailwind` directives:

```css
/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* v4 */
@import "tailwindcss";
```

Source: [Upgrade guide — Removed @tailwind directives](https://tailwindcss.com/docs/upgrade-guide#removed-tailwind-directives)

What that import expands to (official theme docs):

```css
@layer theme, base, components, utilities;
@import "./theme.css" layer(theme);
@import "./preflight.css" layer(base);
@import "./utilities.css" layer(utilities);
```

Source: [Theme variables — Default theme variables](https://tailwindcss.com/docs/theme#default-theme-variables)

Keep CAR-34 `:root { --bg: #121212; … }` **after** the import as ordinary CSS variables (not `@theme`). `@theme` is only for tokens that should mint utilities. `:root` is for variables that are not themselves utility namespaces.

Source: [Theme variables — Why @theme instead of :root?](https://tailwindcss.com/docs/theme#why-theme-instead-of-root)

Existing custom CSS in `globals.css` (`.grid-dots`, `.welcome-*`, `.plg-*`, `@keyframes`) stays valid. v4 does not forbid plain CSS next to the import.

Source: [Adding custom styles — Using custom CSS](https://tailwindcss.com/docs/adding-custom-styles#using-custom-css)

---

## 2. CAR-34 tokens → `@theme` vs keeping `tailwind.config`

### 2.1 Official mapping

| v3 JS (`theme.extend`) | v4 CSS | Utilities we use |
|---|---|---|
| `colors.bg: "var(--bg)"` | `--color-bg: var(--bg)` | `bg-bg`, `border-bg`, … |
| `colors.accent: "var(--accent)"` | `--color-accent: var(--accent)` | `bg-accent`, `ring-accent`, … |
| `colors.text-primary: "var(--text)"` | `--color-text-primary: var(--text)` | `text-text-primary` (same awkward name as v3) |
| `fontFamily.sans: ["var(--font-sans)", …]` | `--font-sans: var(--font-sans), …` | `font-sans` |
| `borderRadius.card/node/modal` | `--radius-card/node/modal` | `rounded-card`, `rounded-node`, `rounded-modal` |
| `spacing.grid: "4px"` | `--spacing-grid: 4px` | `p-grid`, `gap-grid`, … |
| `backgroundImage.dot-grid` / `brand-ribbon` | `--background-image-dot-grid` / `--background-image-brand-ribbon` | `bg-dot-grid`, `bg-brand-ribbon` |
| `backgroundSize.dots: "24px 24px"` | `--background-size-dots` | **not** a first-class `bg-dots` utility in v4 docs — see §3 |
| `keyframes.reveal` | `@keyframes reveal` inside `@theme` | only if paired with `--animate-*` |
| `borderColor.DEFAULT: "var(--border)"` | `--default-border-color` / `--border-color` via JS-compat | v4 default border color is `currentColor` unless preserved |
| `plugins: []` | omit | — |

Namespace table: `--color-*`, `--font-*`, `--radius-*`, `--spacing-*`, `--animate-*`.

Source: [Theme variable namespaces](https://tailwindcss.com/docs/theme#theme-variable-namespaces)

JS → CSS property names used by both the runtime compat layer and the upgrade tool (`colors` → `color`, `fontFamily` → `font`, `borderRadius` → `radius`, other camelCase keys kebab-cased, e.g. `backgroundImage` → `background-image`):

Source: [`keyPathToCssProperty` in `apply-config-to-theme.ts`](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/src/compat/apply-config-to-theme.ts)

### 2.2 `@theme` vs `@theme inline` (must hand-check)

If a theme variable **references another CSS variable**, official docs require `@theme inline` so the utility inlines the referenced value instead of pointing at the theme variable (which can resolve in the wrong place). Example from the docs: `--font-sans: var(--font-inter)`.

Source: [Theme variables — Referencing other variables](https://tailwindcss.com/docs/theme#referencing-other-variables)

**Colors:** `--color-accent: var(--accent)` is not circular (`--color-accent` ≠ `--accent`). Still use `@theme inline` so utilities emit `var(--accent)` rather than `var(--color-accent)` that then looks up `--accent`.

**Fonts (collision):** layout already does:

```ts
Inter({ subsets: ["latin"], variable: "--font-sans" })
JetBrains_Mono({ variable: "--font-mono" })
```

and the JS config sets `fontFamily.sans: ["var(--font-sans)", "Inter", …]`.

If the upgrade tool emits `@theme { --font-sans: var(--font-sans), Inter, … }` that **is circular**: `@theme` also generates `--font-sans` on `:root`. Official Next 14 font + Tailwind example uses **distinct** variable names (`--font-inter`, `--font-roboto-mono`) in `next/font`, then maps them in Tailwind.

Source: [Next.js 14 — Font Optimization, With Tailwind CSS](https://nextjs.org/docs/14/app/building-your-application/optimizing/fonts)

**Hand work:** either (a) rename next/font variables to `--font-inter` / `--font-jetbrains` and `@theme inline { --font-sans: var(--font-inter), … }`, or (b) keep `--font-sans` on next/font and `@theme inline` with a **different** theme key. Do not let `@theme` and next/font both own `--font-sans` without `inline`.

### 2.3 What `npx @tailwindcss/upgrade` does vs hand work

Official tool (Node **20+**):

```
npx @tailwindcss/upgrade
```

It updates dependencies, migrates JS config to CSS, migrates stylesheets, and rewrites templates. Run on a **clean git tree** (or `--force`). Review the diff; complex projects still need hand tweaks.

Source: [Upgrade guide — Using the upgrade tool](https://tailwindcss.com/docs/upgrade-guide#using-the-upgrade-tool)

This repo already uses **Node 20** in `apps/frontend/Dockerfile` (`FROM node:20-alpine`).

Tool internals (primary source: upgrade package):

| Step | Behavior |
|---|---|
| JS config | If `canMigrateConfig` passes, emit `@theme { … }`, `@source` globs, delete `tailwind.config.ts`. If not, leave the file and inject `@config` in CSS. |
| Theme | `migrateTheme` walks resolved `theme.extend`, writes `--{keyPathToCssProperty}: value`, and dumps `keyframes` as CSS inside `@theme`. |
| Content | Compares `content` globs to auto-detection; only emits `@source` when auto-scan would miss files. |
| PostCSS | See §1.2. |
| Templates | Renames classes for v4 (e.g. `outline-none` → `outline-hidden`, shadow/ring scale). |
| Fallback | `corePlugins`, `safelist`, `separator` are **not** supported in v4 JS config. Safelist → `@source inline()`. |

Sources:

- [Upgrade guide — Using a JavaScript config file](https://tailwindcss.com/docs/upgrade-guide#using-a-javascript-config-file)
- [`@tailwindcss/upgrade` `index.ts`](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-upgrade/src/index.ts)
- [`migrate-js-config.ts`](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-upgrade/src/codemods/config/migrate-js-config.ts)

This config should be migratable: no `presets`, `plugins: []`, no theme functions, keys that exist on the default theme (`colors`, `fontFamily`, `borderRadius`, `spacing`, `backgroundImage`, `backgroundSize`, `keyframes`, `borderColor`). If the tool still bails (e.g. `findStaticPlugins` heuristics), CSS will get:

```css
@import "tailwindcss";
@config "../../tailwind.config.ts";
```

`@config` remains supported for compatibility and can coexist with `@theme` / `@utility`; CSS wins on conflicts.

Source: [Functions and directives — `@config`](https://tailwindcss.com/docs/functions-and-directives#config)

**Recommended after the tool:** prefer CSS-first `@theme` (delete JS config) so CAR-34 tokens live next to `:root` in `globals.css`. Incremental path: `@config` first, then move namespaces to `@theme` later.

### 2.4 Suggested `@theme` shape (after tool, if writing by hand)

```css
@import "tailwindcss";

@theme inline {
  --font-sans: var(--font-inter), Inter, system-ui, sans-serif;
  --font-mono: var(--font-jetbrains), "JetBrains Mono", monospace;

  --color-bg: var(--bg);
  --color-bg-sidebar: var(--bg-sidebar);
  --color-surface: var(--surface);
  --color-surface-elevated: var(--surface-elevated);
  --color-surface-node: var(--surface-node);
  --color-accent: var(--accent);
  --color-accent-mint: var(--accent-mint);
  --color-accent-mint-bright: var(--accent-mint-bright);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-locked: var(--locked);
  --color-evidence: var(--evidence);
  --color-text-primary: var(--text);
  --color-text-secondary: var(--text-2);
  --color-text-muted: var(--text-3);
  --color-border: var(--border);
  --color-border-soft: var(--border-soft);

  --radius-card: 12px;
  --radius-node: 16px;
  --radius-modal: 12px;

  --spacing-grid: 4px;

  --background-image-brand-ribbon: linear-gradient(135deg, var(--accent-mint) 0%, var(--accent) 100%);
  --background-image-dot-grid: radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px);
}

@utility bg-dots {
  background-size: 24px 24px;
}

:root {
  --bg: #121212;
  /* …existing CAR-34 tokens… */
}
```

`--background-image-*` is how the upgrade/compat layer names v3 `backgroundImage` keys (see `keyPathToCssProperty`). It is **not** listed in the public namespace table; the public `background-image` docs customize gradient **colors** via `--color-*`, not named background images. Treat named `bg-dot-grid` / `bg-brand-ribbon` as a compat/upgrade-tool feature; if a class goes missing, fall back to `@utility` (official custom-utility API).

Sources: [Adding custom styles — `@utility`](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-utilities), [background-image](https://tailwindcss.com/docs/background-image)

---

## 3. Official breakages that hit this repo

### 3.1 Does **not** hit: `@apply`

No `@apply` under `apps/frontend`. The v4 `@apply` / `@reference` rules for CSS modules / Vue SFCs are irrelevant here.

Source: [Upgrade guide — Using @apply with Vue, Svelte, or CSS modules](https://tailwindcss.com/docs/upgrade-guide#using-apply-with-vue-svelte-or-css-modules)

### 3.2 Opacity modifiers — improved, not a v3-style trap

v4 **removed** `bg-opacity-*` / `text-opacity-*` (this app does not use them). The `/50` modifier remains the API (`bg-black/50`). v4 implements alpha with `color-mix()` / `@property`; v4.1 adds inlined fallbacks for older browsers.

This app already uses modifiers on CSS-variable colors, e.g. `bg-surface/90`, `border-border/60`, `bg-surface-node/40`. In v3 those often failed unless colors were RGB channels. v4 color-mix is designed to mix any color including CSS variables.

Sources:

- [Upgrade guide — Removed deprecated utilities](https://tailwindcss.com/docs/upgrade-guide#removed-deprecated-utilities)
- [Colors — Adjusting opacity](https://tailwindcss.com/docs/colors#adjusting-opacity)
- [v4.1 — Improved compatibility with older browsers](https://tailwindcss.com/blog/tailwindcss-v4-1)

Verify `bg-surface/90` and `border-border/60` after upgrade. If a token is not a `<color>` (unlikely for these hex aliases), use `--alpha(var(--color-surface) / 90%)` in CSS.

### 3.3 Content paths vs `@source`

v4 **auto-scans** the project. It skips `.gitignore`, `node_modules`, binaries, **CSS files**, and lockfiles. `content: […]` in JS config is not auto-read; the upgrade tool may emit `@source` or rely on auto-scan.

Sources:

- [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Functions and directives — `@source`](https://tailwindcss.com/docs/functions-and-directives#source)

**Hand-edit for this repo:** `apps/frontend/public/premium-landings/{a,b}.html` are committed, **not** gitignored, static clones with huge compiled class lists. Auto-scan will treat them as source and can bloat production CSS. Exclude them:

```css
@import "tailwindcss";
@source not "../../public/premium-landings";
```

(`@source not` is documented in v4.1.)

Source: [v4.1 — Ignore specific paths with `@source not`](https://tailwindcss.com/blog/tailwindcss-v4-1)

If `next` is ever invoked from the monorepo root rather than `apps/frontend`, set a source base:

```css
@import "tailwindcss" source("../src");
```

Source: [Detecting classes — Setting your base path](https://tailwindcss.com/docs/detecting-classes-in-source-files#setting-your-base-path)

Docker `WORKDIR` is `/app` with the frontend copied in — CWD matches today’s `content` globs.

### 3.4 `bg-dot-grid` / `bg-dots`

Used in `WelcomeLanding.tsx`: `bg-dot-grid bg-dots`.

- `bg-dot-grid` ← v3 `backgroundImage["dot-grid"]`. Upgrade/compat maps to `--background-image-dot-grid`. Confirm `bg-dot-grid` still generates; otherwise `@utility bg-dot-grid { background-image: … }` (there is already a `.grid-dots` plain-CSS duplicate in `globals.css`).
- `bg-dots` ← v3 `backgroundSize.dots`. v4 `background-size` docs only document `bg-auto` | `bg-cover` | `bg-contain` | `bg-size-[…]` | `bg-size-(--var)`. There is **no** documented `--background-size-*` → `bg-dots` utility. **Hand-add** `@utility bg-dots { background-size: 24px 24px; }` or change the markup to `bg-size-[24px_24px]`.

Source: [background-size](https://tailwindcss.com/docs/background-size)

`bg-brand-ribbon` is the same class of token as `bg-dot-grid` (custom `backgroundImage`).

### 3.5 Autoprefixer

Remove it. Tailwind 4 prefixes via Lightning CSS inside `@tailwindcss/postcss`. Leaving both can double-process CSS.

Sources: [Upgrade guide — Using PostCSS](https://tailwindcss.com/docs/upgrade-guide#using-postcss), [Compatibility](https://tailwindcss.com/docs/compatibility)

Next 14: custom PostCSS config already replaces Next’s default Autoprefixer. An empty `{}` plugin list for `@tailwindcss/postcss` is the documented Next + TW4 setup.

### 3.6 Template class renames that **do** appear in `apps/frontend`

The upgrade tool rewrites most of these. Inventory vs official rename table:

| Class in repo | v4 change | Source |
|---|---|---|
| `outline-none` (Select, GoalPicker, DiagnosticPills, EditableDiagnosis, NodeDrawer) | Meaning changed: new `outline-none` is real `outline-style: none`. Accessibility-preserving old behavior is `outline-hidden`. | [Renamed outline utility](https://tailwindcss.com/docs/upgrade-guide#renamed-outline-utility) |
| `ring-accent` + `focus:ring-2` | Bare `ring` is 1px (was 3px) and default color is `currentColor` (was `blue-500`). This app already sets color (`ring-accent`) and width (`focus:ring-2`) in several places. | [Default ring width and color](https://tailwindcss.com/docs/upgrade-guide#default-ring-width-and-color) |
| `space-y-*` (many lists) | Selector changed from `~` siblings to `:not(:last-child)` + margin-bottom. Mostly fine for block stacks; watch inline children. | [Space-between selector](https://tailwindcss.com/docs/upgrade-guide#space-between-selector) |
| `divide-y divide-border` (WelcomeLanding) | Same selector shift as space-between. | [Divide selector](https://tailwindcss.com/docs/upgrade-guide#divide-selector) |
| `backdrop-blur-sm` (DeployBadge) | `blur-sm` / `backdrop-blur-sm` look different unless updated to `-xs`. Tool should rewrite. | [Updated shadow, radius, and blur scales](https://tailwindcss.com/docs/upgrade-guide#updated-shadow-radius-and-blur-scales) |
| `border` / `border-border` | Default border color is `currentColor`. This app usually sets `border-border`. Bare `border` without a color will change. | [Default border color](https://tailwindcss.com/docs/upgrade-guide#default-border-color) |
| Preflight: buttons `cursor: default`; `hidden` vs `flex`/`block` | May affect native `<button>` chrome and any `hidden` + display-class combos. | [Preflight changes](https://tailwindcss.com/docs/upgrade-guide#preflight-changes) |

`shadow-sm` / `rounded-sm` as the old “bare” scale: this app mostly uses `rounded-md` / `rounded-card`. Low risk; still run the template migrator.

### 3.7 Browser floor (product constraint, not Next)

v4 targets Safari 16.4+, Chrome 111+, Firefox 128+. Core features use `@property` and `color-mix()`. v4.1 degrades more gracefully on older Safari but the **designed** floor is unchanged.

Sources: [Upgrade guide — Browser requirements](https://tailwindcss.com/docs/upgrade-guide#browser-requirements), [Compatibility — Browser support](https://tailwindcss.com/docs/compatibility)

---

## 4. Yes/no: is Next 14.2 enough?

### Verdict: **yes**

| Claim | Source | What it shows |
|---|---|---|
| TW4 + Next is PostCSS `@tailwindcss/postcss` + `@import "tailwindcss"` | [tailwindcss.com/docs/guides/nextjs](https://tailwindcss.com/docs/guides/nextjs) | No Next version pin. `create-next-app@latest` is only for **new** apps. |
| PostCSS is the Next/Angular integration path | [tailwindcss.com/docs/installation/using-postcss](https://tailwindcss.com/docs/installation/using-postcss) | Framework-agnostic plugin. |
| Next 14 compiles CSS with PostCSS; custom `postcss.config.*` is supported | [Next.js 14 PostCSS](https://nextjs.org/docs/14/pages/building-your-application/configuring/post-css) | This repo already has one. |
| Next 14 Tailwind **docs** still show v3 | [Next.js 14 Tailwind CSS](https://nextjs.org/docs/14/app/building-your-application/styling/tailwind-css) (lastUpdated 2023-07-31, version 14.2.35) | Frozen v3 recipe. Not a statement that v4 is unsupported. |
| Current Next docs document TW4 PostCSS without a Next-major gate | [Next.js Tailwind CSS](https://nextjs.org/docs/app/guides/tailwind-css) | Same packages/config as Tailwind’s guide. |
| Next 15 release notes do not make TW4 a reason to upgrade Next | [Next.js 15](https://nextjs.org/blog/next-15) | No Tailwind 4 prerequisite. |

**Do not** treat “Next 14 docs still say `npx tailwindcss init -p`” as “you must upgrade Next.” That page predates Tailwind 4.

**Do** follow Tailwind’s current Next.js guide for the PostCSS file and CSS import, while keeping Next 14.2 / React 18.

### What is **not** a Next-major blocker

- React 18 vs 19 — Tailwind is build-time CSS. Next 15’s React 19 bump is unrelated.
- `next/font` — Next 14 API. See §5.
- Turbopack — Next 14.2 `next dev --turbo` is optional; default `next dev` is webpack. Tailwind’s compatibility notes on Turbopack are about CSS-module **performance**, not a Next 15 requirement ([Compatibility — CSS modules](https://tailwindcss.com/docs/compatibility)).
- Node 20 — required by the **upgrade tool**, already the frontend Docker image. Not a Next major.

### If something still broke at runtime

That would be a Next 14 CSS/`@import` loader quirk, not a documented prerequisite. First-party mitigation is still PostCSS (Tailwind’s documented Next path), not jumping to Next 15. A Next major would only become necessary if a **future** Next or Tailwind release dropped PostCSS or required a compiler API Next 14 lacks — **not** the case in the docs cited above.

---

## 5. `canvas-confetti` and Google fonts

### 5.1 `canvas-confetti`

**Not in `apps/frontend` on origin/main.** It lives in the Premium B **Vite** bake-off:

- `claude-design-docs/premium-landings/b/package.json` — `"canvas-confetti": "^1.9.4"`
- imported from `ApplicationModal.tsx` (client-side canvas)

It paints on a `<canvas>` with JS. It does not go through PostCSS, Tailwind, or `next/font`. It does not constrain TW4 on Next 14.

If Premium B is later ported into the Next app, keep the library in a Client Component (`"use client"`). That is a React/Next client-boundary concern, not a Tailwind 4 concern.

### 5.2 Google fonts / `next/font`

**Product app (Next 14):** `src/app/layout.tsx` already uses `next/font/google` (`Inter`, `JetBrains_Mono`) with `variable: "--font-sans"` / `"--font-mono"`. Next 14 self-hosts Google fonts at build time; **no requests are sent to Google by the browser.**

Source: [Next.js 14 — Font Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/fonts)

Wiring to Tailwind is a CSS variable, documented for Next 14 + Tailwind (v3 config shown). In v4 the same variable is mapped with `@theme inline` (§2.2). `next/font` does not need a Next major to work with TW4.

**Premium B (Vite, already Tailwind 4.1.17 + `@tailwindcss/vite`):** `index.html` loads Plus Jakarta Sans + JetBrains Mono from `fonts.googleapis.com`. That file is outside the Next pipeline (also shipped as a static clone at `apps/frontend/public/premium-landings/b.html`). It does not participate in `apps/frontend` PostCSS. Porting that landing into Next should switch to `next/font/google` (`Plus_Jakarta_Sans`, `JetBrains_Mono`) per Next 14 font docs — again independent of a Next major.

Premium B’s Tailwind 4 setup is **Vite** (`@tailwindcss/vite`). The Next app must keep **PostCSS** (`@tailwindcss/postcss`), not the Vite plugin.

Sources: [Upgrade guide — Using Vite](https://tailwindcss.com/docs/upgrade-guide#using-vite) vs [Using PostCSS](https://tailwindcss.com/docs/upgrade-guide#using-postcss)

---

## Implementation notes for CAR-50 (not done here)

1. Work in `apps/frontend` only; clean git tree; Node 20.
2. `npx @tailwindcss/upgrade` (or `--force` on a dedicated branch).
3. Confirm `postcss.config.mjs` is string-key `@tailwindcss/postcss` only; `autoprefixer` gone from `package.json`.
4. Confirm `globals.css` starts with `@import "tailwindcss";`; `:root` tokens remain.
5. Fix fonts with `@theme inline` + distinct next/font variable names.
6. Add `@utility bg-dots` (or change markup) and `@source not` for `public/premium-landings`.
7. Visual-check: `outline-none` → `outline-hidden` on inputs, `bg-dot-grid bg-dots`, `rounded-node` / `rounded-card`, `bg-surface/90`, `ring-accent`.
8. Do not run the Vite plugin in Next. Do not upgrade Next solely for this.

---

## Sources (primary only)

| Doc | URL |
|---|---|
| Tailwind v4 upgrade guide | https://tailwindcss.com/docs/upgrade-guide |
| Tailwind + PostCSS install | https://tailwindcss.com/docs/installation/using-postcss |
| Tailwind + Next.js install | https://tailwindcss.com/docs/guides/nextjs |
| Theme variables / `@theme` | https://tailwindcss.com/docs/theme |
| Functions and directives (`@import`, `@theme`, `@source`, `@utility`, `@config`) | https://tailwindcss.com/docs/functions-and-directives |
| Detecting classes / `@source` | https://tailwindcss.com/docs/detecting-classes-in-source-files |
| Adding custom styles / `@utility` | https://tailwindcss.com/docs/adding-custom-styles |
| Compatibility (browsers, prefixes, no Sass) | https://tailwindcss.com/docs/compatibility |
| Colors / opacity | https://tailwindcss.com/docs/colors |
| background-image | https://tailwindcss.com/docs/background-image |
| background-size | https://tailwindcss.com/docs/background-size |
| Tailwind CSS v4.1 | https://tailwindcss.com/blog/tailwindcss-v4-1 |
| `@tailwindcss/postcss` README | https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-postcss/README.md |
| Upgrade tool + JS/PostCSS migrators | https://github.com/tailwindlabs/tailwindcss/tree/main/packages/%40tailwindcss-upgrade |
| JS theme key → CSS property | https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/src/compat/apply-config-to-theme.ts |
| Next.js 14 Tailwind (v3 recipe, frozen) | https://nextjs.org/docs/14/app/building-your-application/styling/tailwind-css |
| Next.js 14 PostCSS | https://nextjs.org/docs/14/pages/building-your-application/configuring/post-css |
| Next.js 14 fonts + Tailwind variables | https://nextjs.org/docs/14/app/building-your-application/optimizing/fonts |
| Next.js current Tailwind (v4 recipe) | https://nextjs.org/docs/app/guides/tailwind-css |
| Next.js 15 blog | https://nextjs.org/blog/next-15 |
