"""
PLAYER.PY
=========
Ce fichier gère le joueur : position, déplacement, inventaire, stats de survie.
Le joueur peut récolter des ressources et construire des bâtiments.
"""

import pygame
from constants import *
from sprite_loader import SpriteLoader


class Player:
    """Classe représentant le joueur dans le jeu"""

    def __init__(self, start_x, start_y):
        """
        Initialise le joueur à une position donnée
        Args:
            start_x: Position X de départ (en pixels)
            start_y: Position Y de départ (en pixels)
        """
        # Position du joueur
        self.position_x = start_x
        self.position_y = start_y
        self.player_size = 24  # Taille du carré représentant le joueur

        # Charger le sprite (fallback vers rectangle bleu si absent)
        self.sprite = SpriteLoader.load_sprite(
            'player.png',
            size=(self.player_size, self.player_size),
            fallback_color=COLOR_BLUE
        )

        # Inventaire : dictionnaire contenant les ressources
        self.inventory = {
            RESOURCE_METAL: 20,  # On commence avec un peu de métal
            RESOURCE_FOOD: 10,
            RESOURCE_ENERGY: 5,
            RESOURCE_WOOD: 0,
            RESOURCE_STONE: 0,
            # Ressources craftées
            'tools': 0,
            'components': 0,
            'medicine': 0,
            'advanced_materials': 0
        }

        # Statistiques de survie
        self.health_points = PLAYER_INITIAL_HEALTH
        self.hunger_level = PLAYER_INITIAL_HUNGER
        self.is_alive = True

    def update(self, delta_time):
        """
        Met à jour le joueur chaque frame
        Args:
            delta_time: Temps écoulé depuis la dernière frame (en secondes)
        """
        # La faim diminue avec le temps
        self.hunger_level -= PLAYER_HUNGER_DECREASE_RATE * delta_time

        # Si la faim atteint 0, le joueur perd de la vie
        if self.hunger_level <= 0:
            self.hunger_level = 0
            self.health_points -= 5 * delta_time  # Perd 5 PV par seconde

        # Vérifier si le joueur est mort
        if self.health_points <= 0:
            self.health_points = 0
            self.is_alive = False

    def move(self, direction_x, direction_y, world):
        """
        Déplace le joueur dans une direction
        Args:
            direction_x: Direction X (-1 pour gauche, 1 pour droite, 0 pour immobile)
            direction_y: Direction Y (-1 pour haut, 1 pour bas, 0 pour immobile)
            world: Instance du monde pour vérifier les collisions
        """
        # Vérifier le terrain actuel pour appliquer les effets (désert)
        current_grid_x = int(self.position_x // TILE_SIZE)
        current_grid_y = int(self.position_y // TILE_SIZE)
        movement_speed = PLAYER_MOVEMENT_SPEED

        if 0 <= current_grid_x < GRID_SIZE and 0 <= current_grid_y < GRID_SIZE:
            current_terrain = world.grid_terrain[current_grid_y][current_grid_x]
            # Pénalité de vitesse dans le désert
            if current_terrain == TERRAIN_DESERT or current_terrain == TERRAIN_ENERGY_CRYSTAL:
                movement_speed *= DESERT_SPEED_PENALTY

        # Calculer la nouvelle position
        new_position_x = self.position_x + direction_x * movement_speed
        new_position_y = self.position_y + direction_y * movement_speed

        # Vérifier les limites du monde
        map_width = GRID_SIZE * TILE_SIZE
        map_height = GRID_SIZE * TILE_SIZE

        # Convertir en coordonnées de grille pour vérifier le terrain
        grid_x = int(new_position_x // TILE_SIZE)
        grid_y = int(new_position_y // TILE_SIZE)

        # Vérifier si le terrain est franchissable (pas d'eau ou montagne)
        can_move_x = world.is_tile_walkable(grid_x, int(self.position_y // TILE_SIZE))
        can_move_y = world.is_tile_walkable(int(self.position_x // TILE_SIZE), grid_y)

        # Déplacer sur X si possible
        if 0 <= new_position_x <= map_width - self.player_size and can_move_x:
            self.position_x = new_position_x

        # Déplacer sur Y si possible
        if 0 <= new_position_y <= map_height - self.player_size and can_move_y:
            self.position_y = new_position_y

    def harvest_resource(self, world, mouse_x, mouse_y, camera_offset_x, camera_offset_y):
        """
        Récolte une ressource à la position de la souris
        Args:
            world: Instance du monde
            mouse_x, mouse_y: Position de la souris à l'écran
            camera_offset_x, camera_offset_y: Décalage de la caméra
        Returns:
            True si une ressource a été récoltée, False sinon
        """
        # Convertir position souris en position grille (avec décalage caméra)
        grid_x = (mouse_x + camera_offset_x) // TILE_SIZE
        grid_y = (mouse_y + camera_offset_y) // TILE_SIZE

        # Vérifier que c'est dans les limites
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            terrain_type = world.grid_terrain[grid_y][grid_x]

            # Calculer quantité récoltée (bonus si outils)
            harvest_amount = PLAYER_HARVEST_AMOUNT
            if self.inventory.get('tools', 0) > 0:
                harvest_amount = int(PLAYER_HARVEST_AMOUNT * TOOL_HARVEST_MULTIPLIER)

            # Bonus de recherche niveau 1 : Outils Améliorés (+2 récolte)
            research_level = self.inventory.get('_research_level', 0)
            if research_level >= 1:
                harvest_amount += 2

            # Récolter selon le type de terrain
            if terrain_type == TERRAIN_METAL:
                self.inventory[RESOURCE_METAL] += harvest_amount
                world.grid_terrain[grid_y][grid_x] = TERRAIN_GRASS  # Ressource épuisée
                world.depleted_tiles[(grid_x, grid_y)] = RESOURCE_RESPAWN_TIME
                return True
            elif terrain_type == TERRAIN_FOOD:
                self.inventory[RESOURCE_FOOD] += harvest_amount
                world.grid_terrain[grid_y][grid_x] = TERRAIN_GRASS
                world.depleted_tiles[(grid_x, grid_y)] = RESOURCE_RESPAWN_TIME
                return True
            elif terrain_type == TERRAIN_WOOD:
                self.inventory[RESOURCE_WOOD] += harvest_amount
                world.grid_terrain[grid_y][grid_x] = TERRAIN_GRASS
                world.depleted_tiles[(grid_x, grid_y)] = RESOURCE_RESPAWN_TIME
                return True
            elif terrain_type == TERRAIN_STONE:
                self.inventory[RESOURCE_STONE] += harvest_amount
                world.grid_terrain[grid_y][grid_x] = TERRAIN_GRASS
                world.depleted_tiles[(grid_x, grid_y)] = RESOURCE_RESPAWN_TIME
                return True
            elif terrain_type == TERRAIN_ENERGY_CRYSTAL:
                self.inventory[RESOURCE_ENERGY] += harvest_amount
                world.grid_terrain[grid_y][grid_x] = TERRAIN_DESERT  # Redevient désert
                world.depleted_tiles[(grid_x, grid_y)] = RESOURCE_RESPAWN_TIME
                return True

        return False

    def eat_food(self, amount=50):
        """
        Mange de la nourriture pour restaurer la faim
        Args:
            amount: Quantité de faim restaurée
        """
        if self.inventory[RESOURCE_FOOD] >= 1:
            self.inventory[RESOURCE_FOOD] -= 1
            self.hunger_level = min(100, self.hunger_level + amount)
            return True
        return False

    def use_medicine(self):
        """
        Utilise une médecine pour restaurer la vie
        Returns:
            bool: True si médecine utilisée, False sinon
        """
        if self.inventory.get('medicine', 0) >= 1:
            self.inventory['medicine'] -= 1
            self.health_points = min(PLAYER_INITIAL_HEALTH, self.health_points + MEDICINE_HEAL_AMOUNT)
            return True
        return False

    def take_damage(self, damage_amount):
        """
        Le joueur subit des dégâts
        Args:
            damage_amount: Quantité de dégâts subis
        """
        self.health_points -= damage_amount
        if self.health_points <= 0:
            self.health_points = 0
            self.is_alive = False

    def has_resources(self, cost_dict):
        """
        Vérifie si le joueur a assez de ressources
        Args:
            cost_dict: Dictionnaire des ressources nécessaires
        Returns:
            True si le joueur a toutes les ressources, False sinon
        """
        for resource_name, amount_needed in cost_dict.items():
            if self.inventory.get(resource_name, 0) < amount_needed:
                return False
        return True

    def spend_resources(self, cost_dict):
        """
        Dépense des ressources de l'inventaire
        Args:
            cost_dict: Dictionnaire des ressources à dépenser
        """
        for resource_name, amount_to_spend in cost_dict.items():
            self.inventory[resource_name] -= amount_to_spend

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Dessine le joueur à l'écran
        Args:
            screen: Surface Pygame où dessiner
            camera_offset_x, camera_offset_y: Décalage de la caméra
        """
        # Position à l'écran
        x = self.position_x - camera_offset_x
        y = self.position_y - camera_offset_y

        # Dessiner le sprite
        if self.sprite:
            screen.blit(self.sprite, (x, y))

        # Bordure blanche pour mieux voir le joueur
        player_rect = pygame.Rect(x, y, self.player_size, self.player_size)
        pygame.draw.rect(screen, COLOR_WHITE, player_rect, 2)