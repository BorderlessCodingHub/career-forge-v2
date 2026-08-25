"use client";

import { useEffect, useState, type FormEvent } from "react";
import { LockKeyhole, Plus, Search, Trash2 } from "lucide-react";

import { Button } from "@/components/ui";
import {
  addOperatorPilotEmail,
  getOperatorCostPool,
  getOperatorLearnerAccess,
  getOperatorLearnerAccessAudit,
  getOperatorPilotEmails,
  patchOperatorLearnerAccess,
  removeOperatorPilotEmail,
  type OperatorAccessAuditEntry,
  type OperatorAccessPatch,
  type OperatorCostPool,
  type OperatorLearnerAccess,
  type OperatorPilotEmail,
} from "@/lib/operator-console";

function formatBrl(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

function formatAuditValue(value: unknown): string {
  if (value === null || value === undefined) return "cleared";
  if (typeof value === "boolean") return value ? "granted" : "revoked";
  return String(value);
}

function CostStrip({
  pool,
  error,
}: {
  pool: OperatorCostPool | null;
  error: string | null;
}) {
  if (error) {
    return (
      <section
        className="rounded-card border border-warning/40 bg-warning/10 px-4 py-3"
        data-testid="operator-cost-strip-error"
        role="status"
      >
        <p className="text-xs font-medium text-warning">Cost pool unavailable</p>
        <p className="mt-1 text-xs text-text-secondary">{error}</p>
      </section>
    );
  }

  if (!pool) {
    return (
      <div
        className="h-[4.5rem] animate-pulse rounded-card border border-border bg-surface"
        data-testid="operator-cost-strip-loading"
      />
    );
  }

  const percentage =
    pool.budget_brl > 0 ? Math.round((pool.estimated_cost_brl / pool.budget_brl) * 100) : 0;
  const width = Math.min(100, Math.max(0, percentage));

  return (
    <section
      className="rounded-card border border-border bg-surface px-4 py-3"
      data-testid="operator-cost-strip"
      aria-label="Monthly cost pool"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div>
          <span className="font-medium text-text-primary">Cost this month</span>
          <span className="ml-2 text-text-muted">read-only · {pool.year_month}</span>
        </div>
        <span className="font-mono text-text-primary">
          {formatBrl(pool.estimated_cost_brl)} / {formatBrl(pool.budget_brl)} ({percentage}%)
        </span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-bg">
        <div className="h-full rounded-full bg-accent-mint" style={{ width: `${width}%` }} />
      </div>
      <p className="mt-2 text-[11px] text-text-muted">
        {pool.billable_runs} billable runs · {pool.forge_runs} forge runs
      </p>
    </section>
  );
}

function AccessFact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[10px] font-semibold uppercase tracking-[0.14em] text-text-muted">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-text-primary">{value}</dd>
    </div>
  );
}

function PilotListBadge({ testId }: { testId?: string }) {
  return (
    <span
      className="inline-flex rounded-full border border-accent/50 bg-accent/15 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-accent-mint"
      data-testid={testId}
    >
      pilot list
    </span>
  );
}

