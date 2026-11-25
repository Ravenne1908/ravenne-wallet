# Ravenne Wallet — Manuel d'utilisation (français)

Version 9.9.0 · Windows · Node.js 18+ · licence MIT

Ravenne est un wallet crypto **100 % local, 100 % terminal**. Aucun compte,
aucun serveur, aucune télémétrie, **aucune activation**. Toutes les clés
restent sur ta machine, chiffrées par ton mot de passe maître.

Languages: **[English](MANUAL.en.md)** · **[README](README.md)**

---

## Sommaire

1. Installation
2. Premier lancement
3. Concepts
4. Menu Simple
5. Menu Advanced
6. Référence des commandes
7. Confidentialité et traçabilité
8. Sécurité
9. Sauvegardes
10. Fichiers utilisés
11. Dépannage
12. Tests, build, licence

---

## 1. Installation

### Depuis les sources

Prérequis : **Node.js 18 ou plus**.

```powershell
npm install
.\ravenne.bat
```

### Exécutable autonome

```powershell
.\build.bat
```

Produit `ravenne-wallet-vX.Y.Z.zip` (exe + bundle). Aucune installation de
Node requise sur la machine cible.

### Lancement

```powershell
.\ravenne.bat            # menu interactif
.\ravenne.bat help       # liste complète des commandes
```

Il n'y a **qu'un point d'entrée** : `ravenne.js` (ou l'exe). Rien d'autre à
lancer.

---

## 2. Premier lancement

1. **Mot de passe maître** — 8 caractères minimum. Il protège le portail et
   chiffre le coffre. Il est **irrécupérable** : perdu = coffre perdu.
2. **Sélection de profil** — un profil = un jeu de wallets + son historique.
3. **Mode** :
   - **Simple** : MAIN + adresses de réception, sweep, swap, temp, USB.
   - **Advanced** : tout, y compris tokens, split, consolidation, Bitcoin,
     Monero, signature hors-ligne.
   - **Vault** : coffre séparé, mot de passe séparé, seules les phrases sont
     stockées (clés dérivées en mémoire).

Aucun code d'activation, aucun webhook, aucun appel sortant pour démarrer.

---

## 3. Concepts

- **Profil** : conteneur nommé. `ravenne profile new|use|rename|delete`.
- **MAIN** : wallet principal. On peut le garder *watch-only* (seed uniquement
  sur papier) — une fuite du coffre ne donne alors pas accès aux fonds.
- **Réception** : adresses données aux payeurs. Elles renvoient tout vers MAIN.
- **Temp** : adresse jetable, expire puis est sweepée et sa clé effacée.
- **Vault** : coffre long terme séparé (`vault.secure.json`).
- **Duress** : second mot de passe qui ouvre un coffre leurre, silencieusement.
- **USB** : wallet chiffré sur clé USB, clés en RAM uniquement.

---

## 4. Menu Simple

Options :

- Receiving addresses (donner une adresse par payeur)
- Balances (MAIN + en attente)
- Forward everything (sweep immédiat)
- Auto-forward daemon (intervalles aléatoires)
- Swap (Uniswap V2, Ethereum)
- Spend from main
- USB wallet
- Temporary address
- Switch wallet / chain
- Settings
- Backup & security
- Diagnostics (check)
- **Confidentialité (traçabilité)**
- Advanced mode
- Lock & quit

La ligne d'état affiche : chaîne active, nombre de wallets, proxy on/off,
jitter on/off, auto-lock. Les « pastilles » de la bannière résument la
configuration réseau.

---

## 5. Menu Advanced

Catégories :

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

Navigation : `↑↓` déplacer, `⏎` valider, `esc` annuler.

---

## 6. Référence des commandes

### Setup et réception

```
setup [n] [--keep-key]      MAIN + n adresses de réception
addresses [n]               afficher / ajouter des adresses
sweep [--all]               tout renvoyer vers MAIN
auto [minutes]              daemon de forward aléatoire
temp <30m|12h|3d> [n]       adresse jetable
```

### Wallets EVM

```
create [n] [--words 24]     créer n wallets
create [n] --seed           n comptes depuis une seule phrase (BIP-44)
import                      phrase, clé privée ou keystore
watch <0x…> <label>         watch-only
ledger [compte] [label]     adresse Ledger
list [--all]                wallets + soldes
rename <i> <label>
remove <i>
phrase <i>
export <i>                  keystore chiffré
export-key <i>              clé privée brute (attention)
qr <i>
```

### Transferts

```
send <from> <to> <montant> [--token SYM] [--broadcast private|rpc]
hop <from> [minutes]        wallet frais → attente aléatoire → MAIN
split <from> <n> [--random] [--delay s]
consolidate <target> [--delay s]
swap <from> <to> <montant> [wallet#]
convert eth ETH USDT        conversion avant forward
convert eth off
```

### Bitcoin

