"""
SAVE_SYSTEM.PY
==============
Gère la sauvegarde et le chargement de l'état du jeu.
Utilise JSON pour persister l'état complet du jeu.
"""

import json
import os
from constants import *


class SaveSystem:
    """Gère la sauvegarde et le chargement du jeu"""

    SAVE_FILE = "savegame.json"

    @staticmethod
    def save_game(game):
        """
        Sauvegarde l'état complet du jeu dans un fichier JSON
        Args:
            game: Instance de la classe Game
        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        save_data = {
            'version': '1.0',  # Pour compatibilité future
            'player': {
                'position_x': game.player.position_x,
                'position_y': game.player.position_y,
                'inventory': game.player.inventory.copy(),
                'health_points': game.player.health_points,
                'hunger_level': game.player.hunger_level,
                'is_alive': game.player.is_alive
            },
            'world': {
                'grid_terrain': game.world.grid_terrain,  # Grille 2D
                'original_terrain': game.world.original_terrain,  # Terrain original pour respawn
                'depleted_tiles': [[x, y, timer] for (x, y), timer in game.world.depleted_tiles.items()]
            },
            'buildings': [
                {
                    'type': building.__class__.__name__.lower(),
                    'grid_x': building.grid_x,
                    'grid_y': building.grid_y,
                    'production_timer': building.production_timer,
                    # Pour laboratoire
                    'research_level': getattr(building, 'research_level', 0)
                }
                for building in game.buildings_list
            ],
            'enemies': [
                {
                    'type': enemy.__class__.__name__.lower(),
                    'position_x': enemy.position_x,
                    'position_y': enemy.position_y,
                    'health_points': enemy.health_points,
                    'is_alive': enemy.is_alive
                }
                for enemy in game.enemies_list if enemy.is_alive
            ],
            'timers': {
                'total_elapsed_time': game.total_elapsed_time,
                'zombie_spawn_timer': game.zombie_spawn_timer,
                'mutant_spawn_timer': game.mutant_spawn_timer,
                'wolf_spawn_timer': game.wolf_spawn_timer
            },
            'game_state': game.game_state,
            'has_won': game.has_won,
            'stats': game.stats,  # Stats pour les quêtes
            'active_quests': game.quest_manager.active_quests,
            'completed_quests': game.quest_manager.completed_quests,
            'crafting_queue': game.crafting_queue.queue  # Queue de crafting
        }

        try:
            with open(SaveSystem.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Jeu sauvegardé dans {SaveSystem.SAVE_FILE}")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False

    @staticmethod
    def load_game():
        """
        Charge l'état du jeu depuis le fichier JSON
        Returns:
            dict: Données de sauvegarde ou None si erreur
        """
        if not os.path.exists(SaveSystem.SAVE_FILE):
            print("Aucune sauvegarde trouvée.")
            return None

        try:
            with open(SaveSystem.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            print(f"Sauvegarde chargée depuis {SaveSystem.SAVE_FILE}")
            return save_data
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            return None

    @staticmethod
    def save_exists():
        """
        Vérifie si un fichier de sauvegarde existe
        Returns:
            bool: True si existe, False sinon
        """
        return os.path.exists(SaveSystem.SAVE_FILE)
