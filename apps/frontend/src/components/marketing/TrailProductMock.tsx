import {
  FORGE_MOCK_FOCUS_NODE_INDEX,
  TRAIL_MOCK_NODES,
} from "./forge-product-mock-data";

function TrailMockCard({
  title,
  body,
  selected,
}: {
  title: string;
  body: string;
  selected: boolean;
}) {
  return (
    <div
      className={`w-full max-w-[260px] rounded-node border px-4 py-3 ${
        selected
          ? "border-accent bg-surface-node/90 shadow-[0_0_24px_var(--accent-glow)]"
          : "border-accent/35 bg-surface-node/70"
      }`}
    >
      <p className="text-sm font-semibold text-text-primary">{title}</p>
      <p className="mt-1 line-clamp-2 text-xs text-text-secondary">{body}</p>
    </div>
  );
}

export function TrailProductMock() {
  return (
    <div
      className="relative mx-auto max-w-3xl"
      data-testid="trail-product-mock"
      aria-hidden
    >
      <div
        className="absolute bottom-2 left-1/2 top-2 w-px -translate-x-1/2 bg-border"
        aria-hidden
      />
      <ol className="space-y-8">
        {TRAIL_MOCK_NODES.map((node, index) => {
          const selected = index === FORGE_MOCK_FOCUS_NODE_INDEX;
          const isLeft = node.side === "left";

          return (
            <li key={node.title} className="relative flex items-center">
              <div className="flex min-w-0 flex-1 items-center justify-end">
                {isLeft ? (
                  <>
                    <TrailMockCard
                      title={node.title}
                      body={node.body}
                      selected={selected}
                    />
                    <span
                      className={`h-[2px] min-w-6 max-w-[120px] flex-1 ${
                        selected ? "bg-accent-mint" : "bg-border"
                      }`}
                    />
                  </>
                ) : null}
              </div>
              <span
                className={`relative z-10 h-3 w-3 shrink-0 rounded-full border-2 ${
                  selected
                    ? "border-accent-mint bg-accent shadow-[0_0_12px_var(--mint-glow)]"
                    : "border-border bg-bg"
                }`}
              />
              <div className="flex min-w-0 flex-1 items-center justify-start">
                {!isLeft ? (
                  <>
                    <span
                      className={`h-[2px] min-w-6 max-w-[120px] flex-1 ${
                        selected ? "bg-accent-mint" : "bg-border"
                      }`}
                    />
                    <TrailMockCard
                      title={node.title}
                      body={node.body}
                      selected={selected}
                    />
                  </>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