```
btc create [n]
btc list · btc balance
btc send <btc:i> <adresse> <montant> [--coincontrol]
btc utxos <btc:i>            lister les UTXO
btc freeze|unfreeze <i> <#>  exclure / réintégrer un UTXO
btc label <i> <#> <texte>    étiqueter un UTXO
btc watch <adresse> <label>
btc qr <btc:i> · btc phrase <btc:i>
btc sync
btc network main|test
```

Le change part **toujours** sur une adresse fraîche de la chaîne interne
(`m/84'/coin'/1'/0/i`), jamais sur l'adresse source.

### Monero

```
xmr create [n]
xmr list · xmr balance
xmr send <from> <to> <montant>
xmr forward
xmr watch <adresse> <vue> <label>
xmr phrase <i> · xmr remove <i>
xmr install                 engine officiel, SHA-256 vérifié
xmr engine                  démarre l'engine local
xmr connect <url> [user:pass]
xmr node <url> | reset
xmr network main|stage
```

### Signature hors-ligne (EVM)

```
tx-prepare <from> <to> <montant> --file u.json      [en ligne]
tx-sign u.json <wallet#>                            [machine hors-ligne]
tx-broadcast u.json.signed.json                     [en ligne, vite]
```

### Sécurité et réseau

```
changepass
lock
wipe [all]                  coffre actif, ou toutes les données locales
harden                      profil de confidentialité en une passe
verify <adresse|wallet>     checksum + look-alike + QR
2fa on|off
duress on|off
network <chain>
rpc [chain] [url|reset]
proxy <url>|off|require on|off
tor
privacy
check
```

### Réglages

Tout est aussi accessible **dans le logiciel** : menu principal → Settings
(proxy, Tor, requireProxy, broadcast, clearnet, BTC API, daemon XMR, RPC
personnalisé, VPN, jitter, rotation, auto-lock). Aucune commande à taper.

```
settings                    afficher
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

### Sauvegardes

```
backup [fichier]            copie chiffrée du coffre
restore <fichier>
recover [fichier]           restaure le .bak automatique si le coffre est corrompu
usbbackup <dossier>
usbrestore <dossier>
```

### Options globales

```
--yes -y        confirmer les prompts non destructifs
--all -a        toutes les chaînes
--random -r     montants aléatoires (split)
--delay <s>     pause entre envois
--words 24      seeds de 24 mots
--seed          créer depuis une seed
--token <SYM>   envoi ERC-20
--file <path>   fichier de tx
--keystore <f>  keystore pour tx-sign
--broadcast private|rpc
--profile <nom>
--no-vpn · --no-proxy        contourner une garde (déconseillé)
```

### Variables d'environnement

```
RAVENNE_PASS=<mot de passe>   déverrouillage non interactif
RAVENNE_KEYPASS=<pass>        mot de passe keystore / USB
RAVENNE_FORCE_VPN=1|0         force l'état VPN
RAVENNE_SKIP_VPN=1            saute la garde VPN
HTTPS_PROXY / ALL_PROXY       proxy pour tout le trafic
```

---

## 7. Confidentialité et traçabilité

### Le réseau d'abord

```powershell
ravenne proxy http://127.0.0.1:8118
ravenne proxy require on
```

Ravenne route **tout** par ce proxy : RPC, explorateurs, prix, Monero.
`proxy off` efface le réglage. `require on` refuse de démarrer sans proxy.

`ravenne tor` détecte Privoxy/Tor en local et l'enregistre.

### Ce qui relie une transaction

| Couche | Ce qui trahit | Ce qui la casse |
|---|---|---|
| Réseau | IP sur chaque requête / broadcast | proxy obligatoire |
| Chaîne | réutilisation d'adresse, change | adresses fraîches, diffusion privée |
| Correspondant | la personne en face | une adresse par payeur |
| Local | labels, CSV, sauvegardes | rien en clair, pas de cloud |

### Diffusion privée

Sur **Ethereum mainnet**, les envois passent par **Flashbots Protect** puis
**MEV Blocker** : la transaction ne transite jamais par le mempool public.
Si les deux relais échouent, l'envoi échoue — **aucun repli public**.

```powershell
ravenne settings broadcast private   # forcé
ravenne settings broadcast auto      # défaut : privé sur ETH, RPC ailleurs
ravenne settings broadcast rpc       # direct (traçable)
ravenne send 0 alice 0.1 --broadcast rpc   # ponctuel
```

Les swaps et approbations Uniswap suivent le même mode.

### Garde clearnet

Sans proxy/Tor actif, Ravenne **refuse d'envoyer** (EVM, BTC, XMR, swap,
split, consolidation, sweep). Un écran l'explique une fois par session ;
tape `CLEARNET-OK` pour forcer, ou règle :

```powershell
ravenne settings allowclearnet on|off
```

En mode `auto` (daemon), aucun prompt : bloqué tant qu'il n'y a pas de tunnel.

### Autres leviers

- `ravenne harden` : applique le profil complet en une passe (proxy, jitter,
  rotation, diffusion privée, clearnet bloqué, VPN fail-closed).
- `ravenne hop <wallet> [minutes]` : wallet frais, attente aléatoire, MAIN.
- `ravenne verify <adresse|wallet>` : checksum, appartenance, look-alike.
- **Coin control BTC** : `btc utxos`, `btc freeze`, `btc label`, `send --coincontrol`.
- `ravenne privacy` : tableau de bord des couches de traçabilité.
- Rotation RPC et jitter : `settings rotation on`, `settings jitter on`.
- Ton propre RPC : `ravenne rpc eth http://ton-node:8545`.
- Ton propre Esplora : `settings btcapi https://…`.
- Ton propre daemon Monero : `xmr node http://…`.
- Adresses usagées marquées `used` et signalées.
- Prix off par défaut.

