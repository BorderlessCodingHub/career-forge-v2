import { MappingDimensionList } from "@/components/diagnosis/MappingDimensionList";
import { formatYearsXpLabel } from "@/lib/years-xp";
import type { CvAttachment, RubricDimensionKey, RubricMapItem, YearsXpRange } from "@/types/contracts";

type OnboardingRecapSidebarProps = {
  goalTitle: string;
  motivation: string;
  yearsXp: YearsXpRange;
  cvAttachment: CvAttachment | null;
  bootstrapping: boolean;
  streaming: boolean;
  streamPhaseLabel: string;
  roundCount: number;
  progressPct: number;
  mappingProgress: RubricMapItem[];
  activeKeys: Set<RubricDimensionKey>;
  analyzingKey: RubricDimensionKey | null;
};

export function OnboardingRecapSidebar({
  goalTitle,
  motivation,
  yearsXp,
  cvAttachment,
  bootstrapping,
  streaming,
  streamPhaseLabel,
  roundCount,
  progressPct,
  mappingProgress,
  activeKeys,
  analyzingKey,
}: OnboardingRecapSidebarProps) {
  return (
    <aside className="rounded-md border border-border bg-surface p-6">
      <div className="text-xs uppercase tracking-wide text-text-muted">
        Seu sonho
      </div>
      <div className="mt-3 text-lg font-medium text-text-primary">{goalTitle}</div>
      <p className="mt-3 text-sm leading-relaxed text-text-secondary">{motivation}</p>

      <dl className="mt-4 space-y-2 border-t border-border-soft pt-4 text-sm">
        <div className="flex justify-between gap-3">
          <dt className="text-text-muted">Experiência</dt>
          <dd className="text-text-primary">{formatYearsXpLabel(yearsXp)}</dd>
        </div>
        {cvAttachment && (
          <div className="flex justify-between gap-3">
            <dt className="text-text-muted">Currículo</dt>
            <dd className="truncate text-text-primary" title={cvAttachment.filename}>
              {cvAttachment.filename}
            </dd>
          </div>
        )}
      </dl>

      {!bootstrapping && roundCount > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between text-xs text-text-muted">
            <span>Perfil completo</span>
            <span>{progressPct}%</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-elevated">
            <div
              className="h-full rounded-full bg-brand-ribbon transition-all"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      )}

      <div className="mt-6">
        <div className="text-xs uppercase tracking-wide text-text-muted">
          O que a IA está mapeando
        </div>
        {streaming && (
          <p className="mt-1 flex items-center gap-2 text-xs text-accent">
            <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
            {streamPhaseLabel}
          </p>
        )}
        <MappingDimensionList
          items={mappingProgress}
          activeKeys={activeKeys}
          analyzingKey={analyzingKey}
          streaming={streaming}
        />
      </div>
    </aside>
  );
}
