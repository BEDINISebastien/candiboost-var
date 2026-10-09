# CandiBoost Var — actualisation automatique

**Fonctionnement :** GitHub Actions exécute `collect.py` à 6 h 15 et 18 h 15 UTC chaque jour. Le script lit les flux RSS configurés, filtre les annonces et actualise `offres.json`. GitHub Pages publie `index.html` pour une consultation depuis le navigateur.

## Mise en service gratuite

1. Créer un dépôt GitHub **public** et y déposer les fichiers et le dossier `.github/workflows` sans modifier leur arborescence.
2. Dans **Settings → Actions → General**, autoriser les workflows et leurs droits d'écriture si nécessaire.
3. Dans **Actions → Actualiser les offres → Run workflow**, déclencher le premier relevé.
4. Dans **Settings → Pages**, sélectionner **Deploy from a branch**, branche `main`, dossier `/ (root)`.
5. Sur [Emploi-Territorial](https://www.emploi-territorial.fr/emploi-mobilite/), filtrer le Var et les métiers, puis utiliser « Flux RSS » ; copier l'URL du flux dans `sources.txt`, une URL par ligne. La veille publique sera alors adaptée à ces recherches.
6. Pour d'autres sources, ajouter uniquement des flux RSS publics valides à `sources.txt`.

**Limites :** la source RSS Remotive peut être inaccessible ou ne contenir aucune annonce pertinente. Les sites comme France Travail, Choisir le service public et certains portails ne fournissent pas toujours un flux public exploitable. Leur intégration complète nécessite leurs API autorisées ou des flux officiels adaptés. Le script n'invente ni offres ni e-mails, n'extrait pas d'adresses personnelles, et ne contourne pas les protections de sites. Les offres ne sont pas garanties exhaustives. Une exécution GitHub Actions peut être retardée ou désactivée après inactivité du dépôt. Les données sont publiques sur un dépôt public : ne pas y mettre son CV, ses contacts privés ou son suivi personnel.

**Important :** ouvrir directement `index.html` sur un ordinateur ne lance pas de recherche internet ; il faut déployer le site et activer le collecteur. Aucun service distant n'a été configuré pour vous.
