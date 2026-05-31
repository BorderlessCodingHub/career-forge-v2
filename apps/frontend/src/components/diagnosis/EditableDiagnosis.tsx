"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  closestCenter,
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui";
import { confirmDiagnosis, startForgeRunFromProfile } from "@/lib/api-client";
import { setForgeRunId } from "@/lib/forge-session";
import type { DiagnosisResponse } from "@/types/contracts";
import {
  clearStoredDiagnosis,
  getAnswers,
  getCvAttachment,
  getMotivation,
  getSelectedGoal,
  getStoredDiagnosis,
  getYearsXp,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";

type Tone = "strength" | "gap" | "priority";

const NODE_LABELS: Record<string, string> = {
  js: "JavaScript base",
  git: "Git e GitHub",
  http: "HTTP básico",
  db: "Banco relacional",
  rest: "APIs REST",
  auth: "Autenticação JWT",
  final: "Projeto: API CRUD",
};

function resolveLabel(value: string): string {
  return NODE_LABELS[value] ?? value;
}

const TONE_CLASSES: Record<Tone, string> = {
  strength: "border-success/20 bg-success/5",
  gap: "border-warning/20 bg-warning/5",
  priority: "border-accent/20 bg-accent/5",
};

const TONE_ITEM_CLASSES: Record<Tone, string> = {
  strength: "border-success/15",
  gap: "border-warning/15",
  priority: "border-accent/15",
};

function ViewItem({
  value,
  tone,
  onEdit,
  onDelete,
}: {
  value: string;
  tone: Tone;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      className={`flex items-center justify-between gap-3 rounded-md border px-3 py-2 ${TONE_ITEM_CLASSES[tone]}`}
    >
      <span className="text-sm text-text-primary">{value}</span>
      <div className="flex shrink-0 items-center gap-1">
        <button
          type="button"
          onClick={onEdit}
          className="rounded p-1 text-accent-mint transition hover:bg-accent-mint/10"
          aria-label="Editar"
        >
          <Pencil size={14} />
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="rounded p-1 text-red-500 transition hover:bg-red-500/10"
          aria-label="Excluir"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}

function EditItem({
  value,
  tone,
  onSave,
  onDiscard,
}: {
  value: string;
  tone: Tone;
  onSave: (value: string) => void;
  onDiscard: () => void;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [draft, setDraft] = useState(value);

  useEffect(() => {
    ref.current?.focus();
  }, []);

  const commit = () => {
    const trimmed = draft.trim();
    if (trimmed.length === 0) {
      onDiscard();
    } else {
      onSave(trimmed);
    }
  };

  return (
    <textarea
      ref={ref}
      className={`min-h-[72px] w-full resize-none rounded-md border px-3 py-2 text-sm text-text-primary outline-none ring-accent focus:ring-2 ${TONE_ITEM_CLASSES[tone]} bg-bg`}
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === "Escape") {
          e.preventDefault();
          if (value) {
            onSave(value);
          } else {
            onDiscard();
          }
        }
      }}
    />
  );
}

function EditableList({
  title,
  items,
  tone,
  onChange,
}: {
  title: string;
  items: string[];
  tone: Tone;
  onChange: (items: string[]) => void;
}) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [adding, setAdding] = useState(false);

  return (
    <div className={`rounded-md border p-5 ${TONE_CLASSES[tone]}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium uppercase tracking-wide text-text-secondary">
          {title}
        </h3>
        <span className="rounded-full bg-surface px-2 py-0.5 text-xs text-text-muted">
          {items.length}
        </span>
      </div>
      <div className="space-y-2">
        {items.map((item, index) =>
          editingIndex === index ? (
            <EditItem
              key={`${tone}-edit-${index}`}
              value={item}
              tone={tone}
              onSave={(val) => {
                const next = [...items];
                next[index] = val;
                onChange(next);
                setEditingIndex(null);
              }}
              onDiscard={() => {
                const next = items.filter((_, i) => i !== index);
                onChange(next);
                setEditingIndex(null);
              }}
            />
          ) : (
            <ViewItem
              key={`${tone}-view-${index}`}
              value={item}
              tone={tone}
              onEdit={() => setEditingIndex(index)}
              onDelete={() => {
                const next = items.filter((_, i) => i !== index);
                onChange(next);
              }}
            />
          ),
        )}
        {adding ? (
          <EditItem
            key={`${tone}-add-new`}
            value=""
            tone={tone}
            onSave={(val) => {
              onChange([...items, val]);
              setAdding(false);
            }}
            onDiscard={() => setAdding(false)}
          />
        ) : (
          <button
            type="button"
            onClick={() => setAdding(true)}
            className="flex w-full items-center justify-center gap-1.5 rounded-md border border-dashed border-accent/30 py-2 text-sm text-accent transition hover:bg-accent/5"
          >
            <Plus size={14} />
            Adicionar {tone === "strength" ? "ponto forte" : "lacuna"}
          </button>
        )}
      </div>
    </div>
  );
}

function SortableItem({ id, value }: { id: string; value: string }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 rounded-md border px-3 py-2 ${TONE_ITEM_CLASSES.priority} ${
        isDragging ? "z-10 shadow-lg" : ""
      }`}
    >
      <button
        type="button"
        className="cursor-grab touch-none text-accent-mint/50 hover:text-accent-mint active:cursor-grabbing"
        aria-label="Arrastar para reordenar"
        {...attributes}
        {...listeners}
      >
        <GripVertical size={14} />
      </button>
      <span className="text-sm text-text-primary">{resolveLabel(value)}</span>
    </div>
  );
}

