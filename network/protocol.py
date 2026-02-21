"""
PROTOCOL.PY
===========
Définit le protocole de communication réseau pour le multijoueur.
Messages échangés entre serveur et clients au format JSON.
"""

import json

# Types de messages
MSG_CONNECT = "connect"
MSG_DISCONNECT = "disconnect"
MSG_PLAYER_UPDATE = "player_update"
MSG_INVENTORY_UPDATE = "inventory_update"
MSG_BUILDING_PLACE = "building_place"
MSG_BUILDING_UPDATE = "building_update"
MSG_ENEMY_SPAWN = "enemy_spawn"
MSG_ENEMY_UPDATE = "enemy_update"
MSG_ENEMY_DEATH = "enemy_death"
MSG_HEARTBEAT = "heartbeat"
MSG_GAME_STATE = "game_state"


class NetworkMessage:
    """Classe de base pour les messages réseau"""

    @staticmethod
    def encode(msg_type, data):
        """
        Encode un message en JSON
        Args:
            msg_type: Type de message
            data: Données du message (dict)
        Returns:
            str: Message JSON encodé avec délimiteur
        """
        message = {
            'type': msg_type,
            'data': data
        }
        return json.dumps(message) + "\n"

    @staticmethod
    def decode(msg_str):
        """
        Décode un message JSON
        Args:
            msg_str: String JSON
        Returns:
            tuple: (msg_type, data)
        """
        try:
            message = json.loads(msg_str)
            return message.get('type'), message.get('data')
        except json.JSONDecodeError:
            return None, None


class PlayerUpdateMessage:
    """Message de mise à jour de position du joueur"""

    @staticmethod
    def create(player_id, x, y, health, hunger):
        """
        Crée un message de mise à jour du joueur
        Args:
            player_id: ID du joueur
            x, y: Position
            health: Points de vie
            hunger: Niveau de faim
        Returns:
            str: Message encodé
        """
        data = {
            'player_id': player_id,
            'x': x,
            'y': y,
            'health': health,
            'hunger': hunger
        }
        return NetworkMessage.encode(MSG_PLAYER_UPDATE, data)


class InventoryUpdateMessage:
    """Message de mise à jour de l'inventaire partagé"""

    @staticmethod
    def create(inventory):
        """
        Crée un message de mise à jour de l'inventaire
        Args:
            inventory: Dictionnaire inventaire
        Returns:
            str: Message encodé
        """
        # Filtrer les clés spéciales (qui commencent par _)
        clean_inventory = {k: v for k, v in inventory.items() if not k.startswith('_')}
        data = {'inventory': clean_inventory}
        return NetworkMessage.encode(MSG_INVENTORY_UPDATE, data)


class BuildingMessage:
    """Messages pour les bâtiments"""

    @staticmethod
    def create_place(building_type, grid_x, grid_y):
        """
        Crée un message de placement de bâtiment
        Args:
            building_type: Type de bâtiment
            grid_x, grid_y: Position dans la grille
        Returns:
            str: Message encodé
        """
        data = {
            'building_type': building_type,
            'grid_x': grid_x,
            'grid_y': grid_y
        }
        return NetworkMessage.encode(MSG_BUILDING_PLACE, data)

    @staticmethod
    def create_update(building_index, durability=None):
        """
        Crée un message de mise à jour de bâtiment (ex: durabilité mur)
        Args:
            building_index: Index du bâtiment dans la liste
            durability: Durabilité actuelle (optionnel)
        Returns:
            str: Message encodé
        """
        data = {
            'building_index': building_index,
            'durability': durability
        }
        return NetworkMessage.encode(MSG_BUILDING_UPDATE, data)


class EnemyMessage:
    """Messages pour les ennemis"""

    @staticmethod
    def create_spawn(enemy_id, enemy_type, spawn_x, spawn_y):
        """
        Crée un message d'apparition d'ennemi
        Args:
            enemy_id: ID unique de l'ennemi
            enemy_type: Type d'ennemi (zombie, mutant, wolf)
            spawn_x, spawn_y: Position d'apparition
        Returns:
            str: Message encodé
        """
        data = {
            'enemy_id': enemy_id,
            'enemy_type': enemy_type,
            'spawn_x': spawn_x,
            'spawn_y': spawn_y
        }
        return NetworkMessage.encode(MSG_ENEMY_SPAWN, data)

    @staticmethod
    def create_update(enemy_id, x, y, health):
        """
        Crée un message de mise à jour d'ennemi
        Args:
            enemy_id: ID de l'ennemi
            x, y: Position
            health: Points de vie
        Returns:
            str: Message encodé
        """
        data = {
            'enemy_id': enemy_id,
            'x': x,
            'y': y,
            'health': health
        }
        return NetworkMessage.encode(MSG_ENEMY_UPDATE, data)

    @staticmethod
    def create_death(enemy_id):
        """
        Crée un message de mort d'ennemi
        Args:
            enemy_id: ID de l'ennemi
        Returns:
            str: Message encodé
        """
        data = {'enemy_id': enemy_id}
        return NetworkMessage.encode(MSG_ENEMY_DEATH, data)


class GameStateMessage:
    """Message d'état complet du jeu (synchronisation initiale)"""

    @staticmethod
    def create(players, buildings, enemies, inventory, elapsed_time):
        """
        Crée un message d'état complet du jeu
        Args:
            players: Liste des joueurs
            buildings: Liste des bâtiments
            enemies: Liste des ennemis
            inventory: Inventaire partagé
            elapsed_time: Temps de jeu écoulé
        Returns:
            str: Message encodé
        """
        data = {
            'players': players,
            'buildings': buildings,
            'enemies': enemies,
            'inventory': inventory,
            'elapsed_time': elapsed_time
        }
        return NetworkMessage.encode(MSG_GAME_STATE, data)
