"""
WORLD.PY
========
Ce fichier gère le monde du jeu : la grille, le terrain, la génération procédurale.
Le monde est une grille 20x20 avec différents types de terrain (herbe, métal, nourriture).
"""

import random
import pygame
from constants import *


class World:
    """Classe représentant le monde du jeu"""

    def __init__(self, seed=None):
        """
        Initialise le monde avec une grille vide
        Args:
            seed: Graine aléatoire optionnelle pour génération reproductible
        """
        # Définir la seed si fournie
        if seed is not None:
            random.seed(seed)

        # Créer une grille 20x20 remplie d'herbe
        self.grid_terrain = [[TERRAIN_GRASS for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]

        # Générer le terrain procédural (lacs, montagnes, biomes)
        self.generate_terrain()

        # Générer des ressources aléatoirement sur la carte
        self.generate_resources()

        # Sauvegarder le terrain original pour la régénération
        self.original_terrain = [row[:] for row in self.grid_terrain]

        # Dictionnaire des ressources épuisées : {(x, y): timer_restant}
        self.depleted_tiles = {}

    def update(self, delta_time):
        """
        Met à jour le monde (régénération des ressources)
        Args:
            delta_time: Temps écoulé depuis la dernière frame
        """
        # Mettre à jour les timers de respawn
        tiles_to_respawn = []

        for pos, timer in list(self.depleted_tiles.items()):
            self.depleted_tiles[pos] -= delta_time
            if self.depleted_tiles[pos] <= 0:
                tiles_to_respawn.append(pos)

        # Régénérer les ressources
        for x, y in tiles_to_respawn:
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                # Restaurer le terrain original
                self.grid_terrain[y][x] = self.original_terrain[y][x]
                del self.depleted_tiles[(x, y)]

    def generate_terrain(self):
        """Génère le terrain procédural avec lacs, montagnes, forêts et déserts"""
        # Générer des lacs (clusters d'eau)
        self._generate_water_bodies()

        # Générer des chaînes de montagnes
        self._generate_mountains()

        # Générer des biomes (forêts)
        self._generate_biomes()

        # Générer des zones désertiques
        self._generate_desert()

    def _generate_water_bodies(self):
        """Crée des lacs avec croissance par cluster"""
        num_lakes = 2  # Nombre de lacs

        for _ in range(num_lakes):
            # Position de départ du lac
            seed_x = random.randint(2, GRID_SIZE - 3)
            seed_y = random.randint(2, GRID_SIZE - 3)

            # Taille du lac
            lake_size = random.randint(5, 12)
            water_tiles = [(seed_x, seed_y)]
            self.grid_terrain[seed_y][seed_x] = TERRAIN_WATER

            # Croissance du lac (algorithme cellulaire)
            for _ in range(lake_size):
                if water_tiles:
                    expand_x, expand_y = random.choice(water_tiles)

                    # Essayer d'étendre dans les 4 directions
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_x = expand_x + dx
                        new_y = expand_y + dy

                        # Vérifier les limites
                        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                            # 70% de chance d'expansion
                            if random.random() < 0.7 and self.grid_terrain[new_y][new_x] == TERRAIN_GRASS:
                                self.grid_terrain[new_y][new_x] = TERRAIN_WATER
                                water_tiles.append((new_x, new_y))

    def _generate_mountains(self):
        """Génère des chaînes de montagnes linéaires"""
        num_ranges = 2  # Nombre de chaînes

        for _ in range(num_ranges):
            # Point de départ
            start_x = random.randint(0, GRID_SIZE - 1)
            start_y = random.randint(0, GRID_SIZE - 1)

            # Direction (horizontal, vertical, diagonal)
            direction = random.choice([(1, 0), (0, 1), (1, 1), (1, -1)])

            # Longueur de la chaîne
            length = random.randint(4, 8)

            for i in range(length):
                x = (start_x + i * direction[0]) % GRID_SIZE
                y = (start_y + i * direction[1]) % GRID_SIZE

                # Ne pas écraser l'eau
                if self.grid_terrain[y][x] not in [TERRAIN_WATER]:
                    self.grid_terrain[y][x] = TERRAIN_MOUNTAIN

    def _generate_biomes(self):
        """Crée des zones de forêt (patches circulaires)"""
        num_forests = 3  # Nombre de forêts

        for _ in range(num_forests):
            # Centre de la forêt
            center_x = random.randint(3, GRID_SIZE - 4)
            center_y = random.randint(3, GRID_SIZE - 4)
            radius = random.randint(2, 4)

            # Créer un patch circulaire
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                        # Distance au centre
                        distance = (dx**2 + dy**2)**0.5

                        # Si dans le rayon et herbe, transformer en forêt
                        if distance <= radius and self.grid_terrain[y][x] == TERRAIN_GRASS:
                            if random.random() < 0.7:  # 70% de densité
                                self.grid_terrain[y][x] = TERRAIN_FOREST

    def _generate_desert(self):
        """Crée des zones désertiques (patches circulaires)"""
        num_deserts = random.randint(1, 2)  # 1-2 zones désertiques

        for _ in range(num_deserts):
            # Centre du désert (loin de l'eau de préférence)
            center_x = random.randint(3, GRID_SIZE - 4)
            center_y = random.randint(3, GRID_SIZE - 4)
            radius = random.randint(2, 3)

            # Créer un patch circulaire
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                        # Distance au centre
                        distance = (dx**2 + dy**2)**0.5

                        # Si dans le rayon et herbe, transformer en désert
                        if distance <= radius and self.grid_terrain[y][x] == TERRAIN_GRASS:
                            self.grid_terrain[y][x] = TERRAIN_DESERT

    def generate_resources(self):
        """
        Génère des ressources selon les biomes
        Bois dans forêts, pierre près montagnes, etc.
        """
        # Placer du métal aléatoirement sur l'herbe (15 sources)
        metal_count = 0
        attempts = 0
        while metal_count < 15 and attempts < 100:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.grid_terrain[y][x] == TERRAIN_GRASS:
                self.grid_terrain[y][x] = TERRAIN_METAL
                metal_count += 1
            attempts += 1

        # Placer de la pierre près des montagnes (8 sources)
        stone_count = 0
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid_terrain[y][x] == TERRAIN_GRASS:
                    # Vérifier si à côté d'une montagne
                    near_mountain = False
                    for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < GRID_SIZE and 0 <= nx < GRID_SIZE:
                            if self.grid_terrain[ny][nx] == TERRAIN_MOUNTAIN:
                                near_mountain = True
                                break

                    if near_mountain and random.random() < 0.4 and stone_count < 8:
                        self.grid_terrain[y][x] = TERRAIN_STONE
                        stone_count += 1

        # Placer du bois dans les forêts (30% des tiles de forêt)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid_terrain[y][x] == TERRAIN_FOREST:
                    if random.random() < 0.3:
                        self.grid_terrain[y][x] = TERRAIN_WOOD

        # Placer de la nourriture sur l'herbe (12 sources)
        food_count = 0
        attempts = 0
        while food_count < 12 and attempts < 100:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if self.grid_terrain[y][x] == TERRAIN_GRASS:
                self.grid_terrain[y][x] = TERRAIN_FOOD
                food_count += 1
            attempts += 1

        # Placer des cristaux d'énergie dans les déserts (40% des tiles de désert)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid_terrain[y][x] == TERRAIN_DESERT:
                    if random.random() < 0.4:
                        self.grid_terrain[y][x] = TERRAIN_ENERGY_CRYSTAL

    def get_terrain_color(self, terrain_type):
        """
        Retourne la couleur associée à un type de terrain
        Args:
            terrain_type: Type de terrain (TERRAIN_GRASS, TERRAIN_METAL, etc.)
        Returns:
            Tuple RGB représentant la couleur
        """
        if terrain_type == TERRAIN_GRASS:
            return COLOR_GREEN
        elif terrain_type == TERRAIN_METAL:
            return COLOR_GRAY
        elif terrain_type == TERRAIN_FOOD:
            return COLOR_DARK_GREEN
        elif terrain_type == TERRAIN_WOOD:
            return COLOR_WOOD_BROWN
        elif terrain_type == TERRAIN_STONE:
            return COLOR_STONE_GRAY
        elif terrain_type == TERRAIN_WATER:
            return COLOR_WATER_BLUE
        elif terrain_type == TERRAIN_MOUNTAIN:
            return COLOR_MOUNTAIN_GRAY
        elif terrain_type == TERRAIN_FOREST:
            return COLOR_FOREST_GREEN
        elif terrain_type == TERRAIN_DESERT:
            return COLOR_DESERT_YELLOW
        elif terrain_type == TERRAIN_ENERGY_CRYSTAL:
            return (0, 255, 255)  # Cyan brillant pour les cristaux d'énergie
        return COLOR_BLACK

    def is_tile_walkable(self, grid_x, grid_y):
        """
        Vérifie si une case est franchissable (pas d'obstacle)
        Args:
            grid_x, grid_y: Coordonnées de la case dans la grille
        Returns:
            True si la case est franchissable, False sinon
        """
        # Vérifier les limites
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return False

        # Eau et montagnes bloquent le passage
        terrain = self.grid_terrain[grid_y][grid_x]
        return terrain not in [TERRAIN_WATER, TERRAIN_MOUNTAIN]

    def is_tile_buildable(self, grid_x, grid_y, buildings_list):
        """
        Vérifie si une case est constructible (pas de bâtiment déjà présent)
        Args:
            grid_x, grid_y: Coordonnées de la case dans la grille
            buildings_list: Liste de tous les bâtiments existants
        Returns:
            True si la case est libre, False sinon
        """
        # Vérifier qu'il n'y a pas déjà un bâtiment à cet endroit
        for building in buildings_list:
            if building.grid_x == grid_x and building.grid_y == grid_y:
                return False
        return True

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Dessine le monde (la grille de terrain) à l'écran
        Args:
            screen: Surface Pygame où dessiner
            camera_offset_x, camera_offset_y: Décalage de la caméra
        """
        # Parcourir toute la grille
        for grid_y in range(GRID_SIZE):
            for grid_x in range(GRID_SIZE):
                # Calculer la position en pixels (avec décalage caméra)
                pixel_x = grid_x * TILE_SIZE - camera_offset_x
                pixel_y = grid_y * TILE_SIZE - camera_offset_y

                # Ne dessiner que les cases visibles à l'écran
                if -TILE_SIZE < pixel_x < SCREEN_WIDTH and -TILE_SIZE < pixel_y < SCREEN_HEIGHT:
                    # Obtenir le type de terrain et sa couleur
                    terrain_type = self.grid_terrain[grid_y][grid_x]
                    terrain_color = self.get_terrain_color(terrain_type)

                    # Dessiner la case
                    tile_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, terrain_color, tile_rect)

                    # Bordure noire pour mieux voir la grille
                    pygame.draw.rect(screen, COLOR_BLACK, tile_rect, 1)
