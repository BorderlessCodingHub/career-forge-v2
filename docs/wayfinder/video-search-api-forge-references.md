# CAR-114 — Video search API options for forge References

**Question:** What **dedicated video search** options can feed Node **Video References** during or after forge, with a quality bar (duration, channel, views), and how do they compare to the current `web_search` path?

**Snapshot (origin/main):** Forge `research_enrich` calls `OpenAiNativeWebSearchClient` (`ai/tools/openai_web_search.py`) with Responses API `tools=[{"type":"web_search"}]` — title/URL/snippet only. Planner attaches `StudyResource` (`schemas/study_plan.py`: `source_type` ∈ `official_docs|tutorial|reference|example`; no video type). ADR-007 `/reference` is allowlist-only embed + Escape hatch; learner preview uses `referrerPolicy="no-referrer"`. Glossary already defines **Video Reference** (dedicated video search + quality bar; official docs win when equal). `MAX_RESEARCH_ITERATIONS = 3` web searches per forge.

---

## Answer

**YouTube Data API v3 (`search.list` + `videos.list`) is the only first-party, dedicated video search that can enforce a structured quality bar.** OpenAI has **no** hosted `video_search` tool — only `web_search` (and image web search). Domain-filtering `web_search` to `youtube.com` can surface watch URLs but does **not** return duration, view count, or channel stats as API fields.

**Contract to implement (when a follow-on issue lands):**

1. **Discovery:** `GET youtube/v3/search` with `type=video`, `videoEmbeddable=true`, optional `videoDuration` / `order` / `safeSearch` / `relevanceLanguage`.
2. **Quality bar:** batch `GET youtube/v3/videos?id=…&part=snippet,contentDetails,statistics,status` (≤50 ids/call) and filter on `contentDetails.duration`, `statistics.viewCount`, `snippet.channelTitle` / `channelId`, `status.embeddable`.
3. **Product attach:** write a **Video Reference** (title + watch URL) onto a Node — not a Live Forge `artifact_found` Source until attached ([CONTEXT.md](../../CONTEXT.md)).
4. **Viewer:** prove `youtube.com` (and optionally `youtube-nocookie.com`) on the operator embed allowlist; keep Escape hatch. **Do not** keep `no-referrer` on YouTube iframes — YouTube requires an HTTP `Referer` for embedded playback.
5. **Do not** treat OpenAI `web_search` as the quality bar. At most use it as a cheap discovery hint, then enrich/filter via YouTube Data API — or skip it and search YouTube directly.

**No OpenAI first-party video search exists today.** Remaining work is GCP key + quota plan, a small YouTube client beside (not inside) `openai_web_search.py`, schema/source_type for video, and a YouTube-specific referrer policy on the Reference viewer adapter.

---

## 1. Current forge path (constraints)

### 1.1 What `research_enrich` returns today

`roadmap_forge.iter_research_enrichment_events` builds up to three prompts (“You must use web_search…”) and yields `artifact_found` cards with `{title, url, snippet}` from citation annotations. There is no duration, channel, views, or embeddable flag.

Sources in-repo:

- `apps/backend/src/career_forge/ai/tools/openai_web_search.py` — `WebSearchSource(title, url, snippet)`
- `apps/backend/src/career_forge/ai/graphs/roadmap_forge.py` — `MAX_RESEARCH_ITERATIONS = 3`, `_research_artifact`
- `apps/backend/src/career_forge/schemas/study_plan.py` — `StudyResource`

### 1.2 ADR-007 / Escape hatch

| Concern | Locked decision |
|---|---|
| Object | **Reference** on a Node — not Forge source, not `/learn` |
| Embed | Allowlist-only; default = source card + **Open original** Escape hatch |
| Proxy | No third-party HTML fetch through Career Forge |
| Escape hatch | New tab; does not mark `done` |

YouTube embeds are **compatible in principle** with ADR-007 (hostname allowlist + Escape hatch). They are **not** compatible with today’s blanket `REFERENCE_PREVIEW_REFERRER_POLICY = "no-referrer"` once `youtube.com` is liberated — see §4.

Sources: [ADR-007](../decisions/ADR-007-reference-viewer.md), `apps/frontend/src/lib/reference-viewer.ts`

### 1.3 Glossary already names the product object

> **Video Reference:** A Reference whose primary medium is video, attached to a Node after a dedicated video search with a quality bar. Official docs References still win when equal.

Source: [CONTEXT.md](../../CONTEXT.md)

---

## 2. OpenAI: no dedicated video search

### 2.1 Hosted tools (Responses API)

