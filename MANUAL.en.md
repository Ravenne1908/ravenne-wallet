# Ravenne Wallet — User Manual (English)

Version 9.9.0 · Windows · Node.js 18+ · MIT license

Ravenne is a **100% local, 100% terminal** crypto wallet. No account, no
server, no telemetry, **no activation**. All keys stay on your machine,
encrypted with your master password.

Languages: **[Français](MANUAL.fr.md)** · **[README](README.md)**

---

## Contents

1. Installation
2. First launch
3. Concepts
4. Simple menu
5. Advanced menu
6. Command reference
7. Privacy and traceability
8. Security
9. Backups
10. Files used
11. Troubleshooting
12. Tests, build, license

---

## 1. Installation

### From source

Requires **Node.js 18+**.

```powershell
npm install
.\ravenne.bat
```

### Standalone executable

```powershell
.\build.bat
```

Produces `ravenne-wallet-vX.Y.Z.zip` (exe + bundle). No Node install needed
on the target machine.

### Launch

```powershell
.\ravenne.bat            # interactive menu
.\ravenne.bat help       # full command list
```

There is **one entry point**: `ravenne.js` (or the exe). Nothing else to run.

---

## 2. First launch

1. **Master password** — 8 characters minimum. It protects the gate and
   encrypts the vault. It is **unrecoverable**: lose it, lose the vault.
2. **Profile selection** — a profile is one set of wallets + its history.
3. **Mode**:
   - **Simple**: MAIN + receiving addresses, sweep, swap, temp, USB.
   - **Advanced**: everything, including tokens, split, consolidation,
     Bitcoin, Monero, offline signing.
   - **Vault**: separate file, separate password, only mnemonics stored
     (keys derived in memory).

No activation code, no webhook, no outbound call to start.

---

## 3. Concepts

- **Profile**: named container. `ravenne profile new|use|rename|delete`.
- **MAIN**: primary wallet. Can be kept *watch-only* (seed on paper only) —
  a vault leak then does not expose the funds.
- **Receiving**: addresses handed to payers; they forward everything to MAIN.
- **Temp**: burner address; expires, gets swept, its key is erased.
- **Vault**: separate long-term store (`vault.secure.json`).
- **Duress**: a second password opens a decoy vault, silently.
- **USB**: encrypted wallet on a USB stick, keys in RAM only.

---

## 4. Simple menu

Options:

- Receiving addresses (one per payer)
- Balances (MAIN + waiting)
- Forward everything (immediate sweep)
- Auto-forward daemon (random intervals)
- Swap (Uniswap V2, Ethereum)
- Spend from main
- USB wallet
- Temporary address
- Switch wallet / chain
- Settings
- Backup & security
- Diagnostics (check)
- **Privacy (traceability)**
- Advanced mode
- Lock & quit

The status line shows: active chain, wallet count, proxy on/off, jitter
on/off, auto-lock. Banner pills summarize your network posture.

---

## 5. Advanced menu

Categories:

- **Insight & data** — dashboard, list, balance, stats, history, sync, csv, price
- **Wallets** — profile, create, import, watch, ledger, temp, rename, phrase,
  export, remove, qr
- **Transfers** — send, swap, split, consolidate
- **Bitcoin** — list, create, balance, send, watch, qr, phrase, sync, network
- **Monero (XMR)** — list, create, balance, send, forward, watch, phrase,
  install, connect, node, network
- **USB & advanced** — usb, tokens, book, tx-prepare/sign/broadcast
- **Settings & security** — privacy, 2fa, duress, network, rpc, proxy, tor,
  settings, changepass, lock, wipe
- **Automation** — usbbackup, usbrestore

Navigation: `↑↓` move, `⏎` select, `esc` cancel.

---

## 6. Command reference

### Setup and receiving

```
setup [n] [--keep-key]      MAIN + n receiving addresses
addresses [n]               show / add addresses
sweep [--all]               forward everything to MAIN
auto [minutes]              randomized forward daemon
temp <30m|12h|3d> [n]       burner address
```

### EVM wallets

```
create [n] [--words 24]     create n wallets
create [n] --seed           n accounts from one phrase (BIP-44)
import                      phrase, private key or keystore
watch <0x…> <label>         watch-only
ledger [account] [label]    Ledger address
list [--all]                wallets + balances
rename <i> <label>
remove <i>
phrase <i>
export <i>                  encrypted keystore
export-key <i>              raw private key (careful)
qr <i>
```

### Transfers

