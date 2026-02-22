# 🗺️ Plan de Mises à Jour - Frontier Forge

## 🚀 Vision du Projet
Frontier Forge vise à devenir un jeu de gestion/survie 2D riche et profond, combinant la construction de base, la gestion de ressources, et la défense contre des vagues d'ennemis.

---

## ✅ Phase 2 : Expansion des Bâtiments - COMPLÉTÉE

### ✅ Phase 2A : Bâtiment Mur - COMPLÉTÉE
- [x] Implémentation de la classe Wall
- [x] Intégration dans le menu de construction (touche 8)
- [x] Interaction avec les ennemis (attaque/destruction)
- [x] Barre de durabilité
- [x] Tests et validation

### ✅ Phase 2B : Bâtiment Entrepôt - COMPLÉTÉE
- [x] Vérification de l'implémentation de la classe Warehouse
- [x] Ajout au menu de construction (touche 9)
- [x] Interface utilisateur mise à jour (1-9)
- [x] Tests de production passive
- [x] Documentation (CHANGELOG.md, ROADMAP.md créés)

### ✅ Phase 2C : Bâtiment Usine - COMPLÉTÉE
- [x] Vérification de l'implémentation de la classe Factory
- [x] Ajout au menu de construction (touche 0)
- [x] Système de crafting automatique intégré
- [x] Gestion des recettes assignées
- [x] Tests de crafting automatique
- [x] Documentation mise à jour

---

## 📋 Phase 3 : Intelligence Artificielle Avancée

### Phase 3A : Pathfinding
- [ ] Implémentation de l'algorithme A* ou Dijkstra
- [ ] Les ennemis contournent les obstacles (murs, bâtiments)
- [ ] Optimisation pour éviter les calculs coûteux
- [ ] Visualisation des chemins (mode debug)

### Phase 3B : Comportements d'Ennemis Avancés
- [ ] Formation en meute pour les loups
- [ ] Ciblage prioritaire (tourelles > hôpital > générateur > joueur)
- [ ] Attaques coordonnées
- [ ] Boss ennemis avec patterns spéciaux

### Phase 3C : PNJ Alliés
- [ ] Colons qui rejoignent la base
- [ ] Assignation de tâches (récolte, construction, défense)
- [ ] Système de moral et besoins
- [ ] Commerce avec caravanes

---

## 📋 Phase 4 : Système de Progression

### Phase 4A : Arbre Technologique
- [ ] Interface d'arbre de technologies
- [ ] Déblocage de nouveaux bâtiments via recherche
- [ ] Prérequis entre technologies
- [ ] Coûts de recherche évolutifs

### Phase 4B : Niveaux et Expérience
- [ ] Système XP pour le joueur
- [ ] Compétences à débloquer (vitesse, récolte, santé)
- [ ] Points de compétence à distribuer
- [ ] Spécialisations (Combat, Construction, Survie)

### Phase 4C : Quêtes et Objectifs
- [ ] Système de quêtes dynamiques
- [ ] Récompenses (ressources, XP, blueprints)
- [ ] Quêtes principales et secondaires
- [ ] Journal de quêtes dans l'interface

---

## 📋 Phase 5 : Contenu et Diversité

### Phase 5A : Nouveaux Biomes
- [ ] Toundra glacée (ralentit le joueur, cristaux de glace)
- [ ] Marais toxique (dégâts continus, champignons rares)
- [ ] Cavernes souterraines (minerais rares, ennemis puissants)
- [ ] Ruines anciennes (artefacts, puzzles)

