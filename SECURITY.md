# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 9.7.x and newer | yes |
| older | no |

## Reporting a vulnerability

Use **GitHub Security Advisories** on this repository
(`Security` → `Report a vulnerability`). Do not open a public issue for a
vulnerability that could put funds at risk.

Please include:

- an affected version / commit,
- a minimal reproduction (command or script),
- the impact (key disclosure, fund loss, deanonymisation, DoS…).

## Threat model (honest summary)

Ravenne protects against:

- offline disk theft (Argon2id + AES-256-GCM, padded vault),
- casual process inspection (keys derived in memory, watch-only MAIN),
- address reuse and naive payment clustering (fresh addresses, coin control,
  private broadcast, random hop),
- IP leakage to RPC/explorer providers **when a proxy/Tor is configured and
  required**,
- accidental vault corruption (atomic writes + `.bak` + `ravenne recover`).

Ravenne does **not** protect against:

- a compromised host (keylogger, screen capture, firmware, malicious OS),
- on-chain graph analysis (it raises cost, it does not erase links),
- a KYC counterparty or a public RPC without a tunnel,
- third-party protocols (Uniswap, relays, Monero daemons) lying to you,
- an unaudited implementation. **No external audit has been performed.**

## Release signing

Releases are signed with an **Ed25519** key. The public key is
`release-key.pub`. The private key never touches this repository.

**Fingerprint:** `1e:25:f2:cf:c7:59:54:78:3c:0e:48:9a:ba:0c:cf:bf:70:ef:36:e0:65:66:75:de:82:cc:82:e1:1d:31:c7:b2`

Verify a release:

```powershell
# SHA256SUMS.sig must verify against release-key.pub
node scripts/verify-release.mjs SHA256SUMS release-key.pub

# then check the zip/exe hashes
Get-FileHash ravenne-wallet-vX.Y.Z.zip -Algorithm SHA256
```

The fingerprint can also be printed with
`node scripts/verify-release.mjs --fingerprint release-key.pub`.

## Dependency policy

- Runtime dependencies are pinned by `package-lock.json`.
- CI runs `npm ci`, `node --check`, `npm test` on Windows and Linux.
- `npm audit --omit=dev --audit-level=critical` runs in CI.
