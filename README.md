# Recipe SEO Radar FREE

Veille SEO automatisée et gratuite de recettes recherchées aux États-Unis, toutes catégories, sans porc.

## Utilisation

1. Ouvrir **Actions** dans GitHub.
2. Cliquer **Recipe SEO Radar FREE** → **Run workflow**.
3. Lire le rapport **reports/latest.md** et télécharger **reports/latest.csv** dans Code.

Une exécution quotidienne vise 7h heure **Africa/Casablanca**. GitHub Actions peut retarder les exécutions ; aucune précision à la minute n'est garantie.

## Ce que la version gratuite fait

- Découverte étendue via Google Autocomplete USA et sources Google Trends publiques si accessibles.
- Analyse expérimentale de tendance sur 90 jours avec pytrends (non officiel et parfois bloqué).
- Pré-analyse facultative de résultats Bing RSS : **ne correspond pas à un classement Google USA**.
- Filtre des recettes liées au porc, déduplication et rapports Markdown + CSV.
- Aucune clé API ni carte bancaire. Exécution avec GitHub Actions sur le dépôt public.

## Limites importantes

Google Autocomplete ne fournit ni volume mensuel ni KD. Google Trends fournit un indice relatif, pas un volume. Pytrends peut échouer (429), et Bing RSS ne remplace pas la SERP Google. Le rapport doit explicitement marquer toutes les métriques absentes comme **non vérifiées**. La concurrence « quasi zéro » ne peut pas être garantie sans analyse Google USA approfondie. Le filtre sans porc doit être contrôlé avant publication. Les pistes proposées ne garantissent pas de trafic.

## Exécution locale (optionnelle)

Installer Python 3.11+, puis lancer :

    pip install -r requirements.txt
    python radar.py --self-test
    python radar.py

## Organisation

- radar.py : collecte, filtrage, tendances, classement, rapport
- .github/workflows/radar.yml : lancement manuel et récurrent
- reports/latest.md : rapport exploitable
- reports/latest.csv : données exportables
- data/seen.json : historique anti-répétition

Projet original inspiré des méthodes de découverte de mots-clés des dépôts open source présentés par l'utilisateur. Aucun code tiers n'est directement copié.