### Phase 5B : Nouveaux Ennemis
- [ ] Robots mécaniques (résistants aux balles, faibles à l'EMP)
- [ ] Créatures volantes (évitent les murs)
- [ ] Boss de zone avec mécaniques uniques
- [ ] Events d'invasion (hordes massives)

### Phase 5C : Nouveaux Bâtiments
- [ ] Système de défense avancé (lance-missiles, champ de force)
- [ ] Raffinerie (transforme ressources basiques en avancées)
- [ ] Dôme hydroponique (production massive de nourriture)
- [ ] Télépporteur (déplacement rapide sur la carte)
- [ ] Centre de commandement (donne vision globale)

---

## 📋 Phase 6 : Polissage et Graphismes

### Phase 6A : Assets Visuels
- [ ] Sprites personnalisés pour tous les bâtiments
- [ ] Animations de construction
- [ ] Particules (fumée, explosions, étincelles)
- [ ] Effets météo (pluie, neige, tempête de sable)

### Phase 6B : Audio
- [ ] Musique d'ambiance (jour/nuit/combat)
- [ ] Effets sonores (construction, récolte, combat)
- [ ] Sons d'environnement (vent, eau, oiseaux)

### Phase 6C : Interface Utilisateur
- [ ] Menus animés
- [ ] Tooltips détaillés
- [ ] Minimap avec fog of war
- [ ] Notifications et alertes visuelles

---

## 🚧 Phase 7 : Multijoueur - EN COURS

### ✅ Phase 7B : Multijoueur en Ligne - COMPLÉTÉE (Partielle)
- [x] Serveur dédié (TCP Socket)
- [x] Synchronisation réseau (JSON Protocol)
- [x] Mode coopératif (2-4 joueurs)
- [x] Support Hamachi/VPN
- [x] Inventaire partagé
- [x] Synchronisation bâtiments (corrigée 2026-02-21)
- [x] Callbacks ennemis (ajoutés 2026-02-21)
- [x] Documentation complète

### 🔥 Phase 7B-Fix : Corrections Synchronisation - EN COURS
**Statut** : 🟡 Implémentation complétée, tests en attente
- [x] Fix duplication bâtiments (commit 10a3da3)
- [x] Fix duplication inventaire (commit 10a3da3)
- [x] Ajout callbacks ennemis (commit 10a3da3)
- [x] Synchronisation cycle jour/nuit (commit 1176e80 - 2026-02-23)
- [x] Logs debug pour diagnostic (commit 1176e80 - 2026-02-23)
- [x] Fenêtre adaptative + F11 plein écran (commit 3b95170 - 2026-02-23)
- [ ] Tests complets 2 joueurs (validation logs debug)
- [ ] Tests complets 4 joueurs
- [ ] Suppression logs debug après validation

**Note** : Le code de dessin des RemotePlayer est déjà présent (lignes 859-862). Les logs debug permettront de vérifier si les callbacks sont appelés correctement.

### 📋 Phase 7A : Coopération Locale (Split-Screen) - REPORTÉE
- [ ] Split-screen 2 joueurs
- [ ] Inventaires séparés option
- [ ] Objectifs communs

### 📋 Phase 7C : Améliorations Multijoueur - REPORTÉE (après 7B-Fix)
- [ ] Chat textuel in-game
- [ ] Lobby de sélection
- [ ] Mode compétitif (bases rivales)
- [ ] Interpolation de mouvement (smooth)
- [ ] Prédiction côté client
- [ ] Compression de données
- [ ] Anti-cheat avancé
- [ ] Reconnexion automatique
- [ ] Spectateurs

---

## 📋 Phase 8 : Méta-Jeu et Rejouabilité

### Phase 8A : Modes de Jeu Alternatifs
- [ ] Mode Survie infini (vagues croissantes)
- [ ] Mode Sandbox (ressources illimitées)
- [ ] Mode Speedrun (chronomètre, classement)
- [ ] Défis hebdomadaires

### Phase 8B : Système de Seeds
- [ ] Génération de monde avec seed
- [ ] Partage de seeds entre joueurs
- [ ] Seeds thématiques (désert infini, archipel, etc.)

### Phase 8C : Mods et Customisation
- [ ] Support de mods (nouveaux bâtiments, ennemis)
- [ ] Éditeur de niveau
- [ ] Workshop communautaire

---

## 🎯 Priorités Actuelles (Mise à jour 2026-02-21)

### 🔥 URGENT (À faire IMMÉDIATEMENT)
1. **Phase 7B-Fix** : Corriger affichage joueurs distants (CRITIQUE)
   - Ajouter draw() des remote_players dans boucle de rendu
   - Vérifier affichage ennemis synchronisés
   - Synchroniser cycle jour/nuit

2. **Feature** : Fenêtre adaptative (CODE PRÊT, non committé)
   - Tester modifications
   - Commit "Fenêtre adaptative + plein écran (F11)"

### 📋 MOYEN TERME
3. **Phase 3A** : Pathfinding pour les ennemis
4. **Phase 6A** : Améliorer les graphismes de base
5. **Phase 4A** : Arbre technologique
6. **Phase 5A** : Nouveaux biomes

---

## 📊 Métriques de Succès

- [ ] Boucle de gameplay engageante (30+ minutes de jeu)
- [ ] Équilibrage : victoire atteignable mais challengeante
- [ ] Code maintenable et bien documenté
- [ ] Performance stable (60 FPS)
- [ ] Feedback positif des joueurs testeurs

---

## 💡 Idées en Vrac (Backlog)

- Système de saisons (été/hiver affectent les ressources)
- Événements aléatoires (météorite, éclipse, aurora)
- Pets/Animaux domestiques qui aident
- Système de réputation avec factions
- Artefacts légendaires avec effets uniques
- Mode photo pour capturer de belles bases
- Statistiques détaillées de fin de partie

---

**Dernière mise à jour** : 2026-02-21 23:30
**Version actuelle** : 0.4.1-dev (Corrections multijoueur en cours)
**Dernier commit** : 10a3da3 (Phase 7B Fix : Correction synchronisation)
**Prochaine version** : 0.4.2 (Phase 7B-Fix complète) puis 0.5.0 (Fenêtre adaptative)

**⚠️ FICHIER SESSION** : Voir `SESSION_2026-02-21.md` pour détails complets