### Workflow recommandé

1. Une adresse par paiement (`temp` ou `addresses`).
2. `sweep` plus tard, jamais dans la minute.
3. Dépense depuis un wallet de dépense, jamais depuis une réception.
4. Jamais de retrait KYC directement vers MAIN.
5. XMR pour ce qui doit être réellement privé.

---

## 8. Sécurité

- **Portail** : **Argon2id** (32 Mio, t=3) + comparaison à temps constant.
  Les anciens coffres scrypt sont acceptés et migrés au déverrouillage suivant.
- **Coffre** : AES-256-GCM, Argon2id, **paddé par blocs de 4 Kio** (la taille
  du fichier ne révèle pas le nombre de wallets). Déverrouillage ≈ 4–6 s.
- **Verrouillage persistant** : les échecs survivent au redémarrage ;
  blocage temporaire à partir de 10 échecs.
- **2FA TOTP** locale : `2fa on`.
- **Duress** : second mot de passe → coffre leurre, sans message révélateur.
- **Wipe** : 3 passes aléatoires + suppression ; `wipe all` inclut le coffre
  sécurisé, le leurre, les caches XMR et les logs.
- **MAIN watch-only** : recommandé ; la seed ne quitte pas le papier.
- **USB** : clés en RAM, jamais écrites sur le disque local.
- **Signature hors-ligne** : `tx-prepare` / `tx-sign` / `tx-broadcast`.

Limites honnêtes : les phrases et clés transitent en mémoire (JavaScript ne
permet pas de les effacer) ; un hôte compromis (keylogger, capture d'écran,
firmware) reste hors de portée.

---

## 9. Sauvegardes

- Seed MAIN **sur papier ou métal**, passphrase BIP39 stockée séparément.
- **Écriture atomique** : coffre écrit dans un fichier temporaire, synchronisé, puis renommé. Une coupure ne peut pas le tronquer.
- **`.bak` automatique** : la version précédente est conservée. Au déverrouillage, si le coffre principal est illisible, Ravenne tente le `.bak` et le restaure (l'ancien est gardé en `.corrupt-*`).
- `ravenne recover` : restauration explicite depuis le `.bak`.
- `ravenne backup` : copie chiffrée du coffre, à stocker hors ligne.
- `ravenne usbbackup E:\` : coffre + coffre sécurisé + portail + config proxy.
- Teste une restauration avant d'en avoir besoin.
- Ne stocke jamais le CSV d'historique en clair.

---

## 10. Fichiers utilisés

| Fichier | Rôle |
|---|---|
| `ravenne.js` | moteur / point d'entrée unique |
| `access.ravenne.json` | sel + hash Argon2id du mot de passe maître |
| `vault.ravenne.json` | coffre principal (AES-256-GCM) |
| `vault.secure.json` | coffre Vault (mot de passe séparé) |
| `vault-decoy.ravenne.json` | coffre leurre (duress) |
| `net.ravenne.json` | proxy persistant / requireProxy |
| `gate-attempts.log` | journal local des échecs de portail |
| `ravenne.ico` | icône de l'exe |

---

## 11. Dépannage

**« VPN REQUIRED »** — démarre ton VPN, ou accepte :
```powershell
ravenne settings vpncheck off     # déconseillé
ravenne settings failclosed off   # ancien comportement (fail-open)
```

**« No proxy configured, but requireProxy is ON »** — configure un proxy ou
lance avec `--no-proxy` (expose ton IP).

**« Envoi bloqué sans tunnel »** — `ravenne proxy …` ou
`ravenne settings allowclearnet on`.

**Flashbots échoue** — les deux relais privés sont indisponibles ; réessaie
plus tard ou passe en `settings broadcast rpc`.

**RPC injoignable** — `ravenne rpc <chain> reset`, ou choisis un autre
endpoint : `ravenne rpc eth https://…`.

**Monero / Windows Defender** — le binaire officiel peut être signalé à tort
(PUA/CryptoMiner). Vérifie le SHA-256 affiché et ajoute le dossier aux
exclusions.

**Node trop vieux** — Node.js 18+ requis (`node -v`).

---

## 12. Tests, build, licence

```powershell
npm test       # node:test — 15 tests
.\build.bat    # exe + zip
```

Licence **MIT** — voir `LICENSE`. Code ouvert, aucune dépendance à un service
Ravenne.
