# AI Assistant Split-Pane + Tool Expansion

## Layout
- Chat column (left) narrowed; new right-hand Action History panel shows recent action runs with status and timestamps.
- Widescreen container retained with header/sidebar chrome; compact input/footer to save vertical space.

## Tooling
- Added `transfer_inventory` intent and handler (LedgerRepository.transfer) with location resolution and optional batch context.
- Action history captures the latest 20 runs; chat bubbles retain action cards and results are appended.

## Files
- `platforms/console/src/views/AIAssistant.vue`
- `platforms/console/src/services/AssistantActionExecutor.js`
- `server/server.js` (prompt supported intents list)
