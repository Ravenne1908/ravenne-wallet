# Ravenne Wallet v9.10.0 — icons, boot animation, adaptive theme

## Interface

- **Monochrome icons** on every main option (single-width glyphs, no emoji
  that breaks alignment): receive, send, verify, forward, swap, hop, wallets,
  history, Bitcoin, Monero, privacy, settings, security, advanced, vault,
  refresh, quit.
- Icons also added to Settings categories/submenus, the Security menu and the
  Advanced categories.
- **Launch animation** (TTY only): wordmark reveal, then vault/wallet/chain/
  terminal/background/tunnel lines. Can be disabled in
  **Settings → Wallet & display → Launch animation**.
- **Automatic light/dark theme detection** via OSC 11:
  - asks the terminal for its background color and adapts green/yellow/gray,
  - **never paints a background**, so a Windows Terminal background image
    stays visible,
  - override with `--theme light|dark`, `RAVENNE_THEME=`, or
    **Settings → Wallet & display → Theme**.
- Boot screen shows whether you are in **Windows Terminal** and the detected
  background (light/dark).

## Reliability checks

- New test: menu geometry at 120×40, 80×30, 60×24, 44×20, 40×14 — every line
  has the expected width and the panel fits the height.
- New test: background luminance → light/dark.
- `npm test`: **17/17**.
- `node --check`: OK.

## Known advisory (not a code bug)

`npm audit` reports a critical advisory in `form-data` pulled by
`monero-javascript → request`. There is **no upstream fix**. Ravenne only uses
`monero-javascript` for local WASM key generation; the vulnerable `request` /
`form-data` HTTP path is not used (wallet RPC goes through our own `fetch`).
CI keeps the audit step non-blocking until Monero tooling is replaced or
upstream updates.

## Install

Unzip → run `ravenne.bat` or `ravenne.exe`.
From source: `npm install` then `.\ravenne.bat` (Node.js 18+).
