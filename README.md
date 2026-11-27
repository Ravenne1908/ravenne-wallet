# Ravenne Wallet

**A local-first, privacy-focused crypto wallet that lives in your terminal.**
EVM (Ethereum, Polygon, BNB Chain, Arbitrum, Base, Optimism), Bitcoin and
Monero — no account, no server, no telemetry, no activation.

> Open source (MIT). No webhook, no phone-home, no analytics. Everything runs
> on your machine, encrypted with your master password.
>
> Clean terminal UI: a **centered menu** with icons, a **ghost boot splash**,
> automatic **light/dark theme detection** (works over a Windows Terminal
> background image), English only, monochrome with green/yellow status colors.

**[Full manual — English](MANUAL.en.md)** · **[Manuel complet — français](MANUAL.fr.md)**

---

## What it does

- **Multiple profiles** — several named wallets, one active at a time.
- **Simple flow** — one MAIN wallet (seed can stay on paper only) plus
  receiving addresses that forward everything to it.
- **Advanced** — ERC-20 tokens, split/consolidate, offline signing, address
  book, import/export, statistics.
- **Vault** — separate file, separate password, only mnemonics on disk
  (private keys derived in memory).
- **Bitcoin** BIP84 (bc1…), fresh change address on the internal chain,
  mainnet/testnet.
- **Monero** — keys generated locally, optional wallet engine.
- **Security** — Argon2id master password, AES-256-GCM vault padded to 4 KiB
  buckets, **atomic writes + `.bak` + `ravenne recover`**, TOTP 2FA, duress
  (decoy) vault, persistent lockout, 3-pass wipe.
- **Privacy** — persistent proxy/Tor, RPC rotation, query jitter, private
  broadcast (Flashbots + MEV Blocker), custom Esplora, BTC coin control,
  private hop, address-reuse guard, sends blocked without a tunnel.

## Install

Windows, **Node.js 18+**:

```powershell
npm install
.\ravenne.bat
```

Standalone executable (no Node needed):

```powershell
.\build.bat
```

## First run

1. Choose your **master password** (8 chars min., unrecoverable).
2. Select or create a **profile**.
3. Follow the dashboard: set up MAIN + receiving addresses.

No activation code, no webhook, no outbound call to start.

## Interface

- **Ghost splash** — a monochrome, 235-frame animation (GhosttyFetch, MIT),
  scaled to the window, with a progress bar. Any key skips it.
  `Settings → Wallet & display` controls it: on/off, short/normal/full,
  or *Preview the splash*. CLI: `--anim short|normal|full`, `--no-anim`,
  `RAVENNE_NO_ANIM=1`.
- **Centered menu** — icons in their own column, scrolling with
  `↑ n more / ↓ n more`, live re-centering on resize, `esc` to go back.
- **Background image friendly** — Ravenne never paints a background: it asks
  the terminal for its background color (OSC 11) and adapts the palette.
  Force it with `--theme light|dark` or `Settings → Wallet & display → Theme`.
- **Monochrome** — white/gray UI, green = OK, yellow = warning/error.

## Quick start

```powershell
ravenne                      # interactive dashboard
ravenne help                 # all commands
ravenne setup                # MAIN + receiving addresses
ravenne addresses 5          # new addresses to hand out
ravenne temp 24h             # burner address, one payment
ravenne sweep                # forward everything to MAIN
ravenne hop 0 30             # private EVM hop via a fresh wallet
ravenne harden               # apply the privacy profile in one pass
ravenne verify w1            # checksum + look-alike + QR
ravenne send 0 alice 0.1     # from wallet #0
```

## Privacy essentials

```powershell
ravenne proxy http://127.0.0.1:8118   # Tor/Privoxy or a VPN box
ravenne proxy require on              # refuse to start without a tunnel
ravenne settings broadcast private    # private relays on Ethereum
ravenne settings btcapi https://…     # your own Esplora
ravenne settings allowclearnet off    # block sends without a tunnel
```

Everything above is also available **inside the app**: Home → Settings, and
Home → Privacy.

Details, limits and the full workflow: **[English manual](MANUAL.en.md)** /
**[manuel français](MANUAL.fr.md)**.

## Verify a release

Signed with Ed25519. Fingerprint:

`1e:25:f2:cf:c7:59:54:78:3c:0e:48:9a:ba:0c:cf:bf:70:ef:36:e0:65:66:75:de:82:cc:82:e1:1d:31:c7:b2`

```powershell
node scripts/verify-release.mjs SHA256SUMS release-key.pub
Get-FileHash ravenne-wallet-vX.Y.Z.zip -Algorithm SHA256
```

## Tests

```powershell
npm test          # 22 tests: crypto, wallets, BTC tx, menus, splash geometry
npm run ghost     # preview one splash frame in the terminal
```

## License

MIT — see [LICENSE](LICENSE). The boot animation is third-party (MIT):
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
