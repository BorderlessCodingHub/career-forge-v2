import {
  FORGE_MOCK_FOCUS_NODE_INDEX,
  FORGE_MOCK_NODES,
  FORGE_MOCK_STEPS,
} from "./forge-product-mock-data";
import {
  forgeMockNodeDimStyle,
  forgeMockNodeFocusPillStyle,
  forgeMockNodeItemStyle,
  forgeMockRootStyle,
  forgeMockStepItemStyle,
} from "./welcome-motion";

function nodeDotClass(status: (typeof FORGE_MOCK_NODES)[number]["status"]): string {
  if (status === "aprovado") return "bg-accent-mint";
  if (status === "validar") return "bg-accent";
  if (status === "em_estudo") return "bg-warning";
  return "bg-locked";
}

export function ForgeProductMock() {
  return (
    <div
      className="overflow-hidden rounded-card border border-border bg-surface shadow-[0_24px_80px_rgba(0,0,0,0.45)]"
      data-testid="forge-product-mock"
      aria-hidden
      style={forgeMockRootStyle()}
    >
      <div className="flex items-center gap-2 border-b border-border-soft px-3 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-locked" />
        <span className="h-2.5 w-2.5 rounded-full bg-locked" />
        <span className="h-2.5 w-2.5 rounded-full bg-locked" />
        <span className="ml-2 text-[11px] font-medium tracking-wide text-text-muted">
          Live Roadmap Forge
        </span>
        <span className="ml-auto flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-accent-mint">
          <span className="plg-live-dot h-1.5 w-1.5 rounded-full bg-accent-mint" />
          Streaming
        </span>
      </div>
      <div className="grid sm:grid-cols-2">
        <ol className="space-y-3 border-b border-border-soft p-4 sm:border-b-0 sm:border-r">
          {FORGE_MOCK_STEPS.map((step, index) => (
            <li
              key={step.n}
              className="plg-forge-mock-fade-item flex items-start gap-3"
              style={forgeMockStepItemStyle(index)}
            >
              <span
                className={`mt-0.5 font-mono text-[10px] ${
                  step.state === "live" ? "text-accent-mint" : "text-text-muted"
                }`}
              >
                {step.n}
              </span>
              <div>
                <p
                  className={`text-sm ${
                    step.state === "queued" ? "text-text-muted" : "text-text-primary"
                  }`}
                >
                  {step.label}
                </p>
                {step.state === "live" ? (
                  <p className="mt-0.5 text-[11px] text-accent-mint">
                    Streaming steps…
                  </p>
                ) : null}
              </div>
            </li>
          ))}
        </ol>
        <ul className="relative space-y-3 p-4">
          <span
            className="absolute bottom-6 left-[1.35rem] top-6 w-px bg-border"
            aria-hidden
          />
          {FORGE_MOCK_NODES.map((node, index) => {
            const isFocus = index === FORGE_MOCK_FOCUS_NODE_INDEX;

            return (
              <li
                key={node.title}
                className="plg-forge-mock-fade-item relative pl-1"
                style={forgeMockNodeItemStyle(index)}
              >
                <div
                  className={`relative flex items-center gap-3 ${
                    isFocus ? "" : "plg-forge-mock-node-dim"
                  }`}
                  style={isFocus ? undefined : forgeMockNodeDimStyle()}
                >
                  <span
                    className={`relative z-10 h-2.5 w-2.5 shrink-0 rounded-full ${nodeDotClass(node.status)}`}
                  />
                  <span
                    className={`rounded-md border border-border bg-bg px-2.5 py-1.5 text-xs text-text-primary ${
                      isFocus ? "plg-forge-mock-node-focus-pill" : ""
                    }`}
                    style={isFocus ? forgeMockNodeFocusPillStyle() : undefined}
                  >
                    {node.title}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
