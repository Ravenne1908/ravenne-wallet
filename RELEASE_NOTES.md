# Ravenne Wallet v9.11.1 — menu navigation fixes, instant saves

## Why this release

On Windows, navigating in and out of submenus a few times could leave a menu
on screen that no longer reacted to the arrow keys. Two separate causes were
found and fixed.

## Menu input

- **Raw mode is kept between menus.** It used to be switched off on every
  transition (`Esc` → parent menu → submenu …) and back on; after a few
  cycles the Windows console stopped delivering input. Menus now enable raw
  mode once and leave it on until the app exits.
- **Own key parser.** Ravenne no longer depends on readline's parser for
  menus. A lone `Esc` is recognised after 35 ms, and `Esc` immediately
  followed by an arrow keeps **both** actions (it used to be swallowed as an
  `Alt+arrow` prefix). Adds `Ctrl+N` / `Ctrl+P`, `Tab`, `PgUp` / `PgDn`,
  `Home` / `End`, `j` / `k`.
- `Esc` inside a text/number/password prompt now **cancels the prompt** and
  returns to the menu instead of quitting the whole app.
- Empty choice lists no longer crash the key handler.

## No more dead ends

- **Advanced mode → Settings & security → Settings** now opens the real,
  interactive Settings menu (it used to print a static table).
- New **RPC endpoints** menu, **ERC-20 tokens** menu (add / remove / show)
  and **Address book** menu (add / remove / show) — the entries whose
  descriptions promised management.
- The **Vault** screen uses the same renderer as the rest of the app: aligned
  icons, `esc` = back, no inverse-video block.
- After Settings, Security, Vault or Advanced return, the main menu is shown
  directly instead of a blank `— Enter —` prompt where arrows look dead.
- Results that must be read (seed phrase, private key, backup path, privacy
  dashboard, token/UTXO tables) now wait for Enter before the next repaint
  clears the screen.

## Responsiveness

- Argon2id was re-run on **every** vault save: a settings toggle froze the UI
  for 1.5–3 s (much more on a slow machine). The derived key is now cached for
  the session (same salt, file format unchanged), so a save takes ~20–30 ms.
  A new password or a restored vault gets a fresh salt and key.
- `icacls` hardening runs asynchronously; it no longer blocks the menu.

## Verification

- `node --check`: OK.
- `npm test`: **24/24** (new: menu key parser incl. `Esc`+arrow, empty menu
  layout, long-word titles not mistaken for icons).
- esbuild single-file bundle: OK. Non-TTY smoke tests: OK.
- Interactive audit in a real pseudo-terminal: Settings → each of the four
  categories, back out and re-enter (the previous freeze), toggle a setting
  then move immediately, Advanced → Settings, tokens and address book menus —
  all responsive.

## Known advisory (not a code bug)

`npm audit` still reports the `form-data` advisory pulled by
`monero-javascript → request`; there is no upstream fix and Ravenne does not
use that HTTP path (Monero RPC goes through our own `fetch`).

## Install

Unzip → run `ravenne.bat` or `ravenne.exe`.
From source: `npm install` then `.\ravenne.bat` (Node.js 18+).
