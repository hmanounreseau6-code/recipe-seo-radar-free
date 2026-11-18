# Recipe SEO Radar FREE

Veille SEO automatisée et gratuite de recettes recherchées aux États-Unis, toutes catégories, sans porc.

## Utilisation

1. Ouvrir **Actions** dans GitHub.
2. Cliquer **Recipe SEO Radar FREE** → **Run workflow**.
3. Lire **reports/latest.md** : 10 familles de recettes et meilleurs angles Rising identifiés.
4. Ouvrir **reports/angles.csv** : toutes les requêtes associées (Rising, Top ou suggestions Autocomplete) avec liens Google Trends USA et recherche Google pour inspecter les concurrents.
5. Utiliser **reports/latest.csv** comme récapitulatif.

Une exécution quotidienne vise 7h heure **Africa/Casablanca**. GitHub Actions peut retarder les exécutions ; aucune précision à la minute n'est garantie.

## Ce que la version gratuite fait

- Découverte étendue via Google Autocomplete USA et sources Google Trends publiques si accessibles.
- Pour chaque keyword choisi : interrogation des **requêtes associées Google Trends USA (Rising et Top)** ; si l'expression exacte est trop rare, nouvelle interrogation du sujet parent en le signalant.
- Séparation des angles liés à la recette et des recettes indépendantes qui apparaissent dans les recherches associées.
- Un angle n'est proposé comme Rising que si Google Trends le renvoie réellement ; les alternatives Google Autocomplete restent **non vérifiées**.
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
- reports/latest.csv : synthèse exportable
- reports/angles.csv : toutes les variantes et leurs preuves / liens de vérification
- data/seen.json : historique anti-répétition

Projet original inspiré des méthodes de découverte de mots-clés des dépôts open source présentés par l'utilisateur. Aucun code tiers n'est directement copié.

## Interprétation des angles

Une forte progression relative (y compris Breakout ou +175 200 %) peut provenir d'un volume initial quasi nul. L'angle n'est **pas automatiquement facile à classer** : vérifier les 10 résultats organiques Google USA, notamment l'intention de recherche, les recettes exactes déjà publiées et les grands médias culinaires. L'outil gratuit peut échouer à lire Google Trends suite aux limites anti-automatisation ; dans ce cas, ouvrir les liens Google Trends du rapport et vérifier les requêtes Rising manuellement.
