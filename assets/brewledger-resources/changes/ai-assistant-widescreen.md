# AI Assistant Widescreen Update (Desktop)

## Goal
- Make the console AI assistant feel like an interactive tool with more horizontal space, while retaining existing header/sidebar chrome.

## Changes
- Expanded the assistant page to full width within the content area, keeping sidebar/header.
- Taller container (`calc(100vh - 180px)`) and denser padding; badges indicating Interactive/Widescreen.
- Input footer uses subtle background to separate from scroll area; message bubbles gain light borders/shadows for tool-like affordance.

## Notes
- Routes/components unchanged; only `AIAssistant.vue` layout/styling updated.
