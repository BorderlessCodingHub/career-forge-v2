function SkeletonConnectorStub() {
  return (
    <div
      className="h-[2px] min-w-6 max-w-[120px] flex-1 bg-border/40"
      aria-hidden
    />
  );
}

function SkeletonSpineRow({ isLeft }: { isLeft: boolean }) {
  return (
    <li className="relative flex items-center">
      <div className="flex min-w-0 flex-1 items-center justify-end">
        {isLeft && (
          <>
            <div className="h-[88px] w-full max-w-[260px] animate-pulse rounded-node border border-border/60 bg-surface-node/40" />
            <SkeletonConnectorStub />
          </>
        )}
      </div>
      <div
        className="relative z-10 h-3 w-3 shrink-0 rounded-full border-2 border-border bg-bg"
        aria-hidden
      />
      <div className="flex min-w-0 flex-1 items-center justify-start">
        {!isLeft && (
          <>
            <SkeletonConnectorStub />
            <div className="h-[88px] w-full max-w-[260px] animate-pulse rounded-node border border-border/60 bg-surface-node/40" />
          </>
        )}
      </div>
    </li>
  );
}

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
                <SkeletonSpineRow key={row} isLeft={row % 2 === 0} />
              ))}
            </ol>
          </div>
        ))}
      </div>
    </div>
  );
}
