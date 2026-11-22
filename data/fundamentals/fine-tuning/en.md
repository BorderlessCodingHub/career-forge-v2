---
goal_id: fine-tuning
locale: en
---

Fine-tuning changes the weights. It does not replace a missing fact in the prompt.

## Tune only what the prompt cannot hold

A behavior that must hold on every request, and that the prompt cannot state reliably, is a candidate for a weight update. A fact that changes next week stays in retrieval.
