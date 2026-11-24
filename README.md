# Ravenne Wallet

**A local-first, privacy-focused crypto wallet that lives in your terminal.**
EVM (Ethereum, Polygon, BNB Chain, Arbitrum, Base, Optimism), Bitcoin and
Monero — no account, no server, no telemetry, no activation.

> Open source (MIT). No webhook, no phone-home, no analytics. Everything runs
> on your machine, encrypted with your master password.
>
> Clean terminal UI: aligned panels, a balance dashboard, English only,
> monochrome with green/yellow status colors.

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
  buckets, TOTP 2FA, duress (decoy) vault, persistent lockout, 3-pass wipe.
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

## Tests

```powershell
npm test
```

## License

MIT — see [LICENSE](LICENSE).