function ReorderableList({
  title,
  items,
  onChange,
}: {
  title: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  const stableIdsRef = useRef<Map<string, string>>(new Map());
  const counterRef = useRef(0);

  const getStableId = (value: string): string => {
    const existing = stableIdsRef.current.get(value);
    if (existing) return existing;
    const id = `priority-${counterRef.current++}`;
    stableIdsRef.current.set(value, id);
    return id;
  };

  const ids = items.map(getStableId);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = ids.indexOf(active.id as string);
    const newIndex = ids.indexOf(over.id as string);
    onChange(arrayMove(items, oldIndex, newIndex));
  };

  return (
    <div className={`rounded-md border p-5 ${TONE_CLASSES.priority}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium uppercase tracking-wide text-text-secondary">
          {title}
        </h3>
        <span className="rounded-full bg-surface px-2 py-0.5 text-xs text-text-muted">
          {items.length}
        </span>
      </div>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={ids} strategy={verticalListSortingStrategy}>
          <div className="space-y-2">
            {items.map((item, index) => (
              <SortableItem
                key={ids[index]}
                id={ids[index]}
                value={item}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
      <p className="mt-3 text-center text-xs text-text-muted">
        Arraste para reordenar prioridades
      </p>
    </div>
  );
}

type EditableDiagnosisProps = {
  initialDiagnosis?: DiagnosisResponse | null;
};

export function EditableDiagnosis({ initialDiagnosis }: EditableDiagnosisProps) {
  const router = useRouter();
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(
    () => initialDiagnosis ?? getStoredDiagnosis(),
  );
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (diagnosis) return;
    const stored = getStoredDiagnosis();
    if (stored) {
      setDiagnosis(stored);
    } else {
      router.replace("/onboarding");
    }
  }, [diagnosis, router]);

  if (!diagnosis) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">Carregando diagnóstico…</p>
      </main>
    );
  }

  const updateDiagnosis = (patch: Partial<DiagnosisResponse>) => {
    setDiagnosis((current) => {
      if (!current) return current;
      const next = { ...current, ...patch };
      setStoredDiagnosis(next);
      return next;
    });
  };

  const handleConfirmAndForge = async () => {
    const goalId = getSelectedGoal();
    const motivation = getMotivation();
    if (!goalId || !motivation) {
      setError("Dados de onboarding incompletos. Refaça o diagnóstico.");
      return;
    }

    setConfirming(true);
    setError(null);
    try {
      await confirmDiagnosis({
        diagnosis,
        goal_id: goalId,
        motivation,
        years_xp: getYearsXp() ?? undefined,
        answers: getAnswers(),
        cv: getCvAttachment(),
      });
      const forge = await startForgeRunFromProfile();
      setForgeRunId(forge.run_id);
      router.push("/forge");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Falha ao confirmar diagnóstico ou iniciar o forge.",
      );
      setConfirming(false);
    }
  };

  const handleRestart = () => {
    clearStoredDiagnosis();
    router.push("/");
  };

  return (
    <main className="min-h-screen grid-dots px-4 py-10" data-testid="editable-diagnosis">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-sm text-text-secondary">
            <span className="h-2 w-2 rounded-full bg-accent-mint" />
            Perfil: <strong className="text-text-primary">{diagnosis.profile.label}</strong>
          </div>
          <h1 className="mt-4 text-4xl font-semibold text-text-primary">
            Seu diagnóstico
          </h1>
          <p className="mt-3 max-w-3xl text-text-secondary">
            Ajuste fortes, lacunas e prioridades antes de forjar sua trilha. Esta
            é a foto de hoje — ela recalibra a cada validação.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <EditableList
            title="Pontos fortes"
            tone="strength"
            items={diagnosis.strengths}
            onChange={(strengths) => updateDiagnosis({ strengths })}
          />
          <EditableList
            title="Lacunas"
            tone="gap"
            items={diagnosis.gaps}
            onChange={(gaps) => updateDiagnosis({ gaps })}
          />
          <ReorderableList
            title="Prioridades iniciais"
            items={diagnosis.starting_priorities}
            onChange={(starting_priorities) =>
              updateDiagnosis({ starting_priorities })
            }
          />
        </div>

        <div className="mt-6 rounded-md border border-border bg-surface p-5 text-sm text-text-secondary">
          <strong className="text-text-primary">Avaliação por evidência.</strong>{" "}
          Career Forge não deixa marcar tópicos como concluídos sem provar
          entendimento numa entrevista com a IA.
        </div>

        {error && (
          <p className="mt-6 rounded-md border border-danger/30 bg-danger/10 p-3 text-sm text-danger">
            {error}
          </p>
        )}

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Button variant="ghost" onClick={handleRestart} disabled={confirming}>
            Refazer diagnóstico
          </Button>
          <Button
            data-testid="generate-roadmap"
            onClick={() => void handleConfirmAndForge()}
            disabled={confirming}
          >
            {confirming ? "Salvando e iniciando forge…" : "Gerar roadmap →"}
          </Button>
        </div>
      </div>
    </main>
  );
}
