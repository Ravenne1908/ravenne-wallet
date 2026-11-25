# Contributing

## Ground rules

- This software signs transactions. **No crypto improvisation.**
  Any change to key derivation, encryption, PSBT building, change addresses
  or signing must come with tests.
- Keep the UI monochrome (green/yellow status only), English, left-aligned.
- One entry point: `ravenne.js`. Do not add launcher scripts.

## Workflow

```powershell
npm ci
npm test
node --check ravenne.js
```

Before opening a PR:

1. `npm test` passes (15+ tests).
2. `node --check ravenne.js` passes.
3. New features have at least one test (pure helpers are exported through
   `_internals`).
4. The README/manuals are updated when commands change.

## Security-sensitive changes

Open an issue first for anything touching:

- master password / Argon2id / vault format,
- gate lockout / 2FA / duress,
- BTC PSBT, change derivation, coin control,
- broadcasting or proxy handling.

Include a short threat-model note: what leaks before, what leaks after.
