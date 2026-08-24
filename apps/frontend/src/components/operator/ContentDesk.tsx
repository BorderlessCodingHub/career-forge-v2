"use client";

import { useEffect, useMemo, useState } from "react";
import { FileCheck2, FileX2, Search } from "lucide-react";

import { Button } from "@/components/ui";
import {
  getOperatorContentSkills,
  patchOperatorContentSkill,
  type OperatorContentPatch,
  type OperatorContentSkill,
} from "@/lib/operator-console";

type ContentFilter = "all" | "published" | "unpublished" | "body-missing";

function ContentSkillRow({
  skill,
  onUpdated,
}: {
  skill: OperatorContentSkill;
  onUpdated: (skill: OperatorContentSkill) => void;
}) {
  const [title, setTitle] = useState(skill.title);
  const [url, setUrl] = useState(skill.url ?? "");
  const [published, setPublished] = useState(skill.published);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTitle(skill.title);
    setUrl(skill.url ?? "");
    setPublished(skill.published);
  }, [skill]);

  const dirty =
    title !== skill.title || url !== (skill.url ?? "") || published !== skill.published;
  const invalidPublish = published && !skill.body_present;

  async function save() {
    const normalizedTitle = title.trim();
    if (!normalizedTitle) {
      setError("Title is required.");
      return;
    }
    setSaving(true);
    setError(null);
    const patch: OperatorContentPatch = {
      title: normalizedTitle,
      url: url.trim() || null,
      published,
    };
    try {
      onUpdated(await patchOperatorContentSkill(skill.skill_id, patch));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save this annotation.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <li
      className="rounded-card border border-border bg-surface p-4"
      data-testid={`operator-content-row-${skill.skill_id}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-accent-mint">{skill.skill_id}</p>
          <p className="mt-1 text-[11px] text-text-muted">{skill.track_id}</p>
          {skill.description ? (
            <p className="mt-2 text-xs text-text-secondary">{skill.description}</p>
          ) : null}
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${
            skill.body_present
              ? "border-accent-mint/40 bg-accent-mint/10 text-accent-mint"
              : "border-border bg-bg text-text-muted"
          }`}
          data-testid={`operator-content-body-${skill.skill_id}`}
        >
          {skill.body_present ? (
            <FileCheck2 className="h-3.5 w-3.5" aria-hidden="true" />
          ) : (
            <FileX2 className="h-3.5 w-3.5" aria-hidden="true" />
          )}
          {skill.body_present ? "Git body present" : "No git body"}
        </span>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(12rem,1fr)_minmax(14rem,1.3fr)_auto]">
        <label className="text-xs font-medium text-text-secondary">
          Title
          <input
            type="text"
            value={title}
            disabled={saving}
            maxLength={200}
            data-testid={`operator-content-title-${skill.skill_id}`}
            className="mt-1.5 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-mint"
            onChange={(event) => setTitle(event.target.value)}
          />
        </label>
        <label className="text-xs font-medium text-text-secondary">
          URL
          <input
            type="url"
            value={url}
            disabled={saving}
            placeholder="https://…"
            data-testid={`operator-content-url-${skill.skill_id}`}
            className="mt-1.5 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none placeholder:text-text-muted focus:border-accent-mint"
            onChange={(event) => setUrl(event.target.value)}
          />
        </label>
        <label className="flex items-center gap-2 self-end rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-secondary">
          <input
            type="checkbox"
            checked={published}
            disabled={saving || (!skill.body_present && !skill.published)}
            data-testid={`operator-content-published-${skill.skill_id}`}
            className="h-4 w-4 accent-accent-mint"
            onChange={(event) => setPublished(event.target.checked)}
          />
          Published
        </label>
      </div>

      {invalidPublish ? (
        <p className="mt-3 text-xs text-warning">
          Unpublish this item or add its canonical markdown body in git before saving.
        </p>
      ) : null}
      {error ? (
        <p className="mt-3 text-sm text-red-300" role="alert">
          {error}
        </p>
      ) : null}
      <div className="mt-4 flex justify-end">
        <Button
          variant="ghost"
          disabled={saving || !dirty || !title.trim() || invalidPublish}
          data-testid={`operator-content-save-${skill.skill_id}`}
          onClick={() => void save()}
        >
          {saving ? "Saving…" : "Save annotation"}
        </Button>
      </div>
    </li>
  );
}

export function ContentDesk() {
  const [skills, setSkills] = useState<OperatorContentSkill[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ContentFilter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOperatorContentSkills()
      .then(setSkills)
      .catch((cause) =>
        setError(cause instanceof Error ? cause.message : "Could not load Content desk."),
      )
      .finally(() => setLoading(false));
  }, []);

  const visibleSkills = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return skills.filter((skill) => {
      const matchesQuery =
        !normalized ||
        `${skill.skill_id} ${skill.track_id} ${skill.title}`
          .toLowerCase()
          .includes(normalized);
      const matchesFilter =
        filter === "all" ||
        (filter === "published" && skill.published) ||
        (filter === "unpublished" && !skill.published) ||
        (filter === "body-missing" && !skill.body_present);
      return matchesQuery && matchesFilter;
    });
  }, [filter, query, skills]);

  return (
    <section data-testid="operator-desk-content">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-mint">
        Content desk
      </p>
      <h2 className="mt-2 text-2xl font-semibold text-text-primary">Catalog annotations</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-text-secondary">
        Annotate existing catalog IDs with a title, URL, and publishing state. Git owns the
        markdown body; this desk never creates skill IDs.
      </p>

      <div className="mt-6 flex max-w-3xl flex-col gap-2 sm:flex-row">
        <label className="relative block min-w-0 flex-1">
          <span className="sr-only">Search catalog skills</span>
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted"
            aria-hidden="true"
          />
          <input
            type="search"
            value={query}
            data-testid="operator-content-search"
            placeholder="Filter by skill ID, track, or title"
            className="w-full rounded-md border border-border bg-surface py-2.5 pl-10 pr-3 text-sm text-text-primary outline-none placeholder:text-text-muted focus:border-accent-mint"
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <label>
          <span className="sr-only">Editorial queue filter</span>
          <select
            value={filter}
            data-testid="operator-content-filter"
            className="h-full min-h-10 rounded-md border border-border bg-surface px-3 text-sm text-text-primary outline-none focus:border-accent-mint"
            onChange={(event) => setFilter(event.target.value as ContentFilter)}
          >
            <option value="all">All content</option>
            <option value="published">Published</option>
            <option value="unpublished">Unpublished</option>
            <option value="body-missing">Body missing</option>
          </select>
        </label>
      </div>

      {error ? (
        <p
          className="mt-5 rounded-md border border-red-900 bg-red-950 px-3 py-2 text-sm text-red-200"
          role="alert"
          data-testid="operator-content-error"
        >
          {error}
        </p>
      ) : null}
      {loading ? (
        <div
          className="mt-6 h-36 animate-pulse rounded-card border border-border bg-surface"
          data-testid="operator-content-loading"
        />
      ) : (
        <>
          <p className="mt-5 text-xs text-text-muted">
            {visibleSkills.length} of {skills.length} catalog IDs
          </p>
          <ul className="mt-3 grid gap-3" data-testid="operator-content-list">
            {visibleSkills.map((skill) => (
              <ContentSkillRow
                key={skill.skill_id}
                skill={skill}
                onUpdated={(updated) =>
                  setSkills((current) =>
                    current.map((item) =>
                      item.skill_id === updated.skill_id ? updated : item,
                    ),
                  )
                }
              />
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
