"""
BUILDINGS.PY
============
Ce fichier contient toutes les classes de bâtiments.
Chaque bâtiment a un coût, une position, et peut produire des ressources.
"""

import pygame
import math
from constants import *
from sprite_loader import SpriteLoader


class Building:
    """Classe de base pour tous les bâtiments"""

    def __init__(self, grid_x, grid_y, building_name, building_color, sprite_filename=None):
        """
        Initialise un bâtiment
        Args:
            grid_x, grid_y: Position dans la grille
            building_name: Nom du bâtiment
            building_color: Couleur du bâtiment (RGB)
            sprite_filename: Nom du fichier sprite (optionnel)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.building_name = building_name
        self.building_color = building_color
        self.production_timer = 0  # Timer pour la production automatique

        # Charger le sprite si fourni
        if sprite_filename:
            self.sprite = SpriteLoader.load_sprite(
                sprite_filename,
                size=(TILE_SIZE, TILE_SIZE),
                fallback_color=building_color
            )
        else:
            self.sprite = SpriteLoader.create_placeholder_sprite((TILE_SIZE, TILE_SIZE), building_color)

    def update(self, delta_time, player_inventory):
        """
        Met à jour le bâtiment (à surcharger dans les sous-classes)
        Args:
            delta_time: Temps écoulé depuis la dernière frame
            player_inventory: Inventaire du joueur (pour ajouter les ressources)
        """
        pass

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Dessine le bâtiment à l'écran
        Args:
            screen: Surface Pygame
            camera_offset_x, camera_offset_y: Décalage de la caméra
        """
        # Calculer la position en pixels
        pixel_x = self.grid_x * TILE_SIZE - camera_offset_x
        pixel_y = self.grid_y * TILE_SIZE - camera_offset_y

        # Dessiner le bâtiment
        building_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.building_color, building_rect)
        pygame.draw.rect(screen, COLOR_WHITE, building_rect, 2)


class Mine(Building):
    """Mine : produit du métal automatiquement"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Mine", COLOR_DARK_GRAY, 'mine.png')

    def update(self, delta_time, player_inventory):
        """Produit du métal à intervalle régulier"""
        self.production_timer += delta_time

        # Produire du métal tous les X secondes
        if self.production_timer >= PRODUCTION_TICK_INTERVAL:
            self.production_timer = 0
            production = BUILDING_MINE_PRODUCTION
            # Bonus de recherche niveau 3 : Production Optimisée
            if player_inventory.get('_research_level', 0) >= 3:
                production += 1
            player_inventory[RESOURCE_METAL] += production


class Farm(Building):
    """Ferme : produit de la nourriture automatiquement"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Ferme", COLOR_YELLOW, 'farm.png')

    def update(self, delta_time, player_inventory):
        """Produit de la nourriture à intervalle régulier"""
        self.production_timer += delta_time

        if self.production_timer >= PRODUCTION_TICK_INTERVAL:
            self.production_timer = 0
            production = BUILDING_FARM_PRODUCTION
            # Bonus de recherche niveau 3 : Production Optimisée
            if player_inventory.get('_research_level', 0) >= 3:
                production += 1
            player_inventory[RESOURCE_FOOD] += production


class Generator(Building):
    """Générateur : produit de l'énergie automatiquement"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Générateur", COLOR_ORANGE, 'generator.png')

    def update(self, delta_time, player_inventory):
        """Produit de l'énergie à intervalle régulier"""
        self.production_timer += delta_time

        if self.production_timer >= PRODUCTION_TICK_INTERVAL:
            self.production_timer = 0
            production = BUILDING_GENERATOR_PRODUCTION
            # Bonus de recherche niveau 3 : Production Optimisée
            if player_inventory.get('_research_level', 0) >= 3:
                production += 1
            # Bonus de recherche niveau 5 : Efficacité Énergétique
            if player_inventory.get('_research_level', 0) >= 5:
                production += 1
            player_inventory[RESOURCE_ENERGY] += production


