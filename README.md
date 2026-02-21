# 🚀 Frontier Forge - Prototype de Jeu de Gestion 2D

Prototype de jeu de gestion/survie en 2D développé avec Pygame, inspiré de jeux comme EVE Online, Factorio, Oxygen Not Included, et bien d'autres.

## 📋 Description

Frontier Forge est un jeu de gestion de ressources en temps réel où vous devez :
- **Récolter des ressources** (métal, nourriture, énergie)
- **Construire des bâtiments** pour automatiser la production
- **Survivre** aux menaces (zombies, faim)
- **Atteindre la victoire** en construisant une fusée ou en survivant 10 jours

## 🎮 Objectifs de Victoire

Vous pouvez gagner de **deux manières** :
1. **Construire une fusée** (coûte 100 métal + 50 énergie)
2. **Survivre 10 jours** (1 jour = 1 minute de jeu réel)

## 🕹️ Contrôles

| Touche | Action |
|--------|--------|
| **Z Q S D** ou **Flèches** | Déplacer le joueur |
| **Clic gauche** | Récolter une ressource / Placer un bâtiment |
| **1** | Sélectionner Mine (coût : 10 métal) |
| **2** | Sélectionner Ferme (coût : 8 métal) |
| **3** | Sélectionner Générateur (coût : 15 métal) |
| **4** | Sélectionner Tourelle (coût : 20 métal + 10 énergie) |
| **5** | Sélectionner Fusée (coût : 100 métal + 50 énergie) |
| **E** | Manger de la nourriture (restaure 50 faim) |
| **ESC** | Quitter le jeu |

## 🏗️ Bâtiments

| Bâtiment | Coût | Production | Description |
|----------|------|------------|-------------|
| **Mine** | 10 métal | +1 métal/2s | Produit du métal automatiquement |
| **Ferme** | 8 métal | +1 nourriture/2s | Produit de la nourriture |
| **Générateur** | 15 métal | +2 énergie/2s | Produit de l'énergie |
| **Tourelle** | 20 métal + 10 énergie | - | Défend contre les zombies (portée 150px) |
| **Fusée** | 100 métal + 50 énergie | - | Objectif de victoire ! |

## 🌍 Ressources

- **Métal (gris)** : Nécessaire pour construire tous les bâtiments
- **Nourriture (jaune)** : Maintient votre niveau de faim
- **Énergie (orange)** : Nécessaire pour la tourelle et la fusée

## 💀 Survie

- Votre **faim diminue** continuellement (0.5 par seconde)
- Si votre faim atteint 0, vous **perdez de la vie** (5 PV/s)
- Les **zombies apparaissent** toutes les 15 secondes et vous attaquent
- Les **tourelles** défendent automatiquement contre les zombies

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- Pygame 2.5.0 ou supérieur

### Installation des dépendances

```bash
pip install -r requirements.txt
```

Ou manuellement :
```bash
pip install pygame
```

## 🚀 Lancement du jeu

```bash
python main.py
```

## 📁 Structure du Projet

```
ForgeFrontier/
│
├── main.py           # Boucle principale du jeu
├── player.py         # Classe du joueur (mouvement, inventaire, stats)
├── world.py          # Classe du monde (grille, terrain, génération)
├── buildings.py      # Classes des bâtiments (Mine, Ferme, etc.)
├── enemies.py        # Classe des ennemis (Zombies)
├── ui.py             # Interface utilisateur (HUD, menus)
├── constants.py      # Constantes du jeu (couleurs, valeurs, configs)
├── requirements.txt  # Dépendances Python
└── README.md         # Ce fichier
```

## 🎯 Stratégie de Base

1. **Début de partie** :
   - Récoltez du métal (cases grises) en cliquant dessus
   - Construisez des **Mines** pour automatiser la production de métal
   - Récoltez de la nourriture (cases vert foncé) pour ne pas mourir de faim

2. **Milieu de partie** :
   - Construisez des **Fermes** pour automatiser la nourriture
   - Construisez des **Générateurs** pour produire de l'énergie
   - Placez des **Tourelles** pour défendre votre base

3. **Fin de partie** :
   - Accumulez 100 métal + 50 énergie
   - Construisez la **Fusée** pour gagner !
   - Ou survivez jusqu'au jour 10

## 🔧 Personnalisation

Toutes les constantes du jeu sont dans `constants.py` :
- Vitesse du joueur
- Taille de la grille
- Coûts des bâtiments
- Taux de production
- Apparition des zombies
- etc.

N'hésitez pas à modifier ces valeurs pour équilibrer le jeu selon vos préférences !

## 🛠️ Développement Futur

Le code est modulaire et facile à étendre. Idées d'améliorations :
- [ ] Nouveaux types de ressources (bois, pierre, uranium)
- [ ] Plus de bâtiments (hôpital, laboratoire, usine)
- [ ] Différents types d'ennemis (mutants, robots)
- [ ] Système de recherche technologique
- [ ] Sauvegarde/chargement de parties
- [ ] Graphismes améliorés (sprites, animations)
- [ ] Génération procédurale de terrain (rivières, montagnes)
- [ ] Multijoueur coopératif
- [ ] Système de quêtes
- [ ] Commerce avec des PNJ

## 📝 Notes pour Débutants

- Chaque fichier est **commenté en détail** pour faciliter la compréhension
- Les **variables ont des noms explicites** (>5 caractères)
- Le code suit une **architecture claire** (séparation des responsabilités)
- Utilisez ce projet comme **base d'apprentissage** de Pygame !

## 🐛 Dépannage

**Le jeu ne se lance pas :**
- Vérifiez que Pygame est installé : `pip list | grep pygame`
- Vérifiez votre version de Python : `python --version`

**Le jeu est trop difficile/facile :**
- Modifiez les constantes dans `constants.py`
- Par exemple : `ZOMBIE_SPAWN_INTERVAL = 30.0` (zombies moins fréquents)

**Performances faibles :**
- Réduisez `FRAMES_PER_SECOND` dans `constants.py`
- Réduisez `GRID_SIZE` pour une carte plus petite

## 📜 Licence

Ce projet est un prototype éducatif libre d'utilisation.

## 🙏 Crédits

Inspiré par : EVE Online, Factorio, Oxygen Not Included, Workers & Resources,
Age of Empires II, Project Zomboid, Foxhole, KSP, Prison Architect, OpenTTD,
Space Engineers, Kenshi, DayZ, et Big Ambition.

---

**Bon jeu, commandant ! 🚀**
