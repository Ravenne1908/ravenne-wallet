# GhosttyFetch pour Windows 🪟👻

Splash animé du logo **Ghostty** pour ton terminal Windows — édition **noir et blanc brillant** : contours en blanc pur, remplissage en dégradé de gris qui ondule de haut en bas.

C'est un portage Windows en **Python** de [GhosttyFetch](https://github.com/BarutSRB/GhosttyFetch) (Zig, macOS/Linux, MIT), réécrit de zéro et **sans la fonctionnalité risquée** de l'original (le mini-prompt qui exécute des commandes, signalée dans leur README). Seules les données d'animation et l'algorithme de redimensionnement (vote majoritaire) sont réutilisées, avec attribution dans [LICENSE](LICENSE).

```
              ==              @@@@@@@@@@
            ==    ·@$$$$$$$$$@@@$$$$$$@·    ==
           ==   ·@$$$$$$$$$$@      @$$$$@·   ==
                ·@$$$$$@               o@··
                ·@$$$$$                @···
```

## Ce que ça fait

- Affiche l'animation **Ghostty de 235 frames**, mise à l'échelle automatiquement à la taille du terminal (ratio préservé, centrage horizontal)
- **Dégradé monochrome scrollant** (blanc → gris « noir brillant ») sur le remplissage, contours en blanc pur — en vrai « noir et blanc brillant »
- Redimensionnement **en direct** : redimensionne la fenêtre, l'animation s'adapte
- Sortie sans scintillement (synchronized output, supporté par Windows Terminal)
- Exit propre : `Ctrl+C` rend le curseur et laisse le logo affiché
- Aucun prompt interactif, aucun accès réseau, aucune exécution de commande — juste l'animation

## Prérequis

- **Windows 10+** avec [Windows Terminal](https://aka.ms/terminal) (recommandé — le legacy `conhost.exe` fonctionne aussi sur Win10+, mais QuickEdit peut mettre la sortie en pause si tu sélectionnes du texte)
- **Python 3.8+** (`winget install Python.Python.3.12` si besoin)

Aucune dépendance externe : **stdlib uniquement** (json, ctypes, argparse).

## Utilisation

```powershell
python ghosttyfetch.py              # boucle infinie jusqu'à Ctrl+C
python ghosttyfetch.py --once       # un cycle complet puis sortie
python ghosttyfetch.py --cycles 3   # trois cycles puis sortie
```

Pour l'utiliser comme splash à l'ouverture du terminal, ajoute dans ton `$PROFILE` PowerShell :

```powershell
python C:\chemin\vers\ghosttyfetch.py --once
```

### Variante compacte

Deux animations sont incluses. `animation.json` (défaut) : logo ASCII détaillé de 41 lignes. `ansi.json` : version compacte de 21 lignes en blocs (`█▀▄`), pour les petits terminaux :

```powershell
python ghosttyfetch.py --animation ansi.json
```

### Options en ligne de commande

| Option | Effet |
|---|---|
| `--animation FICHIER` | autre fichier d'animation (ex. `ansi.json`) |
| `--config FICHIER` | autre `config.json` |
| `--fps N` | vitesse de lecture (défaut 30) |
| `--color COULEUR` | couleur des contours : `#rrggbb`, ANSI brut (`38;5;45`) ou `off` |
| `--no-color` | désactive toutes les couleurs |
| `--force-color` | force les couleurs même si la sortie est redirigée |
| `--no-center` | colle le logo à gauche au lieu de centrer |
| `--no-scroll` | dégradé figé au lieu d'ondulant |
| `--once` / `--cycles N` | nombre de cycles (défaut : infini) |
| `--frame N` | rend une seule frame (mode script/preview, pipé sur stdout) |

### Variables d'environnement

Identiques à l'original : `GHOSTTY_FPS`, `GHOSTTY_COLOR`, `FORCE_COLOR`, `NO_COLOR`. Priorité : ligne de commande > variables d'environnement > `config.json` > défauts.

## Configuration (`config.json`)

```jsonc
{
  "animation_file": "animation.json",
  "fps": 30.0,
  "color": "#ffffff",              // contours du logo (blanc pur)
  "white_gradient_colors": [       // dégradé du remplissage, haut -> bas
    "#e8e8e8", "#d9d9d9", "#c9c9c9", "#b9b9b9", "#a9a9a9",
    "#999999", "#898989", "#7a7a7a", "#6a6a6a", "#5b5b5b"
  ],
  "white_gradient_scroll": true,   // le dégradé ondule vers le bas
  "white_gradient_scroll_speed": 10,
  "center": true,                  // centre horizontalement
  "cycles": 0,                     // 0 = boucle infinie
  "sync_output": true,             // rendu sans scintillement
  "no_color": false,
  "force_color": false
}
```

Recherche des fichiers de données : répertoire du script → répertoire courant → `%APPDATA%\ghosttyfetch\`.

## Structure du projet

```
ghosttyfetch.py      # point d'entrée
gfetch/
  cli.py             # options CLI + boucle de lecture (timing, resize, exit)
  frames.py          # chargement JSON, parsing des marqueurs, scaling, dégradé
  config.py          # config.json + variables d'environnement + couleurs
  term.py            # ANSI sur Windows (VT100), taille du terminal, curseur
animation.json       # asset : 235 frames (logo ASCII 41 lignes)
ansi.json            # asset : 235 frames (variante compacte blocs 21 lignes)
config.json          # configuration par défaut (noir et blanc brillant)
```

## Packager en .exe autonome (optionnel)

Pour un exécutable unique sans Python installé :

```powershell
pip install pyinstaller
pyinstaller --onefile --name ghosttyfetch ^
  --add-data "animation.json;." --add-data "ansi.json;." --add-data "config.json;." ^
  ghosttyfetch.py
# -> dist\ghosttyfetch.exe
```

## Crédits & licence

- Animation Ghostty + algorithme de scaling : [BarutSRB/GhosttyFetch](https://github.com/BarutSRB/GhosttyFetch) (MIT) — voir [LICENSE](LICENSE)
- Logo Ghostty : projet [Ghostty](https://ghostty.org/)
- Ce portage : MIT, code Python original (aucune partie du prompt interactif de l'original n'a été portée)
