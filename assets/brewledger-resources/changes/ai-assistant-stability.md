# AI Assistant Stability Fixes

## Issues
- Frequent “could not generate a response”.
- Malformed JSON/tool calls not parsed on frontend.

## Fixes
- Server: more robust action parsing (handles fenced code blocks and first object slice), returns parse errors; slightly higher max tokens and lower temperature to reduce truncation/drift.
- Client: displays action parse errors; message model now carries `actionError`.

## Files
- `server/server.js`
- `platforms/console/src/views/AIAssistant.vue`
- `platforms/console/src/services/AIAssistantService.js`
