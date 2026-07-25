## Session Context (Nekomimi Embodiment Layer)

You have access to a substrate-independent embodiment layer with 17 intent tokens and 4 body renderers. The LLM emits ONLY intent tokens — never joint angles.

**Before starting work:**
1. Check available intents: list_intents()
2. Check connected renderers: list_renderers()
3. Express an emotion: intent_tool(token="attending")

**At end of work:**
- Save intent streams for regression testing via recordings_list()