```
send <from> <to> <amount> [--token SYM] [--broadcast private|rpc]
hop <from> [minutes]        fresh wallet → random wait → MAIN
split <from> <n> [--random] [--delay s]
consolidate <target> [--delay s]
swap <from> <to> <amount> [wallet#]
convert eth ETH USDT        convert before forwarding
convert eth off
```

### Bitcoin

```
btc create [n]
btc list · btc balance
btc send <btc:i> <address> <amount> [--coincontrol]
btc utxos <btc:i>            list UTXOs
btc freeze|unfreeze <i> <#>  exclude / re-include a UTXO
btc label <i> <#> <text>     label a UTXO
btc watch <address> <label>
btc qr <btc:i> · btc phrase <btc:i>
btc sync
btc network main|test
```

Change **always** goes to a fresh address on the internal chain
(`m/84'/coin'/1'/0/i`), never back to the source address.

### Monero

```
xmr create [n]
xmr list · xmr balance
xmr send <from> <to> <amount>
xmr forward
xmr watch <address> <viewkey> <label>
xmr phrase <i> · xmr remove <i>
xmr install                 official engine, SHA-256 verified
xmr engine                  start local engine
xmr connect <url> [user:pass]
xmr node <url> | reset
xmr network main|stage
```

### Offline signing (EVM)

```
tx-prepare <from> <to> <amount> --file u.json      [online]
tx-sign u.json <wallet#>                            [offline machine]
tx-broadcast u.json.signed.json                     [online, soon]
```

### Security and network

```
changepass
lock
wipe [all]                  active vault, or all local data
harden                      apply the privacy profile in one pass
verify <address|wallet>     checksum + look-alike + QR
2fa on|off
duress on|off
network <chain>
rpc [chain] [url|reset]
proxy <url>|off|require on|off
tor
privacy
check
```

### Settings

Everything is also available **inside the app**: main menu → Settings
(proxy, Tor, requireProxy, broadcast, clearnet, BTC API, XMR daemon, custom
RPC, VPN, jitter, rotation, auto-lock). No command line needed.

```
settings                    show
settings vpncheck on|off
settings failclosed on|off
settings prices on|off
settings autolock <0-240>
settings meshvpn on|off
settings sweepfee <1-100>
settings rotation on|off
settings jitter on|off
settings broadcast auto|private|rpc
settings allowclearnet on|off
settings btcapi <url|reset>
settings requireproxy on|off
```

### Backups

```
backup [file]               encrypted vault copy
restore <file>
recover [file]              restore the automatic .bak if the vault is corrupt
usbbackup <folder>
usbrestore <folder>
```

### Global flags

```
--yes -y        accept non-destructive prompts
--all -a        all chains
--random -r     random amounts (split)
--delay <s>     pause between sends
--words 24      24-word seeds
--seed          create from a seed
--token <SYM>   ERC-20 send
--file <path>   transaction file
--keystore <f>  keystore for tx-sign
--broadcast private|rpc
--profile <name>
--no-vpn · --no-proxy        bypass a guard (not recommended)
```

### Environment

```
RAVENNE_PASS=<password>   non-interactive unlock
RAVENNE_KEYPASS=<pass>    keystore / USB password
RAVENNE_FORCE_VPN=1|0     force VPN state
RAVENNE_SKIP_VPN=1        skip VPN gate
HTTPS_PROXY / ALL_PROXY   proxy for all traffic
```

---

## 7. Privacy and traceability

### Network first

```powershell
ravenne proxy http://127.0.0.1:8118
ravenne proxy require on
```

Ravenne routes **everything** through it: RPC, explorers, prices, Monero.
`proxy off` clears it. `require on` refuses to start without a proxy.

`ravenne tor` probes local Tor/Privoxy and persists it.

### What links a transaction

| Layer | What leaks | What breaks it |
|---|---|---|
| Network | IP on every request / broadcast | mandatory proxy |
| Chain | address reuse, change | fresh addresses, private broadcast |
| Counterparty | the person in front | one address per payer |
| Local | labels, CSV, backups | nothing in clear, no cloud |

### Private broadcast

On **Ethereum mainnet**, sends go through **Flashbots Protect** then
**MEV Blocker**: the transaction never touches the public mempool. If both
relays fail, the send fails — **no public fallback**.

```powershell
ravenne settings broadcast private   # forced
ravenne settings broadcast auto      # default: private on ETH, RPC elsewhere
ravenne settings broadcast rpc       # direct (traceable)
ravenne send 0 alice 0.1 --broadcast rpc   # one-off
```

Uniswap swaps and approvals follow the same mode.

### Clearnet guard

With no active proxy/Tor, Ravenne **refuses to send** (EVM, BTC, XMR, swap,
split, consolidation, sweep). A screen explains it once per session; type
`CLEARNET-OK` to force, or set:

