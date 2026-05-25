# Backlog — CV parsing (future work)

> **Status:** Not in scope for home-screen-v1. UI stores attachment only.

## Context

Home screen (Goal Picker) allows optional CV upload (PDF/DOC/DOCX) as a quick-win UI:

- Drag-and-drop + file picker
- Stored in `sessionStorage` as base64 + metadata (`filename`, `size`, `mimeType`)
- Shown with remove button — **no parsing, scrape, or LLM yet**

## Future issue scope

1. **Upload pipeline** — move CV from sessionStorage to backend (S3/blob + profile row)
2. **Extract text** — PDF/DOCX parser (no LLM required for v1 extract)
3. **Signal enrichment** — feed extracted skills/years into `DiagnosisRequest` / identity graph
4. **Privacy** — retention policy, delete-on-request, PII handling

## Acceptance (when implemented)

- Attached CV influences diagnosis (skills/gaps) when present
- User can remove/replace CV before forge
- Fail gracefully if parse fails (diagnosis still works from pills)

## Linear

Tracked as **[HAC-33](https://linear.app/hackas-borderless/issue/HAC-33/cv-parsing-extrair-sinais-do-curriculo-para-diagnostico)** in Linear.
