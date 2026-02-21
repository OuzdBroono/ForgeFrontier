# 📜 Historique des Mises à Jour - Frontier Forge

## [Version 0.2.0] - 2026-02-21

### ✅ Phase 2A : Bâtiment Mur - COMPLÉTÉE

**Ajouts :**
- Nouveau bâtiment : **Mur** (touche 8)
  - Coût : 10 pierre + 5 bois
  - Durabilité : 100 points
  - Barre de santé visible au-dessus du mur
- Les ennemis détectent et attaquent les murs en priorité
  - Portée de détection : 50 pixels
  - Les murs bloquent les ennemis
  - Les murs détruits sont automatiquement retirés
- Interface mise à jour : menu de construction affiche maintenant 8 bâtiments (1-8)
- Aide des contrôles mise à jour

**Fichiers modifiés :**
- `main.py` : Ajout touche 8, passage de buildings_list aux ennemis, suppression des murs détruits
- `ui.py` : Menu construction 1-8, largeur boutons ajustée
- `enemies.py` : Logique d'attaque des murs implémentée
- `buildings.py` : Classe Wall (déjà existante)
- `constants.py` : Constantes Wall (déjà existantes)

---

## [Version 0.1.0] - 2026-02-19 à 2026-02-21

### 🎮 Version Initiale

**Fonctionnalités de base :**
- Système de jeu de gestion/survie 2D avec Pygame
- Système de ressources : métal, nourriture, énergie, bois, pierre
- Génération procédurale de terrain (lacs, montagnes, forêts, déserts)
- Cycle jour/nuit avec spawn accéléré des ennemis la nuit

**Bâtiments de production :**
- Mine (touche 1) : Produit du métal
- Ferme (touche 2) : Produit de la nourriture
- Générateur (touche 3) : Produit de l'énergie

**Bâtiments défensifs :**
- Tourelle (touche 4) : Attaque les ennemis à portée

**Bâtiments spéciaux :**
- Fusée (touche 5) : Objectif de victoire
- Hôpital (touche 6) : Soigne le joueur automatiquement
- Laboratoire (touche 7) : Système de recherche avec 5 niveaux

**Bâtiments avancés (Phase 1) :**
- Entrepôt : Produit passivement toutes les ressources
- Usine : Automatise le crafting

**Système d'ennemis :**
- Zombies : Ennemis standards
- Mutants : Tanks lents mais résistants
- Loups : Rapides, apparaissent en meute

**Systèmes annexes :**
- Crafting : Outils, composants, médecine, matériaux avancés
- Sauvegarde/Chargement (F5/F9)
- Respawn des ressources
- Statistiques de jeu
- Interface utilisateur complète

**Objectifs de victoire :**
- Construire la fusée (100 métal + 50 énergie)
- Survivre 10 jours (1 jour = 1 minute)

---

## Légende

- ✅ Fonctionnalité complétée
- 🚧 En cours de développement
- 📋 Planifiée
- 🐛 Correction de bug
- ⚡ Amélioration de performance
- 🎨 Amélioration visuelle