```powershell
ravenne settings allowclearnet on|off
```

In `auto` (daemon) mode there is no prompt: blocked until a tunnel exists.

### Other levers

- `ravenne harden`: applies the full profile in one pass (proxy, jitter,
  rotation, private broadcast, clearnet blocked, fail-closed VPN).
- `ravenne hop <wallet> [minutes]`: fresh wallet, random wait, MAIN.
- `ravenne verify <address|wallet>`: checksum, ownership, look-alike.
- **BTC coin control**: `btc utxos`, `btc freeze`, `btc label`, `send --coincontrol`.
- `ravenne privacy`: traceability dashboard.
- RPC rotation and jitter: `settings rotation on`, `settings jitter on`.
- Your own RPC: `ravenne rpc eth http://your-node:8545`.
- Your own Esplora: `settings btcapi https://…`.
- Your own Monero daemon: `xmr node http://…`.
- Used addresses are flagged `used` and warned about.
- Prices off by default.

### Recommended workflow

1. One address per payment (`temp` or `addresses`).
2. `sweep` later, never within the minute.
3. Spend from a spending wallet, never from a receiving address.
4. Never send a KYC withdrawal straight to MAIN.
5. XMR for what must actually be private.

---

## 8. Security

- **Gate**: **Argon2id** (32 MiB, t=3) + constant-time comparison.
  Legacy scrypt vaults are accepted and migrated on the next unlock.
- **Vault**: AES-256-GCM, Argon2id, **padded to 4 KiB buckets** (file size
  does not reveal the wallet count). Unlock ≈ 4–6 s.
- **Persistent lockout**: failures survive restarts; temporary lock from
  10 failures.
- **Local TOTP 2FA**: `2fa on`.
- **Duress**: second password → decoy vault, with no revealing message.
- **Wipe**: 3 random passes + delete; `wipe all` includes the secure vault,
  the decoy, XMR caches and logs.
- **Watch-only MAIN**: recommended; the seed never leaves paper.
- **USB**: keys in RAM, never written to the local disk.
- **Offline signing**: `tx-prepare` / `tx-sign` / `tx-broadcast`.

Honest limits: phrases and keys transit through memory (JavaScript cannot
zero strings); a compromised host (keylogger, screen capture, firmware) is
out of scope.

---

## 9. Backups

- MAIN seed on **paper or metal**, BIP39 passphrase stored separately.
- **Atomic writes**: vault written to a temp file, fsynced, then renamed. A crash cannot truncate it.
- **Automatic `.bak`**: the previous version is kept. On unlock, if the main file is unreadable, Ravenne tries the `.bak` and restores it (the broken file stays as `.corrupt-*`).
- `ravenne recover`: explicit restore from the `.bak`.
- `ravenne backup`: encrypted vault copy, store offline.
- `ravenne usbbackup E:\`: vault + secure vault + gate + proxy config.
- Test a restore before you need it.
- Never keep the history CSV in clear.

---

## 10. Files used

| File | Role |
|---|---|
| `ravenne.js` | engine / single entry point |
| `access.ravenne.json` | Argon2id salt + hash of the master password |
| `vault.ravenne.json` | main vault (AES-256-GCM) |
| `vault.secure.json` | Vault store (separate password) |
| `vault-decoy.ravenne.json` | decoy vault (duress) |
| `net.ravenne.json` | persistent proxy / requireProxy |
| `gate-attempts.log` | local gate failure log |
| `ravenne.ico` | exe icon |

---

## 11. Troubleshooting

**"VPN REQUIRED"** — start your VPN, or accept:
```powershell
ravenne settings vpncheck off     # not recommended
ravenne settings failclosed off   # old fail-open behavior
```

**"No proxy configured, but requireProxy is ON"** — set a proxy or run with
`--no-proxy` (exposes your IP).

**"Envoi bloqué sans tunnel" (send blocked)** — `ravenne proxy …` or
`ravenne settings allowclearnet on`.

**Flashbots fails** — both private relays are unavailable; retry later or
switch to `settings broadcast rpc`.

**RPC unreachable** — `ravenne rpc <chain> reset`, or pick another endpoint:
`ravenne rpc eth https://…`.

**Monero / Windows Defender** — the official binary may be flagged
(PUA/CryptoMiner heuristic). Check the printed SHA-256 and add the folder to
exclusions.

**Node too old** — Node.js 18+ required (`node -v`).

---

## 12. Tests, build, license

```powershell
npm test       # node:test — 15 tests
.\build.bat    # exe + zip
```

**MIT** license — see `LICENSE`. Open code, no Ravenne service dependency.
