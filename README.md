# Ravenne Wallet

**Wallet crypto local et privé, 100 % terminal.** EVM (Ethereum, Polygon, BNB,
Arbitrum, Base, Optimism), Bitcoin et Monero — sans compte, sans serveur,
sans télémétrie, sans activation.

> Open source (MIT). Aucun webhook, aucune vérification, aucun appel à la
> maison. Tout tourne sur ta machine, chiffré par ton mot de passe maître.

**[Manuel complet — français](MANUAL.fr.md)** · **[Full manual — English](MANUAL.en.md)**

---

## Ce que ça fait

- **Profils multiples** : plusieurs wallets nommés, un actif à la fois.
- **Simple** : un wallet MAIN (seed possiblement sur papier uniquement) +
  des adresses de réception qui renvoient tout vers lui.
- **Advanced** : tout — tokens ERC-20, split/consolidation, offline signing,
  carnet d'adresses, import/export, statistiques.
- **Vault** : coffre séparé, mot de passe séparé, seules les phrases (pas les
  clés privées) sont sur le disque.
- **Bitcoin** BIP84 (bc1…), change sur adresse fraîche, mainnet/testnet.
- **Monero** : clés générées localement, wallet engine optionnel.
- **Sécurité** : passphrase maître scrypt, coffre AES-256-GCM, 2FA TOTP,
  coffre leurre (duress), verrouillage persistant, wipe 3 passes.
- **Confidentialité** : proxy persistant, Tor, rotation RPC, jitter,
  diffusion privée (Flashbots sur Ethereum), API BTC personnalisable,
  garde anti-réutilisation d'adresse, blocage des envois sans tunnel.

## Installation

Windows, Node.js **18 ou plus** :

```powershell
npm install
.\ravenne.bat
```

Ou build un exécutable autonome (pas besoin de Node) :

```powershell
.\build.bat
```

## Premier lancement

1. Choisis ton **mot de passe maître** (8 caractères min., irrécupérable).
2. Sélectionne ou crée un **profil**.
3. Choisis le mode **Simple / Advanced / Vault**.
4. En Simple : suis le setup guidé (MAIN + adresses de réception).

Aucune activation, aucun code, aucun envoi réseau au propriétaire.

## Usage éclair

```powershell
ravenne                      # menu interactif
ravenne help                 # toutes les commandes
ravenne setup                # MAIN + adresses de réception
ravenne addresses 5          # nouvelles adresses à donner
ravenne temp 24h             # adresse jetable, une seule fois
ravenne sweep                # tout renvoyer vers MAIN
ravenne send 0 alice 0.1     # depuis le wallet #0
ravenne privacy              # ce qui peut te relier
ravenne check                # diagnostics
```

## Confidentialité — l'essentiel

```powershell
ravenne proxy http://127.0.0.1:8118   # Tor/Privoxy ou VPN box
ravenne proxy require on              # refuse de démarrer sans tunnel
ravenne settings broadcast private    # Flashbots sur Ethereum
ravenne settings btcapi https://…     # ton Esplora
ravenne settings allowclearnet off    # envois bloqués sans tunnel
```

Détails, limites et workflow complet : **[manuel FR](MANUAL.fr.md)** /
**[manual EN](MANUAL.en.md)**.

## Tests

```powershell
npm test
```

## Licence

MIT — voir [LICENSE](LICENSE).
