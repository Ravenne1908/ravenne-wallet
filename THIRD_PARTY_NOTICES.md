# Third-party notices

Ravenne Wallet is MIT licensed. It bundles or derives from the following
projects.

## GhosttyFetch — boot splash animation

- Upstream: https://github.com/BarutSRB/GhosttyFetch
- Windows port / assets: `gost/` (MIT, see `gost/LICENSE`)
- License: MIT — Copyright (c) 2024 BarutSRB and the gost project contributors
- What we use:
  - the 235-frame Ghostty logo animation (`gost/animation.json`),
  - the majority-vote resampling idea used when shrinking the art.
- What we do **not** use: the original interactive prompt that could execute
  shell commands (intentionally left out upstream and here).

`assets/ghost.js` is generated from `gost/animation.json` by
`scripts/build-ghost.mjs`. It contains a gzip+base64 copy of the animation
frames, so the splash works from the single-file bundle and the `.exe`.

## Ghostty logo

The animation depicts the Ghostty ghost logo:
https://ghostty.org/ — the logo and name belong to the Ghostty project.

## npm dependencies

All runtime dependencies are listed in `package.json` with their own licenses:
`ethers` (MIT), `@clack/prompts` (MIT), `prompts` (MIT), `qrcode` (MIT),
`qrcode-terminal` (Apache-2.0), `bitcoinjs-lib` (MIT), `@scure/bip32`,
`@scure/bip39` (MIT), `@noble/hashes` (MIT), `monero-javascript` (MIT),
`undici` (MIT).
