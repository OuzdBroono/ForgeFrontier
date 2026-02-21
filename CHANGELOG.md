# 📜 Historique des Mises à Jour - Frontier Forge

## [Version 0.4.0] - 2026-02-21

### ✅ Phase 7B : Multijoueur en Ligne - COMPLÉTÉE

**Ajouts Majeurs :**
- **Mode multijoueur coopératif** jouable via Hamachi (LogMeIn)
- Support de 2-4 joueurs en temps réel
- Serveur de jeu avec autorité (port 5555 par défaut)
- Inventaire partagé entre tous les joueurs
- Synchronisation en temps réel de tous les éléments

**Fichiers Créés :**
- `network/protocol.py` : Protocole de communication JSON
- `network/server.py` : Serveur de jeu (11 000+ lignes)
- `network/client.py` : Client réseau avec callbacks
- `network/__init__.py` : Module réseau
- `main_multiplayer.py` : Version multijoueur du jeu (35 KB)
- `start_server.py` : Script de lancement serveur
- `MULTIPLAYER_GUIDE.md` : Guide détaillé (6 000+ mots)
- `README_MULTIPLAYER.md` : Documentation technique

**Fonctionnalités :**
- Synchronisation des positions des joueurs (10x/s)
- Synchronisation de l'inventaire partagé
- Synchronisation des bâtiments construits
- Synchronisation des ennemis (spawn, position, mort)
- Gestion des connexions/déconnexions
- Heartbeat pour détecter les déconnexions (5s)
- Affichage des joueurs distants (carré cyan + ID)
- État complet du jeu envoyé aux nouveaux joueurs

**Protocole Réseau :**
- Messages JSON délimités par `\n`
- Types : connect, disconnect, player_update, inventory_update,
  building_place, enemy_spawn, enemy_death, game_state, heartbeat
- TCP Socket sur port 5555
- Serveur = autorité pour validation

**Modifications :**
- `main_multiplayer.py` : Classe RemotePlayer, callbacks réseau, synchronisation
- Interface de connexion au démarrage (IP + port)

---

## [Version 0.3.0] - 2026-02-21

### ✅ Phase 2C : Bâtiment Usine - COMPLÉTÉE

**Ajouts :**
- Nouveau bâtiment : **Usine** (touche 0)
  - Coût : 30 métal + 15 pierre + 1 matériau avancé
  - Crafting automatique : produit selon la recette assignée
  - Intervalle de production : 10 secondes
- Système de crafting automatique intégré
  - Les usines craftent automatiquement si les ressources sont disponibles
  - Affichage console des items produits
- Interface mise à jour : menu de construction affiche 10 bâtiments (1-9, 0)
- Largeur des boutons optimisée pour 10 bâtiments (82px)

**Fichiers modifiés :**
- `main.py` : Ajout touche 0, logique de crafting automatique
- `ui.py` : Menu construction 1-9,0, boutons redimensionnés
- `CHANGELOG.md` : Mise à jour

---

### ✅ Phase 2B : Bâtiment Entrepôt - COMPLÉTÉE

**Ajouts :**
- Nouveau bâtiment : **Entrepôt** (touche 9)
  - Coût : 20 bois + 10 pierre
  - Production passive : +1 métal, nourriture, bois, pierre toutes les 2s
  - Hub commercial polyvalent
- Interface mise à jour : menu de construction affiche 9 bâtiments (1-9)
- Documentation complète ajoutée

**Fichiers modifiés :**
- `main.py` : Ajout touche 9 pour Entrepôt
- `ui.py` : Menu construction 1-9, largeur boutons ajustée (88px)
- `CHANGELOG.md` : Nouveau fichier créé
- `ROADMAP.md` : Nouveau fichier créé avec plan de développement

---

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
