---
goal_id: agent-engineer
locale: en
---

An agent chooses a tool, runs it, and writes from the result.

## Choose the next tool

The model proposes a tool call. The runtime runs that tool and returns the observation. The next write uses that observation, not a guess about what the tool would have returned.
