# MFC - Reference Produit

## Positionnement confirme

MFC est un espace de pilotage pour etudiants en finance qui centralise candidatures, ressources, echeances, objectifs et contacts. L'application ne remplace pas LinkedIn, les plateformes d'emploi ou Google Drive: elle organise les liens et les informations autour de la recherche de stage ou premier emploi.

## Perimetre livre

- Tableau de bord avec actions urgentes, prochaines echeances, progression des objectifs et statistiques rapides.
- Candidatures avec saisie manuelle, statuts de pipeline, priorite, dates, liens, contacts et notes.
- Vue Kanban et vue liste filtrable pour les candidatures.
- Bibliotheque de ressources sous forme de liens externes classes par categorie, tags et domaine finance.
- Calendrier interne pour deadlines, entretiens, tests, networking, relances et taches.
- Objectifs avec echeance, progression, statut et prochaine etape.
- Contacts professionnels sous forme de mini-CRM.
- Statistiques utiles: volume, statut, domaine, taux entretien et progression.
- Export CSV des donnees.

## Choix MVP

- Stack simple: Streamlit, Pandas et SQLite.
- Donnees saisies manuellement.
- Pas de stockage de fichiers: les documents restent des liens externes.
- Pas d'IA, pas de synchronisation calendrier, pas d'automatisation complexe.
- Donnees de demonstration finance chargees automatiquement au premier lancement.

## Limites connues

- SQLite local convient a une demo ou un usage individuel, mais pas a une application multi-utilisateur.
- L'authentification n'est pas incluse dans cette version.
- Les fichiers personnels ne sont pas heberges par l'application.
- Les integrations LinkedIn, Drive, calendrier et email sont reportees.

## Evolution recommandee

1. Ajouter une authentification.
2. Remplacer SQLite par une base geree.
3. Ajouter une gestion par utilisateur.
4. Ajouter des exports plus structures.
5. Ajouter ensuite des integrations externes, seulement si l'usage manuel est valide.
