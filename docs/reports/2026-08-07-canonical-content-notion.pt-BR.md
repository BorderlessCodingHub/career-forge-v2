# Notion — Conteúdo canônico por skill (resposta ao Yuri)

> **Uso:** colar no Notion (thread do handoff / pergunta do vídeo).  
> **ADR:** [ADR-004](../decisions/ADR-004-canonical-skill-content.md) · 2026-08-07  
> **Idioma:** pt-BR

---

## Colar abaixo

```text
Assunto: Career Forge — Conteúdos do forge × blog/plataforma (reuso)

Pergunta (Yuri)
- Forges de rag-engineer (e outros goals) são específicos por aluno.
- Dá para usar IA para escrever isso no blog/plataforma?
- 3 alunos no mesmo path → outputs diferentes → conteúdos infinitos?
- Relação é 1-N? Como faríamos?

Resposta (decisão)
Não publicamos um post por forge. Publicamos conteúdo canônico por skill.

1) Sim — 3 alunos em rag-engineer podem ter forges diferentes
   (diagnóstico, gaps, ordem, ênfase). Isso muda o GRAFO, não a fábrica de blog.

2) Relação de publish: N:1 (muitos alunos → 1 conteúdo por skill)
   — não 1 forge → N posts.
   Unidade: skill_id (ex. chunking). Piloto: 1 matéria canônica por skill.

3) Como faríamos
   Offline (agora / editorial)
   - Rodar forges sintéticos dos 4 goals.
   - Decidir manualmente quais skills merecem deep-dive.
   - Escrever/aprovar o canônico (teach/Cursor fora do produto ok).
   - Guardar inventário estável (repo: data/canonical/{skill_id}.md).

   Online (aluno real)
   - Forge NÃO gera post.
   - Se o nó for foco (must-have ou gap) E existir canônico → referencia.
   - Se não existir → silêncio (sem placeholder).
   - Nó guarda só a ref (skill_id); UI resolve título/URL atuais.

4) Blog / SEO
   - Piloto: superfície no produto.
   - Depois: o mesmo markdown pode ir ao blog (URL estável por skill).
   - Google indexa canônicos curados — não artifacts pessoais de forge.
   - Evita “conteúdo infinito” e diluição de indexação na plataforma.

5) “A IA decide se vale apontar?”
   - No piloto: regra + lookup (determinístico), não juízo livre no attach.
   - A IA continua montando o grafo; o link é política de produto.

Lock: ADR-004 (repo) · grill 2026-08-07
Ack Yuri (opcional): OK | perguntas — <data>
```

---

## Versão curta (comentário / Slack)

```text
Forges diferentes ≠ posts infinitos. Canônico = 1 por skill (N alunos → 1 conteúdo).
Geramos offline a partir de forges sintéticos; no aluno só linkamos se foco + canônico existe.
Blog depois espelha o mesmo markdown. Detalhe: ADR-004.
```
