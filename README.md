# Tableaux de bord — Photo-expertise IDEA

Pipeline automatique : 2 PDFs Power BI en entrée → une page web par expert en sortie.

## Procédure mensuelle

1. Récupérer les 2 exports Power BI habituels.
2. Les renommer en `ytd.pdf` (cumul YTD) et `mois.pdf` (mois écoulé).
3. Aller dans le dossier `source/` de ce dépôt sur github.com.
4. Glisser-déposer les 2 fichiers (ils écrasent les versions précédentes).
5. Commit. L'action automatique régénère et publie les pages en ~1 minute.

Les URLs des experts ne changent jamais : `https://<ton-compte>.github.io/<nom-du-depot>/expert_APA.html`

## Contenu

- `extract_data.py` — lit les 2 PDFs et calcule la moyenne régionale pondérée
- `generate_pages.py` — produit une page HTML par expert + un index
- `.github/workflows/build.yml` — automatisation GitHub Actions
- `source/` — emplacement des 2 PDFs source
- `_site/` — dossier de sortie (généré, non versionné)

## Filtres et règles

- Experts retenus : volume YTD ≥ 50 EAD
- Moyenne régionale : pondérée par le volume de chaque expert
- Statut (vert / orange / rouge) : calculé sur la valeur YTD selon les seuils plateforme
