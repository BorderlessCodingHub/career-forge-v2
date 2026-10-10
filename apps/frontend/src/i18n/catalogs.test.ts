import { describe, expect, it } from "vitest";

import en from "../../messages/en.json";
import pt from "../../messages/pt-BR.json";
import { trackMessageKey } from "../lib/goal-copy";

function leafKeys(tree: Record<string, unknown>, prefix = ""): string[] {
  const keys: string[] = [];
  for (const [key, value] of Object.entries(tree)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value !== null && typeof value === "object") {
      keys.push(...leafKeys(value as Record<string, unknown>, path));
      continue;
    }
    keys.push(path);
  }
  return keys.sort();
}

describe("learner catalogs", () => {
  it("keeps every en key in pt-BR and every pt-BR key in en", () => {
    expect(leafKeys(pt)).toEqual(leafKeys(en));
  });

  it("locks the accepted pt-BR screen titles", () => {
    expect(pt.goal.title).toBe("Para onde você quer ir?");
    expect(pt.goal.trackRag).toBe("RAG de produção e recuperação avançada");
    expect(pt.goal.trackAgent).toBe("Engenharia de agentes");
    expect(pt.goal.trackEvals).toBe("Avaliação e observabilidade de LLM");
    expect(pt.goal.trackTune).toBe("Fine-tuning e alinhamento");
    expect(pt.diagnosis.yourGoal).toBe("Seu objetivo");
    expect(pt.diagnosis.mapping).toBe("O que a IA está mapeando");
    expect(pt.diagnosis.roundPractice).toBe("Prática e rotina");
    expect(pt.diagnosis.roundContext).toBe("Contexto e limites");
    expect(pt.diagnosis.dimMotivation).toBe("Objetivo");
    expect(pt.diagnosis.dimBackground).toBe("De onde você vem");
    expect(pt.diagnosis.dimVelocity).toBe("Ritmo de estudo");
    expect(pt.diagnosis.dimHandsOn).toBe("Prova prática");
    expect(pt.diagnosis.dimConstraints).toBe("Contexto real");
    expect(pt.diagnosis.yourDiagnosis).toBe("Seu diagnóstico");
    expect(pt.forge.eyebrow).toBe("Forge ao vivo");
    expect(pt.forge.title).toBe("Forjando sua trilha");
    expect(pt.forge.leanRoadmap).toBe("Trilha enxuta");
    expect(pt.forge.revealTitle).toBe("Sua trilha está pronta");
    expect(pt.assess.mockTitle).toBe("Entrevista simulada — validação profunda");
    expect(pt.mentor.drawerTitle).toBe("Mentor contextual");
    expect(pt.tutor.drawerTitle).toBe("Tutor do capítulo");
    expect(pt.report.eyebrow).toBe("Relatório Borderless");
    expect(pt.report.title).toBe("Evidências de aprendizado");
    expect(pt.paywall.eyebrow).toBe("Forge incluído esgotado");
    expect(pt.paywall.body).toBe(
      "Seu forge incluído acabou. USD $7/mês continua o Career Forge.",
    );
    expect(en.paywall.body).toContain("USD $7/mo");
    expect(en.paywall.body).not.toMatch(/R\$|BRL/);
  });

  it("maps a mentor-report English goal label onto the catalog track", () => {
    expect(trackMessageKey("Production RAG & Advanced Retrieval")).toBe("trackRag");
    expect(trackMessageKey("rag-engineer")).toBe("trackRag");
  });
});
