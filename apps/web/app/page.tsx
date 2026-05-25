const apiUrl =
  process.env.API_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

type HealthResponse = {
  status: string;
  service: string;
  database?: string;
};

async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${apiUrl}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const health = await fetchHealth();

  return (
    <main className="min-h-screen grid-dots">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
        <div className="mb-8 inline-flex w-fit items-center gap-2 rounded-full border border-border bg-surface px-4 py-1.5 text-sm text-text-secondary">
          <span className="h-2 w-2 rounded-full bg-brand-ribbon" />
          Borderless BASE 01/2026
        </div>

        <h1 className="max-w-3xl text-5xl font-semibold tracking-tight md:text-6xl">
          <span className="bg-brand-ribbon bg-clip-text text-transparent">
            Career Forge
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-text-secondary md:text-xl">
          Aprender com validação prática — trilha viva para quem está virando
          dev. Diagnóstico, Live Roadmap Forge e mastery por IA.
        </p>

        <div className="mt-10 flex flex-wrap gap-4">
          <span className="rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white">
            Em construção
          </span>
          <span className="rounded-lg border border-border bg-surface px-5 py-2.5 text-sm text-text-secondary">
            Next.js · FastAPI · PostgreSQL
          </span>
        </div>

        <section className="mt-12 rounded-xl border border-border bg-surface p-6">
          <h2 className="text-sm font-medium uppercase tracking-wide text-text-muted">
            Stack status
          </h2>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-text-muted">Frontend</dt>
              <dd className="text-text-primary">apps/web — Next.js 14 App Router</dd>
            </div>
            <div>
              <dt className="text-text-muted">API</dt>
              <dd className="text-text-primary">
                {health
                  ? `${health.service} · ${health.status}${
                      health.database ? ` · db ${health.database}` : ""
                    }`
                  : "Offline — rode docker compose up"}
              </dd>
            </div>
          </dl>
        </section>
      </div>
    </main>
  );
}
