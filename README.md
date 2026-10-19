# meta-gaming

Des petits jeux de 10 à 15 minutes, joués par un agent directement dans le terminal. Chaque jeu est une **cartouche** : un fichier Markdown écrit à la main (lore, règles, ambiance). Un **skill** se charge du reste : il la lit, comble ce qui manque et fait office de maître du jeu.

## Les cartouches

| Cartouche | Le pitch | Statut |
|---|---|---|
| [`DUNGEON.md`](DUNGEON.md) | Deux aventuriers en fuite dans les Catacombes de Paris. Trouveront-ils la sortie ? | testée |
| [`PUISSANCE4.md`](PUISSANCE4.md) | Un Puissance 4 au fond du Balto contre Mémé Josiane, invaincue depuis 1987. | testée |
| [`NARCO.md`](NARCO.md) | Mexique post-apocalyptique, 45 ans après le 21/12/2012, sous la coupe de la Narco-nacion. | ⚠️ **pas encore testée** |

NARCO n'a encore jamais été jouée de bout en bout. Elle devrait marcher, mais attendez-vous à des aspérités (équilibrage, chiffres incohérents, rythme). Les retours sont bienvenus.

## Jouer avec Claude Code

```bash
git clone git@github.com:Dam-Buty/meta-gaming.git
cd meta-gaming
claude
```

Les skills sont dans `.claude/skills/` : Claude Code les détecte tout seul quand on le lance depuis ce dossier. Il y a deux façons de jouer.

### `/cartouche` : le jeu improvisé dans le chat

```
/cartouche DUNGEON.md
```

L'agent raconte en prose et redessine une console ASCII à chaque tour. Les choix s'affichent sous forme de questions à options, les dés sont tirés pour de vrai dans le shell, et il y a du son si votre machine en a. Le plus simple pour commencer.

### `/cartouche-mods` : le jeu avec un mod sur mesure

```
/cartouche-mods PUISSANCE4.md
```

À la mise en place, l'agent écrit un **mod** Claude Code, c'est-à-dire un petit plugin chargé à chaud dans la session. Il donne un écran fixe dans l'interface, des boutons et des raccourcis clavier, et les règles et le hasard sont tenus par du code testé. Au premier lancement, Claude Code vous demande *« Enable hot reloading for this session? »* : répondez oui, puis répondez au message de l'agent pour lancer la partie.

Très adapté aux jeux à règles strictes comme Puissance 4. Il faut une version récente de Claude Code qui gère les mods.

### Bon à savoir

- **Son** : sous Linux, il faut un lecteur audio (`paplay`, `pw-play`, `ffplay`, `mpv` ou `aplay`) et `python3`. Sous macOS, ça marche directement. Sans son, le jeu tourne quand même.
- **Dossiers de partie** : chaque partie crée un dossier `partie-<date>-<suffixe>/` à la racine du projet, pour l'état, les vues ASCII et les sons. Ces dossiers sont ignorés par git et vous pouvez les supprimer à la fin.
- **Une partie, c'est 10 à 15 minutes**, et elle a une vraie fin. Pour rejouer, relancez la commande : chaque partie repart de zéro.

## Jouer avec un autre harnais

Pas de Claude Code ? Vous pouvez quand même jouer avec un autre agent (Codex, Crush, Cursor, etc.). Donnez-lui à lire [`.claude/skills/cartouche/SKILL.md`](.claude/skills/cartouche/SKILL.md) comme instructions, puis la cartouche de votre choix. Le skill commence par inventorier ce que le harnais sait faire (shell, questions à options, fichiers, son…) et prévoit une solution de repli pour chaque capacité absente.

**Aucune garantie que vous aurez tous les bells & whistles** : selon le harnais, vous pourriez perdre la console redessinée, les choix cliquables, les vrais dés ou le son. `cartouche-mods`, lui, ne marche que dans Claude Code.

## Écrire sa propre cartouche

Une cartouche, c'est juste un fichier Markdown. Elle peut se résumer à trois pages de lore sans une seule règle, ou à une table de dégâts sans une phrase d'ambiance : le skill comble les trous. Inspirez-vous des trois cartouches présentes, puis lancez `/cartouche ma-cartouche.md`.
