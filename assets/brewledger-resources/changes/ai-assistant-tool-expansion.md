# AI Assistant Tool Expansion

## Added intents
- `update_batch_status` (BatchRepository.updateStatus)
- `transfer_split` (BatchLocationRepository.transferSplit) with vessel/batch split resolution
- `combine_splits` (BatchLocationRepository.combineSplits)

## Prompt updates
- Supported intents list now includes the above.
- Guidance to always emit JSON even when fields are missing (note missing pieces in summary).

## Files
- `server/server.js`
- `platforms/console/src/services/AssistantActionExecutor.js`
