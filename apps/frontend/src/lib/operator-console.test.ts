import { afterEach, describe, expect, it, vi } from "vitest";

import {
  addOperatorPilotEmail,
  getOperatorContentSkills,
  getOperatorCostPool,
  getOperatorLearnerAccess,
  getOperatorLearnerAccessAudit,
  getOperatorPilotEmails,
  removeOperatorPilotEmail,
  patchOperatorContentSkill,
  patchOperatorLearnerAccess,
  visibleOperatorDesks,
  operatorApiUrl,
} from "./operator-console";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("operatorApiUrl", () => {
  it("keeps Operator cookie requests on the basePath origin", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    process.env.NEXT_PUBLIC_BACKEND_URL = "http://localhost:8000";

    expect(operatorApiUrl("/operator/me")).toBe("/career-forge/operator/me");
  });
});

describe("visibleOperatorDesks", () => {
  it("shows both desk rooms in their canonical order", () => {
    expect(visibleOperatorDesks(["content", "access"])).toEqual([
      { id: "access", label: "Access" },
      { id: "content", label: "Content" },
    ]);
  });

  it("hides desks outside the operator grant", () => {
    expect(visibleOperatorDesks(["content"])).toEqual([
      { id: "content", label: "Content" },
    ]);
    expect(visibleOperatorDesks(["access"])).toEqual([
      { id: "access", label: "Access" },
    ]);
  });
});

describe("Access desk API", () => {
  it("loads the read-only monthly cost pool", async () => {
    const body = {
      year_month: "2026-08",
      estimated_cost_brl: 187.4,
      budget_brl: 500,
      billable_runs: 12,
      forge_runs: 3,
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => body,
      }),
    );

    await expect(getOperatorCostPool()).resolves.toEqual(body);
    expect(fetch).toHaveBeenCalledWith(
      "/career-forge/operator/access/cost-pool",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("lists, adds, and removes normalized pilot emails", async () => {
    const pilot = {
      email: "pilot@example.com",
      created_at: "2026-08-25T12:00:00Z",
      created_by_operator_id: 7,
    };
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ emails: [pilot] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => pilot,
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 204,
        }),
    );

    await expect(getOperatorPilotEmails()).resolves.toEqual([pilot]);
    await expect(addOperatorPilotEmail(" Pilot@Example.com ")).resolves.toEqual(pilot);
    await expect(removeOperatorPilotEmail(" Pilot@Example.com ")).resolves.toBeUndefined();

    expect(fetch).toHaveBeenNthCalledWith(
      2,
      "/career-forge/operator/access/pilot-emails",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: " Pilot@Example.com " }),
      }),
    );
    expect(fetch).toHaveBeenNthCalledWith(
      3,
      "/career-forge/operator/access/pilot-emails/pilot%40example.com",
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  it("encodes learner emails and sends only the requested access patch", async () => {
    const learner = {
      email: "learner+pilot@example.com",
      operator_membership_label: "base" as const,
      membership_label: "base",
      membership_entitled: true,
      billing_entitled: false,
      pilot_email_listed: false,
      stripe_subscription_status: null,
      stripe_billing_locked: false,
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => learner,
      }),
    );

    await getOperatorLearnerAccess(learner.email);
    await patchOperatorLearnerAccess(learner.email, {
      operator_membership_label: "base",
    });

    expect(fetch).toHaveBeenNthCalledWith(
      1,
      "/career-forge/operator/access/learners/learner%2Bpilot%40example.com",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetch).toHaveBeenNthCalledWith(
      2,
      "/career-forge/operator/access/learners/learner%2Bpilot%40example.com",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ operator_membership_label: "base" }),
      }),
    );
  });

  it("returns the learner audit entries from the list envelope", async () => {
    const entries = [
      {
        id: 1,
        actor_type: "operator",
        operator_id: 7,
        actor_email: "operator@example.com",
        learner_email: "learner@example.com",
        field: "billing_entitled",
        before: false,
        after: true,
        action: "set",
        created_at: "2026-08-24T20:00:00Z",
      },
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ entries }),
      }),
    );

    await expect(getOperatorLearnerAccessAudit("learner@example.com")).resolves.toEqual(
      entries,
    );
  });
});

describe("Content desk API", () => {
  it("loads the catalog sidecar and sends metadata-only patches", async () => {
    const skill = {
      skill_id: "rag-retrieval",
      track_id: "rag-engineer-beginner",
      title: "Vector retrieval",
      description: "Index and top-k search",
      url: null,
      published: false,
      body_present: true,
    };
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ skills: [skill] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ ...skill, published: true }),
        }),
    );

    await expect(getOperatorContentSkills()).resolves.toEqual([skill]);
    await expect(
      patchOperatorContentSkill(skill.skill_id, { published: true }),
    ).resolves.toEqual({ ...skill, published: true });
    expect(fetch).toHaveBeenNthCalledWith(
      2,
      "/career-forge/operator/content/skills/rag-retrieval",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ published: true }),
      }),
    );
  });
});