class Turret(Building):
    """Tourelle : défend contre les ennemis"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Tourelle", COLOR_RED, 'turret.png')
        self.shoot_cooldown = 0  # Temps avant de pouvoir tirer à nouveau

    def update(self, delta_time, player_inventory):
        """Met à jour le cooldown de tir"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= delta_time

    def attack_enemies(self, enemies_list, delta_time):
        """
        Attaque les ennemis à portée
        Args:
            enemies_list: Liste des ennemis dans le jeu
            delta_time: Temps écoulé
        """
        # Ne peut tirer que si le cooldown est terminé
        if self.shoot_cooldown <= 0:
            # Position de la tourelle en pixels
            turret_pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
            turret_pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2

            # Chercher un ennemi à portée
            for enemy in enemies_list:
                # Calculer la distance
                distance_x = enemy.position_x - turret_pixel_x
                distance_y = enemy.position_y - turret_pixel_y
                distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

                # Si l'ennemi est à portée, tirer
                if distance <= TURRET_RANGE:
                    enemy.take_damage(TURRET_DAMAGE)
                    self.shoot_cooldown = 1.0  # 1 seconde de cooldown
                    break  # Une tourelle tire sur un seul ennemi à la fois

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """Dessine la tourelle avec un indicateur de portée"""
        super().draw(screen, camera_offset_x, camera_offset_y)

        # Dessiner la portée de la tourelle (cercle semi-transparent)
        turret_center_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2 - camera_offset_x
        turret_center_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2 - camera_offset_y

        # Cercle de portée (rouge transparent)
        range_surface = pygame.Surface((TURRET_RANGE * 2, TURRET_RANGE * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (255, 0, 0, 30), (TURRET_RANGE, TURRET_RANGE), TURRET_RANGE)
        screen.blit(range_surface, (turret_center_x - TURRET_RANGE, turret_center_y - TURRET_RANGE))


class Rocket(Building):
    """Fusée : objectif de victoire du jeu"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Fusée", COLOR_PURPLE, 'rocket.png')
        self.is_victory_condition = True  # Marque comme objectif de victoire

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """Dessine la fusée (plus grande que les autres bâtiments)"""
        pixel_x = self.grid_x * TILE_SIZE - camera_offset_x
        pixel_y = self.grid_y * TILE_SIZE - camera_offset_y

        # Fusée prend 2x2 cases
        rocket_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE * 2, TILE_SIZE * 2)
        pygame.draw.rect(screen, self.building_color, rocket_rect)
        pygame.draw.rect(screen, COLOR_YELLOW, rocket_rect, 3)


class Hospital(Building):
    """Hôpital : soigne le joueur automatiquement"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Hôpital", COLOR_LIGHT_BLUE, 'hospital.png')

    def update(self, delta_time, player_inventory):
        """Produit des soins pour le joueur"""
        self.production_timer += delta_time
        if self.production_timer >= PRODUCTION_TICK_INTERVAL:
            self.production_timer = 0
            # Utiliser une clé spéciale dans l'inventaire pour stocker les soins
            if '_hospital_heal' not in player_inventory:
                player_inventory['_hospital_heal'] = 0
            heal_amount = HOSPITAL_HEAL_RATE
            # Bonus de recherche niveau 4 : Soins Améliorés
            if player_inventory.get('_research_level', 0) >= 4:
                heal_amount += 1
            player_inventory['_hospital_heal'] += heal_amount


