"""
ENEMIES.PY
==========
Ce fichier gère les ennemis du jeu (zombies, mutants, loups).
Les ennemis apparaissent aléatoirement et attaquent le joueur.
"""

import pygame
import math
import random
from constants import *
from sprite_loader import SpriteLoader


class BaseEnemy:
    """Classe de base pour tous les ennemis"""

    def __init__(self, spawn_x, spawn_y, health, speed, damage, size,
                 sprite_file, fallback_color, max_health_constant):
        """
        Initialise un ennemi
        Args:
            spawn_x, spawn_y: Position d'apparition (en pixels)
            health: Points de vie
            speed: Vitesse de déplacement
            damage: Dégâts infligés
            size: Taille du sprite
            sprite_file: Nom du fichier sprite
            fallback_color: Couleur de fallback si sprite manquant
            max_health_constant: HP max pour la barre de vie
        """
        self.position_x = spawn_x
        self.position_y = spawn_y
        self.enemy_size = size
        self.health_points = health
        self.max_health = max_health_constant
        self.speed = speed
        self.damage = damage
        self.is_alive = True
        self.attack_cooldown = 0
        self.enemy_type = 'base'  # Surchargé par les sous-classes

        # Charger le sprite avec fallback
        self.sprite = SpriteLoader.load_sprite(
            sprite_file,
            size=(self.enemy_size, self.enemy_size),
            fallback_color=fallback_color
        )

    def update(self, delta_time, player, buildings_list=None):
        """
        Met à jour l'ennemi (déplacement vers le joueur, attaque)
        Args:
            delta_time: Temps écoulé depuis la dernière frame
            player: Instance du joueur
            buildings_list: Liste des bâtiments (pour attaquer les murs)
        """
        if not self.is_alive or not player.is_alive:
            return

        # Chercher un mur à proximité à attaquer en priorité
        wall_to_attack = None
        if buildings_list:
            closest_wall_distance = float('inf')
            for building in buildings_list:
                if hasattr(building, 'is_obstacle') and building.is_obstacle:
                    # Calculer la distance au mur
                    wall_pixel_x = building.grid_x * TILE_SIZE + TILE_SIZE // 2
                    wall_pixel_y = building.grid_y * TILE_SIZE + TILE_SIZE // 2
                    dx = wall_pixel_x - self.position_x
                    dy = wall_pixel_y - self.position_y
                    distance_to_wall = math.sqrt(dx ** 2 + dy ** 2)

                    # Attaquer le mur le plus proche s'il est à portée
                    if distance_to_wall < 50 and distance_to_wall < closest_wall_distance:
                        closest_wall_distance = distance_to_wall
                        wall_to_attack = building

        # Si un mur est à portée, l'attaquer au lieu du joueur
        if wall_to_attack:
            # Se déplacer vers le mur
            wall_pixel_x = wall_to_attack.grid_x * TILE_SIZE + TILE_SIZE // 2
            wall_pixel_y = wall_to_attack.grid_y * TILE_SIZE + TILE_SIZE // 2
            direction_x = wall_pixel_x - self.position_x
            direction_y = wall_pixel_y - self.position_y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
                self.position_x += direction_x * self.speed
                self.position_y += direction_y * self.speed

            # Attaquer le mur
            if distance < 30:
                self.attack_cooldown -= delta_time
                if self.attack_cooldown <= 0:
                    wall_to_attack.take_damage(self.damage)
                    self.attack_cooldown = 1.5
        else:
            # Sinon, se déplacer vers le joueur
            # Calculer la direction vers le joueur
            direction_x = player.position_x - self.position_x
            direction_y = player.position_y - self.position_y

            # Calculer la distance au joueur
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            # Normaliser la direction (pour avoir une vitesse constante)
            if distance > 0:
                direction_x /= distance
                direction_y /= distance

                # Se déplacer vers le joueur
                self.position_x += direction_x * self.speed
                self.position_y += direction_y * self.speed

            # Vérifier si l'ennemi est assez proche pour attaquer
            if distance < 30:  # Distance d'attaque
                self.attack_cooldown -= delta_time
                if self.attack_cooldown <= 0:
                    player.take_damage(self.damage)
                    self.attack_cooldown = 1.5  # 1.5 secondes entre chaque attaque

    def take_damage(self, damage_amount):
        """
        L'ennemi subit des dégâts
        Args:
            damage_amount: Quantité de dégâts
        """
        self.health_points -= damage_amount
        if self.health_points <= 0:
            self.health_points = 0
            self.is_alive = False

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """
        Dessine l'ennemi à l'écran
        Args:
            screen: Surface Pygame
            camera_offset_x, camera_offset_y: Décalage de la caméra
        """
        if not self.is_alive:
            return

        # Position à l'écran
        x = self.position_x - camera_offset_x
        y = self.position_y - camera_offset_y

        # Dessiner le sprite
        if self.sprite:
            screen.blit(self.sprite, (x, y))

        # Bordure noire pour visibilité
        enemy_rect = pygame.Rect(x, y, self.enemy_size, self.enemy_size)
        pygame.draw.rect(screen, COLOR_BLACK, enemy_rect, 2)

        # Barre de vie au-dessus de l'ennemi
        health_bar_width = self.enemy_size
        health_bar_height = 4
        health_percentage = self.health_points / self.max_health

        # Fond de la barre (rouge)
        health_background = pygame.Rect(
            self.position_x - camera_offset_x,
            self.position_y - camera_offset_y - 8,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(screen, COLOR_RED, health_background)

        # Barre de vie actuelle (vert)
        health_foreground = pygame.Rect(
            self.position_x - camera_offset_x,
            self.position_y - camera_offset_y - 8,
            health_bar_width * health_percentage,
            health_bar_height
        )
        pygame.draw.rect(screen, COLOR_GREEN, health_foreground)


class Zombie(BaseEnemy):
    """Classe représentant un zombie ennemi"""

    def __init__(self, spawn_x, spawn_y):
        """
        Initialise un zombie à une position donnée
        Args:
            spawn_x, spawn_y: Position d'apparition (en pixels)
        """
        super().__init__(
            spawn_x, spawn_y,
            health=ZOMBIE_HEALTH,
            speed=ZOMBIE_SPEED,
            damage=ZOMBIE_DAMAGE,
            size=20,
            sprite_file='zombie.png',
            fallback_color=COLOR_RED,
            max_health_constant=ZOMBIE_HEALTH
        )
        self.enemy_type = 'zombie'


def spawn_enemy_randomly(enemy_class, map_size):
    """
    Fait apparaître un ennemi à une position aléatoire sur les bords de la carte
    Args:
        enemy_class: Classe de l'ennemi (Zombie, Mutant, Wolf, etc.)
        map_size: Taille de la carte en pixels
    Returns:
        Instance de l'ennemi
    """
    # Choisir un bord aléatoire (0=haut, 1=droite, 2=bas, 3=gauche)
    edge = random.randint(0, 3)

    if edge == 0:  # Haut
        spawn_x = random.randint(0, map_size)
        spawn_y = 0
    elif edge == 1:  # Droite
        spawn_x = map_size
        spawn_y = random.randint(0, map_size)
    elif edge == 2:  # Bas
        spawn_x = random.randint(0, map_size)
        spawn_y = map_size
    else:  # Gauche
        spawn_x = 0
        spawn_y = random.randint(0, map_size)

    return enemy_class(spawn_x, spawn_y)


def spawn_zombie_randomly(map_size):
    """
    Fait apparaître un zombie à une position aléatoire sur les bords de la carte
    Args:
        map_size: Taille de la carte en pixels
    Returns:
        Instance de Zombie
    """
    return spawn_enemy_randomly(Zombie, map_size)

class Mutant(BaseEnemy):
    """Classe représentant un mutant (tank : lent mais résistant)"""

    def __init__(self, spawn_x, spawn_y):
        """
        Initialise un mutant à une position donnée
        Args:
            spawn_x, spawn_y: Position d'apparition (en pixels)
        """
        super().__init__(
            spawn_x, spawn_y,
            health=MUTANT_HEALTH,
            speed=MUTANT_SPEED,
            damage=MUTANT_DAMAGE,
            size=28,
            sprite_file='mutant.png',
            fallback_color=COLOR_MUTANT_GREEN,
            max_health_constant=MUTANT_HEALTH
        )
        self.enemy_type = 'mutant'


class Wolf(BaseEnemy):
    """Classe représentant un loup (rapide, en meute)"""

    def __init__(self, spawn_x, spawn_y):
        """
        Initialise un loup à une position donnée
        Args:
            spawn_x, spawn_y: Position d'apparition (en pixels)
        """
        super().__init__(
            spawn_x, spawn_y,
            health=WOLF_HEALTH,
            speed=WOLF_SPEED,
            damage=WOLF_DAMAGE,
            size=18,
            sprite_file='wolf.png',
            fallback_color=COLOR_WOLF_BROWN,
            max_health_constant=WOLF_HEALTH
        )
        self.enemy_type = 'wolf'


def spawn_mutant_randomly(map_size):
    """
    Fait apparaître un mutant sur les bords de la carte
    Args:
        map_size: Taille de la carte en pixels
    Returns:
        Instance de Mutant
    """
    return spawn_enemy_randomly(Mutant, map_size)


def spawn_wolf_randomly(map_size):
    """
    Fait apparaître un loup sur les bords de la carte
    Args:
        map_size: Taille de la carte en pixels
    Returns:
        Instance de Wolf
    """
    return spawn_enemy_randomly(Wolf, map_size)
