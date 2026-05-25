# Career Forge — functional prototype

Static React mock (Babel in browser). No build step.

## Run locally

```bash
cd claude-design-docs/prototype
python3 -m http.server 8765
open http://localhost:8765/
```

**Correct URL:** `http://localhost:8765/` (serves `index.html` → `Career Forge.html`)

Legacy bookmarks: `http://localhost:8765/Career%20OS.html` redirects automatically.

## Deep links (hash)

| Hash | Screen |
|------|--------|
| `#goal` | Goal picker |
| `#diag` | Diagnostic (pill rounds) |
| `#result` | Diagnosis result |
| `#forge` | Live forge stream |
| `#roadmap` | Skill graph (vertical spine) |
| `#validate` | Validation interview |
| `#adaptive` | Adaptive roadmap state |

## Files

| File | Role |
|------|------|
| `Career Forge.html` | Main entry |
| `index.html` | Redirect stub |
| `Career OS.html` | Legacy redirect (HAC-22 rename) |
| `app.jsx` | Shell + navigation |
| `screens-flow.jsx` | Goal, diagnostic, diagnosis, validation |
| `screens-dashboard.jsx` | Roadmap + mentor drawer |
| `screens-forge.jsx` | Forge stream + reveal |
| `skill-graph.jsx` | Vertical roadmap graph |
| `components.jsx` | Shared UI |
| `styles.css` | Borderless tokens + layout |
