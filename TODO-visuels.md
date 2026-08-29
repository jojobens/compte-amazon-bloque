# Visuels provisoires à remplacer

Les visuels listés ici sont des **placeholders** générés à la charte par
`tools/generer_visuel_provisoire.py`. Ils portent la mention « visuel provisoire »
sur l'image elle-même. Ils évitent les images cassées en production, mais ils
n'apportent aucune information au lecteur.

Pour remplacer un visuel : produire le fichier définitif au même nom, aux mêmes
dimensions (1200 × 630), le déposer dans `images/blog/`, puis retirer sa ligne
de ce fichier.

---

## Article : Plan d'action Amazon
`blog/plan-action-amazon.html`

| Fichier | Section | Ce que doit montrer la version définitive | État |
|---|---|---|---|
| `images/blog/plan-action-trois-blocs.png` | 2. La structure en trois blocs | Les trois blocs empilés ou côte à côte, chacun occupant un tiers de la surface, avec leur intitulé : cause racine, mesures immédiates, mesures préventives. Le message est la proportion, pas le contenu. | **provisoire** |
| `images/blog/plan-action-cause-racine.png` | 2.1 La cause racine | Deux colonnes côte à côte. À gauche une cause racine mal formulée, annotée pour montrer ce qui manque. À droite la version corrigée, avec date, acteur, mécanisme et conséquence surlignés. | **provisoire** |
| `images/blog/plan-action-six-erreurs.png` | 3. Les six erreurs qui font rejeter | Les six erreurs en grille de six cases numérotées, chacune avec son intitulé court. Lisible en vignette. | **provisoire** |
| `images/blog/plan-action-pieces-jointes.png` | 5. Les pièces à joindre | Le tableau des pièces par type de blocage, en version graphique : cinq lignes, une icône par type, les pièces attendues en regard. | **provisoire** |
| `images/blog/plan-action-apres-refus.png` | 7. Après un premier refus | Un parcours en étapes : lecture de la notification de refus, reprise de la cause racine, contrôle de cohérence des pièces, resoumission, et l'embranchement vers l'escalade. | **provisoire** |

**Couverture, déjà définitive** : `images/blog/plan-action-amazon.png` et sa vignette
`images/blog/plan-action-amazon-vignette.png`, générées par `tools/generer_couverture.py`
avec le motif `document-plan`. Rien à faire.

---

## Charte à respecter pour les versions définitives

Couleurs, sans aucune autre teinte :

| Rôle | Valeur |
|---|---|
| Bleu nuit, fond | `#16233B` |
| Crème, texte sur fond sombre | `#F6F4EF` |
| Blanc cassé | `#FFFDF9` |
| Ambre, accent | `#C97A2E` |
| Rouge, danger | `#A9432F` |
| Vert | `#4B6E52` |

Typographies : **Fraunces** pour les titres, **IBM Plex Sans** pour le texte,
**IBM Plex Mono** pour les étiquettes et les références.

Dimensions : 1200 × 630 pixels. Poids visé sous 25 Ko, obtenu avec
`python3 tools/optimiser_png.py <fichier>` qui réencode en palette indexée.

Chaque image doit rester lisible en vignette de 400 pixels de large.
