# Auth pivot — email OTP (F3b)

> **Data:** 2026-08-20 · Pedro Alano  
> **Grill:** Career Forge IdP · Borderless membership only  
> **Linear:** [F3b — Email OTP auth + membership](https://linear.app/career-forge-v2/project/f3b-email-otp-auth-membership-53040eae6cbf) · epic [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)

---

## O que mudou

| Antes (CAR-28 antigo) | Agora |
|-----------------------|--------|
| Borderless **emite** JWT; Career Forge só valida | Career Forge **emite** JWT após OTP por e-mail |
| Bloqueado até doc do issuer + JWKS | Eng desbloqueado (stub membership); API Borderless só para label |
| Magic link local: fora | Magic **link** ainda fora; **código 6 dígitos** (estilo GitHub): **in** |

Identidade ≠ entitlement. Login prova e-mail. Membership / compra define o que a conta pode fazer.

---

## Decisões travadas

1. Career Forge = IdP permanente (não workaround até issuer).
2. Soft label `base | psp | external` após OTP válido.
3. Checagem Borderless **depois** do código (não antes do envio).
4. Anon até o 1º forge → upgrade obrigatório (e-mail novo = promote; e-mail existente = chooser).
5. Agora: sem paywall. Alvo: 1 forge grátis → paywall; BASE/PSP ativo = entitled; `external` = Stripe no Forge.
6. Dev: código no log. Prod: Resend/SES (não SMTP Borderless).

---

## Issues

| Issue | Escopo |
|-------|--------|
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic |
| [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) | OTP + upgrade pós-forge — **start** |
| [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) | Membership stub + client HTTP |
| [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) | Send resume por e-mail |
| [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) | Paywall Stripe (later) |

F3a (landing / pilotos) **não** depende disso.

---

## Pedido à plataforma (Yuri)

**Não precisamos mais** de contrato de issuer JWT / JWKS / audience.

**Precisamos só:**

```
GET …/members?email=<addr>
→ { "active": true|false, "program": "base"|"psp"|null }
```

+ token de serviço de staging.

Até existir: Career Forge usa allowlist/stub (CAR-45).

---

## Docs atualizados

- [ADR-003](../decisions/ADR-003-forge-recovery-auth-scaffold.md) amend 2026-08-20  
- [V2-PLAN](../V2-PLAN.md) Decision #1 + F3.6/F3.8/F3.13  
- [ROADMAP](../ROADMAP.md) / [STATUS](../STATUS.md) F3b  

---

_Handoff · Borderless Labs_
