# Exports

Les exports sont générés depuis la base SQLite locale et ne sont pas ajoutés au dépôt par défaut.

Formats disponibles via `py -m ia_database export --format <csv|json|xlsx>` :

- `csv` / `json` — liste plate des fiches (voir [`cli.py`](../src/ia_database/cli.py)) ;
- `xlsx` — classeur Excel multi-feuilles généré par
  [`src/ia_database/exporters/xlsx.py`](../src/ia_database/exporters/xlsx.py) :
  Tableau de bord, Catalogue, Categories, Plateformes, Tarifs, Sources, Historique.