class Laboratory(Building):
    """Laboratoire : effectue des recherches (système extensible)"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Laboratoire", COLOR_PURPLE, 'laboratory.png')
        self.research_timer = 0
        self.research_level = 0

    def update(self, delta_time, player_inventory):
        """Effectue des recherches périodiquement"""
        self.research_timer += delta_time
        if self.research_timer >= LABORATORY_RESEARCH_INTERVAL:
            self.research_timer = 0
            self.research_level += 1
            # Stocker le niveau de recherche dans l'inventaire pour accès global
            player_inventory['_research_level'] = self.research_level

            # Afficher le nom de la recherche débloquée
            if self.research_level in RESEARCH_LEVELS:
                research_info = RESEARCH_LEVELS[self.research_level]
                print(f"🔬 Recherche complétée ! {research_info['name']} (Niveau {self.research_level})")
            else:
                print(f"Recherche niveau {self.research_level} complétée !")


class Wall(Building):
    """Mur : bloque les ennemis et peut être détruit"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Mur", COLOR_STONE_GRAY, 'wall.png')
        self.is_obstacle = True  # Flag pour le pathfinding (Phase 3)
        self.durability = WALL_DURABILITY

    def take_damage(self, damage_amount):
        """
        Le mur subit des dégâts
        Args:
            damage_amount: Quantité de dégâts
        Returns:
            bool: True si le mur est détruit, False sinon
        """
        self.durability -= damage_amount
        return self.durability <= 0

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """Dessine le mur avec barre de durabilité"""
        super().draw(screen, camera_offset_x, camera_offset_y)

        # Barre de durabilité
        pixel_x = self.grid_x * TILE_SIZE - camera_offset_x
        pixel_y = self.grid_y * TILE_SIZE - camera_offset_y
        durability_pct = self.durability / WALL_DURABILITY

        # Fond barre (marron)
        pygame.draw.rect(screen, COLOR_BROWN, (pixel_x, pixel_y - 6, TILE_SIZE, 4))
        # Barre de durabilité (vert)
        pygame.draw.rect(screen, COLOR_GREEN, (pixel_x, pixel_y - 6, TILE_SIZE * durability_pct, 4))


class Warehouse(Building):
    """Entrepôt : augmente capacité ou produit passivement des ressources"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Entrepôt", COLOR_WOOD_BROWN, 'warehouse.png')

    def update(self, delta_time, player_inventory):
        """Produit passivement un peu de toutes les ressources (hub commercial)"""
        self.production_timer += delta_time
        if self.production_timer >= PRODUCTION_TICK_INTERVAL:
            self.production_timer = 0
            # Produire un peu de chaque ressource
            player_inventory[RESOURCE_METAL] += WAREHOUSE_PRODUCTION
            player_inventory[RESOURCE_FOOD] += WAREHOUSE_PRODUCTION
            player_inventory[RESOURCE_WOOD] += WAREHOUSE_PRODUCTION
            player_inventory[RESOURCE_STONE] += WAREHOUSE_PRODUCTION


class Factory(Building):
    """Usine : automatise le crafting"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "Usine", COLOR_DARK_GRAY, 'factory.png')
        self.assigned_recipe = None  # ID de la recette assignée
        self.crafting_timer = 0

    def update(self, delta_time, player_inventory):
        """Produit automatiquement selon la recette assignée"""
        if not self.assigned_recipe:
            return

        self.crafting_timer += delta_time
        if self.crafting_timer >= FACTORY_PRODUCTION_INTERVAL:
            self.crafting_timer = 0
            # Signal pour main.py de crafter (nécessite accès au crafting_system)
            # On utilise une clé spéciale dans l'inventaire
            if '_factory_craft' not in player_inventory:
                player_inventory['_factory_craft'] = []
            player_inventory['_factory_craft'].append(self.assigned_recipe)


# Dictionnaire des types de bâtiments disponibles
BUILDING_TYPES = {
    'mine': {
        'class': Mine,
        'cost': BUILDING_MINE_COST,
        'name': 'Mine'
    },
    'farm': {
        'class': Farm,
        'cost': BUILDING_FARM_COST,
        'name': 'Ferme'
    },
    'generator': {
        'class': Generator,
        'cost': BUILDING_GENERATOR_COST,
        'name': 'Générateur'
    },
    'turret': {
        'class': Turret,
        'cost': BUILDING_TURRET_COST,
        'name': 'Tourelle'
    },
    'rocket': {
        'class': Rocket,
        'cost': BUILDING_ROCKET_COST,
        'name': 'Fusée'
    },
    'hospital': {
        'class': Hospital,
        'cost': BUILDING_HOSPITAL_COST,
        'name': 'Hôpital'
    },
    'laboratory': {
        'class': Laboratory,
        'cost': BUILDING_LABORATORY_COST,
        'name': 'Laboratoire'
    },
    'wall': {
        'class': Wall,
        'cost': BUILDING_WALL_COST,
        'name': 'Mur'
    },
    'warehouse': {
        'class': Warehouse,
        'cost': BUILDING_WAREHOUSE_COST,
        'name': 'Entrepôt'
    },
    'factory': {
        'class': Factory,
        'cost': BUILDING_FACTORY_COST,
        'name': 'Usine'
    }
}
