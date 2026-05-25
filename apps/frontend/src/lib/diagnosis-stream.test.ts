import { describe, expect, it } from "vitest";

import {
  applyMappingDimensionEvent,
  isMappingItemDone,
  mergeMappingItem,
  mergeMappingProgress,
} from "@/lib/diagnosis-stream/state";
import type { RubricMapItem } from "@/types/contracts";

const baseItem = (overrides: Partial<RubricMapItem> = {}): RubricMapItem => ({
  rubric_key: "motivation_goal",
  label: "Objetivo",
  description: "Por que esse caminho",
  confidence: 0,
  saturated: false,
  status: "pending",
  note: "",
  ...overrides,
});

describe("mergeMappingItem", () => {
  it("keeps mapped status when incoming regresses to pending", () => {
    const previous = baseItem({
      status: "mapped",
      saturated: true,
      confidence: 0.85,
      note: "Motivação clara",
    });
    const incoming = baseItem({ status: "pending", confidence: 0.2, note: "" });

    const merged = mergeMappingItem(previous, incoming);
    expect(merged.status).toBe("mapped");
    expect(merged.saturated).toBe(true);
    expect(merged.note).toBe("Motivação clara");
  });

  it("upgrades pending to mapped from stream event", () => {
    const previous = baseItem({ status: "pending" });
    const incoming = baseItem({
      status: "mapped",
      saturated: true,
      confidence: 0.8,
      note: "Novo mapeamento",
    });

    const merged = mergeMappingItem(previous, incoming);
    expect(isMappingItemDone(merged)).toBe(true);
    expect(merged.note).toBe("Novo mapeamento");
  });
});

describe("applyMappingDimensionEvent", () => {
  it("accumulates done dimensions across events", () => {
    const items = [
      baseItem({ rubric_key: "motivation_goal" }),
      baseItem({ rubric_key: "hands_on_proof", label: "Prova prática" }),
    ];

    const afterMotivation = applyMappingDimensionEvent(items, {
      type: "mapping_dimension",
      index: 0,
      total: 5,
      item: baseItem({
        status: "mapped",
        saturated: true,
        confidence: 0.82,
        note: "Motivação mapeada",
      }),
    });

    const afterReplay = applyMappingDimensionEvent(afterMotivation, {
      type: "mapping_dimension",
      index: 0,
      total: 5,
      item: baseItem({ status: "pending", confidence: 0.1, note: "" }),
    });

    expect(afterReplay[0]?.status).toBe("mapped");
    expect(afterReplay[0]?.note).toBe("Motivação mapeada");
  });
});

describe("mergeMappingProgress", () => {
  it("merges full server snapshot without losing done chips", () => {
    const previous = [
      baseItem({
        status: "mapped",
        saturated: true,
        confidence: 0.9,
        note: "Done",
      }),
    ];
    const incoming = [
      baseItem({ status: "pending", confidence: 0, note: "" }),
    ];

    const merged = mergeMappingProgress(previous, incoming);
    expect(merged[0]?.status).toBe("mapped");
  });
});
