# Master Password for Admin Testing

## Summary

Added `MASTER_PASSWORD` env var support to the login flow. When set, any user account can be logged into using that user's email and the master password instead of their real password.

## Implementation

- **server/server.js**: In `POST /api/auth/login`, added check: if `MASTER_PASSWORD` is set and the submitted password matches it, treat as valid; otherwise use normal bcrypt compare.
- **analysis.md**: Documented `MASTER_PASSWORD` in Secret Management (env vars) and Authentication Key Features.

## Usage

1. Add `MASTER_PASSWORD=your-secret` to `.env`
2. Restart server
3. On login page: enter any user's email + master password

## Security

- Do not set in production unless explicitly desired
- Keep in `.env` only; never commit
