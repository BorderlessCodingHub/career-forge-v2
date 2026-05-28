export function VerticalSpineSkeleton() {
  return (
    <div
      className="relative mx-auto max-w-3xl px-4 py-6"
      data-testid="vertical-spine-skeleton"
      aria-busy="true"
      aria-label="Carregando trilha"
    >
      <div
        className="absolute bottom-0 left-1/2 top-0 w-px -translate-x-1/2 bg-border/60"
        aria-hidden
      />
      <div className="space-y-12">
        {[0, 1].map((section) => (
          <div key={section} className="space-y-8">
            <div className="flex justify-center">
              <div className="h-7 w-32 animate-pulse rounded-full bg-surface" />
            </div>
            <ol className="space-y-8">
              {[0, 1, 2].map((row) => (
                <li
                  key={row}
                  className={`relative flex ${row % 2 === 0 ? "justify-start pr-[52%]" : "justify-end pl-[52%]"}`}
                >
                  <div
                    className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-border bg-bg"
                    aria-hidden
                  />
                  <div className="h-[88px] w-full max-w-[260px] animate-pulse rounded-node border border-border/60 bg-surface-node/40" />
                </li>
              ))}
            </ol>
          </div>
        ))}
      </div>
    </div>
  );
}