Documented built-in tools include **web search**, **file search**, **Code Interpreter**, **computer use**, plus function calling / MCP / tool search. Pricing lists **Web search** and **Image Web search** — not video search.

Sources:

- [Using tools](https://developers.openai.com/api/docs/guides/tools)
- [Web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Pricing — Tools](https://developers.openai.com/api/docs/pricing)

Career Forge already binds `{"type":"web_search"}` via LangChain Responses (`use_responses_api=True`).

### 2.2 What `web_search` can and cannot do for video

| Capability | `web_search` | Gap vs Video Reference quality bar |
|---|---|---|
| Find `youtube.com/watch?v=` URLs | Yes (general web index) | No structured video identity |
| Domain filter to `youtube.com` | Yes — `filters.allowed_domains` (≤100), Responses `web_search` only | Still page citations, not video stats |
| Duration / viewCount / channel | No API fields | Model may **guess** from page text — unreliable |
| Embeddable flag | No | Cannot prefer embeddable before attach |
| Image results | Separate `search_content_types: ["image"]` | Not video |

Domain filtering example (official): omit `https://`; subdomains included; only on Responses `web_search` (not legacy `web_search_preview`).

Source: [Web search — Domain filtering](https://developers.openai.com/api/docs/guides/tools-web-search)

### 2.3 Cost (OpenAI)

| Item | Official price |
|---|---|
| Web search tool call | **$10.00 / 1k calls** (+ search-content tokens at model input rates) |
| Image web search | Same $10 / 1k + tokens |
| `web_search_preview` (non-reasoning) | $25 / 1k; search content tokens free |

Forge already pays this for up to **3** research iterations per run (plus planner/evaluator model tokens). Using another `web_search` pass only for YouTube URLs adds **~$0.01/call + tokens** without unlocking the quality bar.

Source: [Pricing — Tools](https://developers.openai.com/api/docs/pricing)

### 2.4 Verdict on OpenAI

**Not a dedicated video search option.** Keep `web_search` for official-docs / tutorial Forge sources. For Video References, call YouTube (or accept Escape-hatch-only links with no enforceable quality bar).

---

## 3. YouTube Data API v3 (primary option)

### 3.1 Search — `search.list`

```
GET https://www.googleapis.com/youtube/v3/search
  ?part=snippet
  &type=video
  &q=...
  &videoEmbeddable=true
  &videoDuration=medium   # optional: short | medium | long
  &order=relevance        # or viewCount, date, rating, …
  &safeSearch=strict
  &maxResults=5..50
  &key=API_KEY
```

Useful filters for a learning quality bar **at search time**:

| Parameter | Quality-bar role |
|---|---|
| `type=video` | Videos only |
| `videoEmbeddable=true` | Prefer in-product embed path |
| `videoDuration` | `short` (&lt;4m), `medium` (4–20m), `long` (&gt;20m) — coarse buckets only |
| `order` | `relevance` (default) or `viewCount` |
| `videoCaption=closedCaption` | Prefer captioned teaching content |
| `relevanceLanguage` / `regionCode` | Locale |
| `channelId` | Curated educator allowlist (optional later) |

`search.list` **snippet** gives `title`, `description`, `channelTitle`, `channelId`, `publishedAt`, thumbnails — **not** exact duration or view count.

Sources: [Search: list](https://developers.google.com/youtube/v3/docs/search/list)

### 3.2 Metadata / quality bar — `videos.list`

```
GET https://www.googleapis.com/youtube/v3/videos
  ?part=snippet,contentDetails,statistics,status
  &id=id1,id2,…   # up to 50
  &key=API_KEY
```

| Field | Use for quality bar |
|---|---|
| `contentDetails.duration` | ISO 8601 (`PT15M33S`) — exact length; reject Shorts / &lt;N min / &gt;N min |
| `statistics.viewCount` | Minimum views floor (product-chosen) |
| `statistics.likeCount` / `commentCount` | Optional secondary signals |
| `snippet.channelTitle` / `channelId` | Channel allow/deny / display |
| `status.embeddable` | Confirm embed before preferring iframe path |
| `status.madeForKids` | Required awareness if embedding (COPPA/GDPR policies) |

Quota cost: **1 unit** per `videos.list` call (general bucket).

Sources: [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list), [Videos resource](https://developers.google.com/youtube/v3/docs/videos)

### 3.3 Quotas, rate, cost

Official default allocation (docs updated **2026-09-15**):

| Bucket | Default / day | Cost per call |
|---|---|---|
| `search.list` | **100** calls (own bucket) | **1** search quota unit |
| `videos.insert` | 100 (own bucket; irrelevant here) | 1 |
| All other methods (incl. `videos.list`) | **10,000** units | `videos.list` = **1** |

Daily reset: midnight Pacific Time. Invalid requests still cost quota. Extra pages of `search.list` each cost another search unit.

**Monetary cost:** API access itself is not sold per-call; quota beyond default requires a **compliance audit + extension form**, not a public price list.

Sources:

- [Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Quota and Compliance Audits](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits)
- [Audit and Quota Extension Form](https://support.google.com/youtube/contact/yt_api_form)

**Capacity sketch for Career Forge:**

| Pattern | Search quota | Notes |
|---|---|---|
| 1 `search.list` per forge (attach videos after plan) | ~100 forges/day before extension | Fits default if video pass is once per run |
| 1 search **per Node** (lean forge ~few nodes) | Burns 100 searches fast | Prefer one query per skill cluster or per forge |
| `search.list` + 1 `videos.list` for top-k | Search 1 + general 1 | Metadata enrich is cheap vs search |

Do **not** multiply GCP projects to dodge quota — Developer Policies treat quotas as abuse controls; extensions go through audit.

### 3.4 ToS / product use / embedding

| Topic | Rule (primary) | Product implication |
|---|---|---|
| API + embedded player | YouTube API Services ToS + Developer Policies apply to Data API **and** embeds | Treat Watch URL + IFrame Player as API Client surface |
| Required Minimum Functionality | Embedded players must send **HTTP Referer**; recommend `strict-origin-when-cross-origin`; no overlays on player chrome; size/autoplay rules | Escape hatch OK; iframe must not use `no-referrer` |
| Branding / player | Do not obscure YouTube branding or alter undocumented player UI | Use official embed / IFrame API params only |
| Audiovisual content | Do not download/cache/store YouTube A/V without prior written approval | Store **Reference title + URL** (+ optional cached metadata with refresh rules); never mirror video bytes |
| API Data retention | Non-Authorized Data: temporary store ≤ **30 days**, then delete or refresh; display current data | Rank with viewCount at selection time; if persisting stats, refresh or drop |
| Terms link | API Clients must link YouTube ToS and state users agree to YouTube ToS | Privacy/terms copy when shipping embeds |
| Made for Kids | Look up MFK status when embedding; restrict tracking accordingly | Use `status.madeForKids` from `videos.list` |
| Commercial | Aggregator-only ad farms discouraged; incidental product embeds OK if policies met | Career Forge teaching loop ≠ video dump site |

Sources:

- [YouTube API Services Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service)
- [Developer Policies](https://developers.google.com/youtube/terms/developer-policies) (§ III.E storage; § III.E.4 refresh; no A/V download)
- [Required Minimum Functionality](https://developers.google.com/youtube/terms/required-minimum-functionality)
- [Embed videos & playlists (Help)](https://support.google.com/youtube/answer/171780) — Referer / error 153
- [IFrame Player API](https://developers.google.com/youtube/iframe_api_reference)

### 3.5 Auth model

Public search + video metadata: **API key** (Google Cloud project with YouTube Data API v3 enabled) is enough for `search.list` / `videos.list` without user OAuth. IFrame embed does not need OAuth for public videos.

---

## 4. Embeddability vs Escape hatch (ADR-007)

### 4.1 Happy path

1. Operator liberates `youtube.com` (and/or `youtube-nocookie.com`) via Content desk after proven iframe preview.
2. Learner `/reference` embeds `https://www.youtube.com/embed/VIDEO_ID` (or nocookie host).
3. Escape hatch always offers **Open original** → `https://www.youtube.com/watch?v=VIDEO_ID` (new tab).

This matches ADR-007: allowlist embed when proven; Escape hatch never removed.

### 4.2 Hard conflict with current preview policy

Repo today:

```ts
export const REFERENCE_PREVIEW_REFERRER_POLICY = "no-referrer";
```

YouTube Help / RMF: missing Referer → blocked embed playback (**error 153**); viewers can still use Watch on YouTube. Official recommendation: do not suppress Referer; prefer `strict-origin-when-cross-origin`.

**Wayfinder consequence:** a YouTube host adapter must override referrer policy for that hostname (or change the global default). Keeping blanket `no-referrer` means liberated YouTube hosts still degrade to Escape hatch only.

### 4.3 Non-embeddable videos

Even with `videoEmbeddable=true` at search time, always re-check `status.embeddable` on `videos.list`. If false → store URL anyway, render **source card + Escape hatch** (ADR-007 default). Do not blank-iframe.

---

## 5. Options matrix (decision aid)

| Option | Dedicated video search? | Quality-bar metadata | Cost / limits | Embed path | Fit for Video References |
|---|---|---|---|---|---|
| **A. YouTube `search.list` + `videos.list`** | Yes | Duration, channel, views, embeddable, captions filter | Free default; **100 searches/day**; extension via audit | Official iframe + Escape hatch (fix referrer) | **Primary** |
| **B. OpenAI `web_search` only** | No | Title/URL/snippet only | ~$0.01/call + tokens; already used in forge | Unknown host until allowlisted; no embeddable flag | Weak — docs/tutorials only |
| **C. `web_search` + `allowed_domains: ["youtube.com"]` then YouTube `videos.list`** | Partial | Stats only after ID extract + `videos.list` | Pay OpenAI **and** burn YouTube quota | Same as A once IDs known | Optional hybrid; usually worse than A alone |
| **D. No API — human/curated URLs** | N/A | Manual | $0 API | Same viewer rules | Ops fallback, not forge automation |

**Recommended default:** **A**, run **after** (or as a sibling step to) docs `research_enrich`, attach at most one Video Reference per Node when it passes the bar; official docs References still win when equal (glossary).

**During vs after forge:**

| Timing | Pros | Cons |
|---|---|---|
| During forge (4th research pass / parallel tool) | Timeline can show video hits | Couples SSE latency + search quota to every forge; confuses Forge source vs Reference |
| After plan / on Node attach | Quota = f(nodes kept); clearer product object | Extra backend step post-`graph_ready` |

Prefer **after** structured plan exists (query from node title + key_concepts), unless product wants timeline theater — still attach only as References, not as Forge sources (ADR-007 non-goal).

---

## 6. Suggested quality bar (product-tunable, API-backed)

Not locked by this research — example filters feasible with official fields:

1. `type=video` + `videoEmbeddable=true` + `safeSearch=strict`
2. Prefer `videoDuration=medium` (4–20 min) for lessons; allow `long` for deep dives; reject unclassified Shorts via exact `duration` after `videos.list` (e.g. discard &lt; 3 min)
3. `viewCount` ≥ product floor (e.g. 1k / 10k) — refresh or drop persisted counts ≤30 days if stored
4. Optional: captions required (`videoCaption=closedCaption`)
5. Optional: channel allowlist for BASE/PSP educators
6. Always keep Escape hatch; never auto-`done` on play

---

## Implementation notes for a follow-on issue (not done here)

1. New thin client e.g. `ai/tools/youtube_video_search.py` — do not fold into `openai_web_search.py`.
2. Env: `YOUTUBE_API_KEY` (server-only); document in `.env.example`.
3. Extend `StudyResource.source_type` (or parallel Video Reference DTO) — glossary term already exists.
4. Quota guard: one search per forge or per N nodes; cache query→video-id briefly; respect 30-day API Data rules for stats.
5. Reference viewer: hostname-specific referrer policy for YouTube; prove embed in operator queue before liberating.
6. Privacy/terms: YouTube ToS link for API Client surfaces that embed.
7. Do not download video bytes; do not scrape watch pages as a YouTube API substitute.

---

## Sources (primary only)

| Doc | URL |
|---|---|
| YouTube Search: list | https://developers.google.com/youtube/v3/docs/search/list |
| YouTube Videos: list | https://developers.google.com/youtube/v3/docs/videos/list |
| YouTube Videos resource (duration, stats, embeddable) | https://developers.google.com/youtube/v3/docs/videos |
| Quota Calculator | https://developers.google.com/youtube/v3/determine_quota_cost |
| Quota and Compliance Audits | https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits |
| Audit / Quota Extension Form | https://support.google.com/youtube/contact/yt_api_form |
| YouTube API Services ToS | https://developers.google.com/youtube/terms/api-services-terms-of-service |
| Developer Policies (storage, no A/V download) | https://developers.google.com/youtube/terms/developer-policies |
| Required Minimum Functionality (Referer, player) | https://developers.google.com/youtube/terms/required-minimum-functionality |
| Embed help (Referer / error 153) | https://support.google.com/youtube/answer/171780 |
| IFrame Player API | https://developers.google.com/youtube/iframe_api_reference |
| OpenAI Using tools | https://developers.openai.com/api/docs/guides/tools |
| OpenAI Web search (domain filters, image search) | https://developers.openai.com/api/docs/guides/tools-web-search |
| OpenAI Pricing (web search tool) | https://developers.openai.com/api/docs/pricing |
| ADR-007 Reference viewer | ../decisions/ADR-007-reference-viewer.md |
| CONTEXT — Video Reference / Escape hatch | ../../CONTEXT.md |
