# Premium landing previews (A / B)

Stakeholder bake-off clones. **Not** the F3a product funnel.

| URL | Source | Artifact |
|-----|--------|----------|
| `/welcome/premium-a` | [`a/`](./a/) | `apps/frontend/public/premium-landings/a.html` |
| `/welcome/premium-b` | [`b/`](./b/) | `apps/frontend/public/premium-landings/b.html` |

Labs: `/career-forge/welcome/premium-a` and `/career-forge/welcome/premium-b`.

## Contract (CAR-41 grill)

- Visual **and** commercial clone of these Vite apps (pricing, apply/strategy theater, confetti on B).
- Direct URL only — **not** linked from `/welcome` or `/welcome/plg`.
- CTAs do **not** enter diagnosis (`/`).
- `noindex,nofollow` + title suffix `· preview`.
- Served via Next rewrite to committed single-file HTML. Do **not** port into `apps/frontend` Tailwind 3.

## Regenerate

```bash
make premium-landings
```

Commit the overwritten HTML under `apps/frontend/public/premium-landings/`.
