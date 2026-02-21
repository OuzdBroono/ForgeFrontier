"""
SPRITE_LOADER.PY
================
Système de chargement et cache de sprites avec fallback automatique.
Si un sprite n'est pas trouvé, utilise un rectangle coloré à la place.
"""

import pygame
import os
from constants import *


class SpriteLoader:
    """Gère le chargement et le cache des sprites"""

    _cache = {}  # Cache des sprites chargés
    SPRITE_DIR = "sprites"

    @classmethod
    def load_sprite(cls, filename, size=None, fallback_color=None):
        """
        Charge un sprite depuis un fichier avec cache
        Args:
            filename: Nom du fichier sprite (ex: 'player.png')
            size: Tuple (width, height) optionnel pour redimensionner
            fallback_color: Couleur de fallback si sprite introuvable
        Returns:
            pygame.Surface: Sprite chargé ou rectangle coloré de fallback
        """
        # Clé de cache unique
        cache_key = f"{filename}_{size}_{fallback_color}"

        # Retourner depuis le cache si déjà chargé
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Chemin complet du fichier
        filepath = os.path.join(cls.SPRITE_DIR, filename)

        # Essayer de charger le sprite
        if os.path.exists(filepath):
            try:
                sprite = pygame.image.load(filepath).convert_alpha()
                if size:
                    sprite = pygame.transform.scale(sprite, size)
                cls._cache[cache_key] = sprite
                return sprite
            except Exception as e:
                print(f"Erreur chargement sprite {filename}: {e}")

        # Fallback : créer un rectangle coloré
        if fallback_color and size:
            sprite = cls.create_placeholder_sprite(size, fallback_color)
            cls._cache[cache_key] = sprite
            return sprite

        return None

    @classmethod
    def create_placeholder_sprite(cls, size, color):
        """
        Crée un rectangle coloré comme sprite de remplacement
        Args:
            size: Tuple (width, height)
            color: Tuple RGB
        Returns:
            pygame.Surface: Rectangle coloré
        """
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    @classmethod
    def clear_cache(cls):
        """Vide le cache de sprites (utile pour libérer mémoire)"""
        cls._cache.clear()
