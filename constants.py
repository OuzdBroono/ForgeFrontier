"""
CONSTANTS.PY
============
Ce fichier contient toutes les constantes du jeu (couleurs, tailles, valeurs de base).
Centraliser les constantes facilite les modifications et la maintenance.
"""

# === CONFIGURATION DE LA FENÊTRE ===
SCREEN_WIDTH = 1800  # Largeur de la fenêtre en pixels
SCREEN_HEIGHT = 900  # Hauteur de la fenêtre en pixels
FRAMES_PER_SECOND = 60  # Nombre d'images par seconde (fluidité du jeu)

# === CONFIGURATION DE LA GRILLE ===
GRID_SIZE = 200  # Taille de la grille (20x20 cases)
TILE_SIZE = 32  # Taille d'une case en pixels (32x32)

# === COULEURS (format RGB: Red, Green, Blue) ===
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 100, 0)
COLOR_DARK_GREEN = (0, 100, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_BROWN = (139, 69, 19)
COLOR_GRAY = (100, 100, 100)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_YELLOW = (255, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_LIGHT_BLUE = (173, 216, 230)
COLOR_WOOD_BROWN = (101, 67, 33)  # Marron foncé pour le bois
COLOR_STONE_GRAY = (128, 128, 128)  # Gris clair pour la pierre
COLOR_WATER_BLUE = (30, 144, 255)  # Bleu pour l'eau
COLOR_MOUNTAIN_GRAY = (105, 105, 105)  # Gris foncé pour les montagnes
COLOR_FOREST_GREEN = (34, 139, 34)  # Vert forêt
COLOR_DESERT_YELLOW = (255, 222, 173)  # Jaune désert

# === TYPES DE TERRAIN ===
TERRAIN_GRASS = 'grass'  # Herbe (terrain normal)
TERRAIN_METAL = 'metal'  # Filon de métal à récolter
TERRAIN_FOOD = 'food'  # Source de nourriture (arbre fruitier)
TERRAIN_WOOD = 'wood'  # Source de bois (forêt)
TERRAIN_STONE = 'stone'  # Gisement de pierre
TERRAIN_WATER = 'water'  # Eau (obstacle non-franchissable)
TERRAIN_MOUNTAIN = 'mountain'  # Montagne (obstacle non-franchissable)
TERRAIN_FOREST = 'forest'  # Forêt (contient du bois)
TERRAIN_DESERT = 'desert'  # Désert (terrain stérile)
TERRAIN_ENERGY_CRYSTAL = 'energy_crystal'  # Cristal d'énergie (trouvé dans le désert)

# === TYPES DE RESSOURCES ===
RESOURCE_METAL = 'metal'  # Métal pour construire
RESOURCE_FOOD = 'food'  # Nourriture pour survivre
RESOURCE_ENERGY = 'energy'  # Énergie pour alimenter les bâtiments
RESOURCE_WOOD = 'wood'  # Bois pour construire
RESOURCE_STONE = 'stone'  # Pierre pour construire

# Ressources craftées
CRAFTING_RESOURCE_TOOLS = 'tools'  # Outils craftés
CRAFTING_RESOURCE_COMPONENTS = 'components'  # Composants
CRAFTING_RESOURCE_MEDICINE = 'medicine'  # Médecine
CRAFTING_RESOURCE_ADVANCED_MATERIALS = 'advanced_materials'  # Matériaux avancés

# === STATISTIQUES DU JOUEUR ===
PLAYER_INITIAL_HEALTH = 100  # Points de vie de départ
PLAYER_INITIAL_HUNGER = 100  # Niveau de faim de départ (100 = pas faim)
PLAYER_HUNGER_DECREASE_RATE = 0.5  # Vitesse de diminution de la faim par seconde
PLAYER_HARVEST_AMOUNT = 5  # Quantité récoltée par clic
PLAYER_MOVEMENT_SPEED = 5  # Vitesse de déplacement (pixels par frame)

# Bonus des objets craftés
TOOL_HARVEST_MULTIPLIER = 2.0  # Les outils doublent la récolte
MEDICINE_HEAL_AMOUNT = 30  # Quantité de vie restaurée par médecine

# Effets du terrain
DESERT_SPEED_PENALTY = 0.5  # Multiplicateur de vitesse dans le désert
RESOURCE_RESPAWN_TIME = 30.0  # Temps de respawn des ressources en secondes

# Cycle jour/nuit
DAY_PHASE_DURATION = 0.6  # 60% du jour est le jour
NIGHT_PHASE_DURATION = 0.4  # 40% du jour est la nuit
NIGHT_TINT_COLOR = (0, 0, 80)  # Bleu foncé pour la nuit
NIGHT_TINT_ALPHA = 120  # Transparence de l'overlay de nuit
NIGHT_ENEMY_SPAWN_MULTIPLIER = 2.0  # Ennemis apparaissent 2x plus vite la nuit

# === BÂTIMENTS - Coûts de construction ===
BUILDING_MINE_COST = {RESOURCE_METAL: 10}  # Coût d'une mine
BUILDING_FARM_COST = {RESOURCE_METAL: 8}  # Coût d'une ferme
BUILDING_GENERATOR_COST = {RESOURCE_METAL: 15}  # Coût d'un générateur
BUILDING_TURRET_COST = {RESOURCE_METAL: 20, RESOURCE_ENERGY: 10}  # Coût d'une tourelle
BUILDING_ROCKET_COST = {RESOURCE_METAL: 100, RESOURCE_ENERGY: 50}  # Coût de la fusée (victoire)
BUILDING_HOSPITAL_COST = {RESOURCE_METAL: 15, RESOURCE_WOOD: 20}  # Coût d'un hôpital
BUILDING_LABORATORY_COST = {RESOURCE_METAL: 25, RESOURCE_STONE: 15, RESOURCE_ENERGY: 10}  # Coût d'un laboratoire
BUILDING_WALL_COST = {RESOURCE_STONE: 10, RESOURCE_WOOD: 5}  # Coût d'un mur
BUILDING_WAREHOUSE_COST = {RESOURCE_WOOD: 20, RESOURCE_STONE: 10}  # Coût d'un entrepôt
BUILDING_FACTORY_COST = {RESOURCE_METAL: 30, RESOURCE_STONE: 15, 'advanced_materials': 1}  # Coût d'une usine

# === BÂTIMENTS - Production par tick ===
BUILDING_MINE_PRODUCTION = 1  # Métal produit par tick
BUILDING_FARM_PRODUCTION = 1  # Nourriture produite par tick
BUILDING_GENERATOR_PRODUCTION = 2  # Énergie produite par tick
PRODUCTION_TICK_INTERVAL = 2.0  # Intervalle de production en secondes
HOSPITAL_HEAL_RATE = 2  # Points de vie soignés par tick
LABORATORY_RESEARCH_INTERVAL = 5.0  # Intervalle de recherche en secondes
WALL_DURABILITY = 100  # Points de durabilité d'un mur
WAREHOUSE_PRODUCTION = 1  # Ressources produites par tick par l'entrepôt
FACTORY_PRODUCTION_INTERVAL = 10.0  # Intervalle de production de l'usine en secondes

# Niveaux de recherche (débloqués par le laboratoire)
RESEARCH_LEVELS = {
    1: {'name': 'Outils Améliorés', 'effect': 'harvest_bonus', 'value': 2},
    2: {'name': 'Tourelles Renforcées', 'effect': 'turret_damage_bonus', 'value': 5},
    3: {'name': 'Production Optimisée', 'effect': 'production_bonus', 'value': 1},
    4: {'name': 'Soins Améliorés', 'effect': 'heal_bonus', 'value': 1},
    5: {'name': 'Efficacité Énergétique', 'effect': 'energy_bonus', 'value': 1}
}

# === ENNEMIS ===
# Zombies (ennemis standards)
ZOMBIE_SPAWN_INTERVAL = 15.0  # Intervalle d'apparition des zombies (secondes)
ZOMBIE_DAMAGE = 10  # Dégâts infligés par un zombie
ZOMBIE_SPEED = 1  # Vitesse de déplacement des zombies
ZOMBIE_HEALTH = 30  # Points de vie d'un zombie

# Mutants (ennemis tanks : lents mais résistants)
MUTANT_SPAWN_INTERVAL = 25.0  # Intervalle d'apparition des mutants (secondes)
MUTANT_DAMAGE = 15  # Dégâts infligés par un mutant
MUTANT_SPEED = 1  # Vitesse de déplacement des mutants (plus lent)
MUTANT_HEALTH = 60  # Points de vie d'un mutant (double des zombies)
COLOR_MUTANT_GREEN = (0, 180, 0)  # Vert pour les mutants

# Loups (ennemis rapides en meutes)
WOLF_SPAWN_INTERVAL = 20.0  # Intervalle d'apparition des loups (secondes)
WOLF_DAMAGE = 8  # Dégâts infligés par un loup (moins que zombie)
WOLF_SPEED = 1  # Vitesse de déplacement des loups (très rapide)
WOLF_HEALTH = 20  # Points de vie d'un loup (moins que zombie)
COLOR_WOLF_BROWN = (139, 90, 43)  # Marron pour les loups

# Tourelles
TURRET_DAMAGE = 15  # Dégâts d'une tourelle
TURRET_RANGE = 150  # Portée de tir d'une tourelle (en pixels)

# === OBJECTIFS DE VICTOIRE ===
SURVIVAL_DAYS_TO_WIN = 10  # Nombre de jours à survivre
SECONDS_PER_DAY = 60  # Durée d'un jour en secondes (1 minute = 1 jour)

# === GÉNÉRATION DE RESSOURCES ===
WOOD_SOURCES_COUNT = 10  # Nombre de sources de bois sur la carte
STONE_SOURCES_COUNT = 8  # Nombre de gisements de pierre sur la carte