function PilotEmailPanel({
  emails,
  loading,
  saving,
  error,
  onAdd,
  onRemove,
}: {
  emails: OperatorPilotEmail[];
  loading: boolean;
  saving: boolean;
  error: string | null;
  onAdd: (email: string) => Promise<boolean>;
  onRemove: (email: string) => Promise<void>;
}) {
  const [email, setEmail] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = email.trim();
    if (!normalized) return;
    if (await onAdd(normalized)) setEmail("");
  }

  return (
    <section
      className="rounded-card border border-border bg-surface p-5 sm:p-6"
      data-testid="operator-pilot-email-panel"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-text-primary">Pilot billing emails</h3>
            <PilotListBadge />
          </div>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-text-secondary">
            These emails bypass checkout for pilots. Removing one only revokes this shortcut;
            it does not change the learner&apos;s billing entitlement.
          </p>
        </div>
        <span className="font-mono text-xs text-text-muted">{emails.length} listed</span>
      </div>

      <form className="mt-4 flex max-w-2xl gap-2" onSubmit={submit}>
        <label className="sr-only" htmlFor="operator-pilot-email">
          Pilot email
        </label>
        <input
          id="operator-pilot-email"
          type="email"
          value={email}
          disabled={saving}
          autoComplete="off"
          data-testid="operator-pilot-email-input"
          className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2.5 text-sm text-text-primary outline-none placeholder:text-text-muted focus:border-accent-mint"
          placeholder="pilot@example.com"
          onChange={(event) => setEmail(event.target.value)}
        />
        <Button type="submit" disabled={saving || !email.trim()} data-testid="operator-pilot-email-add">
          <Plus className="mr-1.5 h-4 w-4" aria-hidden="true" />
          Add email
        </Button>
      </form>

      {error ? (
        <p
          className="mt-3 max-w-2xl rounded-md border border-red-900 bg-red-950 px-3 py-2 text-sm text-red-200"
          role="alert"
          data-testid="operator-pilot-email-error"
        >
          {error}
        </p>
      ) : null}

      {loading ? (
        <div
          className="mt-4 h-16 animate-pulse rounded-md border border-border-soft bg-bg"
          data-testid="operator-pilot-email-loading"
        />
      ) : emails.length ? (
        <ul className="mt-4 divide-y divide-border-soft border-y border-border-soft">
          {emails.map((item) => (
            <li
              key={item.email}
              className="flex flex-wrap items-center justify-between gap-3 py-3"
              data-testid={`operator-pilot-email-${item.email}`}
            >
              <div className="flex min-w-0 items-center gap-2">
                <span className="truncate text-sm text-text-primary">{item.email}</span>
                <PilotListBadge testId={`operator-pilot-badge-${item.email}`} />
              </div>
              <button
                type="button"
                disabled={saving}
                className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                data-testid={`operator-pilot-email-remove-${item.email}`}
                onClick={() => void onRemove(item.email)}
              >
                <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-text-muted" data-testid="operator-pilot-email-empty">
          No pilot billing emails listed.
        </p>
      )}
    </section>
  );
}

function AccessCard({
  learner,
  audit,
  saving,
  onPatch,
}: {
  learner: OperatorLearnerAccess;
  audit: OperatorAccessAuditEntry[];
  saving: boolean;
  onPatch: (patch: OperatorAccessPatch) => Promise<void>;
}) {
  const effectivelyEntitled =
    learner.membership_entitled ||
    learner.billing_entitled ||
    learner.pilot_email_listed ||
    learner.stripe_billing_locked;
  const membershipOptions: Array<{
    label: string;
    value: "base" | "psp" | null;
    testId: string;
  }> = [
    { label: "Borderless source", value: null, testId: "operator-membership-clear" },
    { label: "Override BASE", value: "base", testId: "operator-membership-base" },
    { label: "Override PSP", value: "psp", testId: "operator-membership-psp" },
  ];

  return (
    <section
      className="rounded-card border border-border bg-surface p-5 sm:p-6"
      data-testid="operator-access-card"
    >
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border-soft pb-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-accent-mint">
            Access card
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <h3 className="break-all text-lg font-semibold text-text-primary">{learner.email}</h3>
            {learner.pilot_email_listed ? (
              <PilotListBadge testId="operator-access-pilot-badge" />
            ) : null}
          </div>
        </div>
        <span
          className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
            effectivelyEntitled
              ? "border-accent-mint/40 bg-accent-mint/10 text-accent-mint"
              : "border-border bg-bg text-text-secondary"
          }`}
        >
          {effectivelyEntitled ? "Entitled" : "Not entitled"}
        </span>
      </div>

      <dl className="grid gap-4 border-b border-border-soft py-5 sm:grid-cols-2 lg:grid-cols-4">
        <AccessFact label="Membership" value={learner.membership_label} />
        <AccessFact
          label="Membership source"
          value={learner.operator_membership_label ? "Operator override" : "Borderless"}
        />
        <AccessFact
          label="Membership entitled"
          value={learner.membership_entitled ? "Yes" : "No"}
        />
        <AccessFact
          label="Billing entitled"
          value={learner.billing_entitled ? "Yes" : "No"}
        />
      </dl>

      <div className="grid gap-6 border-b border-border-soft py-5 lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
            Membership override
          </p>
          <p className="mt-1 text-xs leading-5 text-text-secondary">
            Clear the override to resume the Borderless membership source.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {membershipOptions.map((option) => {
              const active = learner.operator_membership_label === option.value;
              return (
                <button
                  key={option.testId}
                  type="button"
                  aria-pressed={active}
                  disabled={saving || active}
                  data-testid={option.testId}
                  className={`rounded-md border px-3 py-2 text-xs font-medium transition disabled:cursor-not-allowed ${
                    active
                      ? "border-accent bg-accent/20 text-text-primary"
                      : "border-border bg-bg text-text-secondary hover:border-accent"
                  } disabled:opacity-60`}
                  onClick={() =>
                    void onPatch({ operator_membership_label: option.value })
                  }
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
            Billing entitlement
          </p>
          {learner.stripe_billing_locked ? (
            <div
              className="mt-3 flex gap-2 rounded-md border border-warning/40 bg-warning/10 p-3 text-xs leading-5 text-warning"
              data-testid="operator-stripe-lock"
            >
              <LockKeyhole className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <span>
                Stripe subscription is {learner.stripe_subscription_status}. Billing is
                read-only here.
              </span>
            </div>
          ) : (
            <Button
              variant="ghost"
              className="mt-3"
              disabled={saving}
              data-testid="operator-billing-toggle"
              onClick={() =>
                void onPatch({ billing_entitled: !learner.billing_entitled })
              }
            >
              {learner.billing_entitled
                ? "Revoke billing entitlement"
                : "Grant billing entitlement"}
            </Button>
          )}
        </div>
      </div>

      <div className="pt-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
          Audit trail
        </p>
        {audit.length ? (
          <ol className="mt-3 space-y-2" data-testid="operator-access-audit">
            {audit.map((entry) => (
              <li
                key={entry.id}
                className="rounded-md border border-border-soft bg-bg px-3 py-2 text-xs"
              >
                <p className="font-mono text-text-secondary">
                  {entry.field}: {formatAuditValue(entry.before)} →{" "}
                  {formatAuditValue(entry.after)}
                </p>
                <p className="mt-1 text-[11px] text-text-muted">
                  {entry.actor_email ?? entry.actor_type} ·{" "}
                  {new Date(entry.created_at).toLocaleString("en-GB", {
                    dateStyle: "medium",
                    timeStyle: "short",
                    timeZone: "UTC",
                  })}{" "}
                  UTC
                </p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="mt-3 text-sm text-text-muted" data-testid="operator-access-audit-empty">
            No access changes recorded for this learner.
          </p>
        )}
      </div>
    </section>
  );
}

export function AccessDesk() {
  const [pool, setPool] = useState<OperatorCostPool | null>(null);
  const [poolError, setPoolError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [pilotEmails, setPilotEmails] = useState<OperatorPilotEmail[]>([]);
  const [pilotLoading, setPilotLoading] = useState(true);
  const [pilotSaving, setPilotSaving] = useState(false);
  const [pilotError, setPilotError] = useState<string | null>(null);
  const [learner, setLearner] = useState<OperatorLearnerAccess | null>(null);
  const [audit, setAudit] = useState<OperatorAccessAuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOperatorCostPool()
      .then(setPool)
      .catch((cause) =>
        setPoolError(
          cause instanceof Error ? cause.message : "Could not load the cost pool.",
        ),
      );
  }, []);

  useEffect(() => {
    getOperatorPilotEmails()
      .then(setPilotEmails)
      .catch((cause) =>
        setPilotError(
          cause instanceof Error ? cause.message : "Could not load pilot billing emails.",
        ),
      )
      .finally(() => setPilotLoading(false));
  }, []);

  async function addPilotEmail(email: string) {
    setPilotSaving(true);
    setPilotError(null);
    try {
      const added = await addOperatorPilotEmail(email);
      setPilotEmails((current) => [
        ...current.filter((item) => item.email !== added.email),
        added,
      ]);
      setLearner((current) =>
        current?.email === added.email ? { ...current, pilot_email_listed: true } : current,
      );
      return true;
    } catch (cause) {
      setPilotError(cause instanceof Error ? cause.message : "Could not add pilot email.");
      return false;
    } finally {
      setPilotSaving(false);
    }
  }

  async function removePilotEmail(email: string) {
    setPilotSaving(true);
    setPilotError(null);
    try {
      await removeOperatorPilotEmail(email);
      setPilotEmails((current) => current.filter((item) => item.email !== email));
      setLearner((current) =>
        current?.email === email ? { ...current, pilot_email_listed: false } : current,
      );
    } catch (cause) {
      setPilotError(cause instanceof Error ? cause.message : "Could not remove pilot email.");
    } finally {
      setPilotSaving(false);
    }
  }

  async function lookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const email = query.trim();
    if (!email) {
      setError("Enter a learner email.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [nextLearner, nextAudit] = await Promise.all([
        getOperatorLearnerAccess(email),
        getOperatorLearnerAccessAudit(email),
      ]);
      setLearner(nextLearner);
      setAudit(nextAudit);
      setQuery(nextLearner.email);
    } catch (cause) {
      setLearner(null);
      setAudit([]);
      setError(cause instanceof Error ? cause.message : "Could not find that learner.");
    } finally {
      setLoading(false);
    }
  }

  async function updateAccess(patch: OperatorAccessPatch) {
    if (!learner) return;
    setSaving(true);
    setError(null);
    try {
      const nextLearner = await patchOperatorLearnerAccess(learner.email, patch);
      const nextAudit = await getOperatorLearnerAccessAudit(learner.email);
      setLearner(nextLearner);
      setAudit(nextAudit);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not update learner access.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section data-testid="operator-desk-access">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-mint">
        Access desk
      </p>
      <h2 className="mt-2 text-2xl font-semibold text-text-primary">Learner access</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-text-secondary">
        Look up a learner by email, manage audited access grants, and inspect the
        read-only monthly cost pool.
      </p>

      <div className="mt-6">
        <CostStrip pool={pool} error={poolError} />
      </div>

      <div className="mt-6 max-w-4xl">
        <PilotEmailPanel
          emails={pilotEmails}
          loading={pilotLoading}
          saving={pilotSaving}
          error={pilotError}
          onAdd={addPilotEmail}
          onRemove={removePilotEmail}
        />
      </div>

      <form className="mt-6 flex max-w-2xl gap-2" onSubmit={lookup}>
        <label className="sr-only" htmlFor="operator-learner-email">
          Learner email
        </label>
        <div className="relative min-w-0 flex-1">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted"
            aria-hidden="true"
          />
          <input
            id="operator-learner-email"
            type="email"
            value={query}
            disabled={loading || saving}
            autoComplete="off"
            data-testid="operator-learner-email"
            className="w-full rounded-md border border-border bg-surface py-2.5 pl-10 pr-3 text-sm text-text-primary outline-none placeholder:text-text-muted focus:border-accent-mint"
            placeholder="learner@example.com"
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <Button
          type="submit"
          disabled={loading || saving}
          data-testid="operator-learner-lookup"
        >
          {loading ? "Looking up…" : "Find learner"}
        </Button>
      </form>

      {error ? (
        <p
          className="mt-3 max-w-2xl rounded-md border border-red-900 bg-red-950 px-3 py-2 text-sm text-red-200"
          role="alert"
          data-testid="operator-access-error"
        >
          {error}
        </p>
      ) : null}

      <div className="mt-6 max-w-4xl">
        {learner ? (
          <AccessCard
            learner={learner}
            audit={audit}
            saving={saving}
            onPatch={updateAccess}
          />
        ) : (
          <div
            className="rounded-card border border-dashed border-border bg-surface p-6"
            data-testid="operator-access-empty"
          >
            <p className="text-sm font-medium text-text-primary">No Access card open</p>
            <p className="mt-1 text-sm text-text-muted">
              Search an email to inspect membership, billing, Stripe lock, and audit.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
