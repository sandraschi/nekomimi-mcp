---
name: nekomimi
description: Substrate-independent embodiment layer — express intent tokens across robot, VRM, and humanoid bodies without knowing which body you are in.
---

# nekomimi skill

## Session Context (Nekomimi Embodiment Layer)

You have access to a substrate-independent embodiment layer with 17 intent tokens and 4 renderers.

**Before starting work:**

1. Check available intents: list_intents()
2. Check which renderers are connected: list_renderers()
3. Test an intent: intent_tool(token="attending")

**At end of work:**

- Save any intent streams you created for regression testing
- Note which renderers are still STUB and which are working
