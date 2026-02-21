"""
CLIENT.PY
=========
Client réseau pour le multijoueur.
Se connecte au serveur et synchronise l'état du jeu.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import threading
import time
from .protocol import *


class NetworkClient:
    """Client réseau pour le multijoueur"""

    def __init__(self):
        """Initialise le client"""
        self.socket = None
        self.connected = False
        self.player_id = None
        self.buffer = ''

        # Callbacks pour traiter les messages reçus
        self.on_connect = None
        self.on_disconnect = None
        self.on_player_update = None
        self.on_inventory_update = None
        self.on_building_place = None
        self.on_enemy_spawn = None
        self.on_enemy_update = None
        self.on_enemy_death = None
        self.on_game_state = None

        # Thread de réception
        self.receive_thread = None

    def connect(self, host, port):
        """
        Se connecte au serveur
        Args:
            host: Adresse IP du serveur
            port: Port du serveur
        Returns:
            bool: True si connexion réussie
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True

            print(f"✅ Connecté au serveur {host}:{port}")

            # Démarrer le thread de réception
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            return True

        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Déconnecte du serveur"""
        if self.connected:
            disconnect_msg = NetworkMessage.encode(MSG_DISCONNECT, {'player_id': self.player_id})
            self.send_message(disconnect_msg)

            self.connected = False
            if self.socket:
                self.socket.close()

            print("❌ Déconnecté du serveur")

    def send_message(self, message):
        """
        Envoie un message au serveur
        Args:
            message: Message à envoyer
        """
        if self.connected and self.socket:
            try:
                self.socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"❌ Erreur envoi message: {e}")
                self.connected = False

    def receive_messages(self):
        """Thread de réception des messages du serveur"""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("❌ Connexion fermée par le serveur")
                    self.connected = False
                    break

                # Ajouter au buffer
                self.buffer += data

                # Traiter les messages complets (séparés par \n)
                while '\n' in self.buffer:
                    message, self.buffer = self.buffer.split('\n', 1)
                    if message:
                        self.process_message(message)

            except Exception as e:
                if self.connected:
                    print(f"❌ Erreur réception: {e}")
                    self.connected = False
                break

    def process_message(self, message):
        """
        Traite un message reçu du serveur
        Args:
            message: Message à traiter
        """
        msg_type, data = NetworkMessage.decode(message)
        if msg_type is None:
            return

        if msg_type == MSG_CONNECT:
            # Réception de notre ID joueur
            self.player_id = data['player_id']
            print(f"🎮 ID Joueur reçu: {self.player_id}")
            if self.on_connect:
                self.on_connect(self.player_id)

        elif msg_type == MSG_DISCONNECT:
            # Un autre joueur s'est déconnecté
            if self.on_disconnect:
                self.on_disconnect(data['player_id'])

        elif msg_type == MSG_PLAYER_UPDATE:
            # Mise à jour d'un autre joueur
            if self.on_player_update:
                self.on_player_update(data)

        elif msg_type == MSG_INVENTORY_UPDATE:
            # Mise à jour de l'inventaire partagé
            if self.on_inventory_update:
                self.on_inventory_update(data['inventory'])

        elif msg_type == MSG_BUILDING_PLACE:
            # Nouveau bâtiment placé
            if self.on_building_place:
                self.on_building_place(
                    data['building_type'],
                    data['grid_x'],
                    data['grid_y']
                )

        elif msg_type == MSG_ENEMY_SPAWN:
            # Nouvel ennemi spawné
            if self.on_enemy_spawn:
                self.on_enemy_spawn(
                    data['enemy_id'],
                    data['enemy_type'],
                    data['spawn_x'],
                    data['spawn_y']
                )

        elif msg_type == MSG_ENEMY_UPDATE:
            # Mise à jour d'ennemi
            if self.on_enemy_update:
                self.on_enemy_update(
                    data['enemy_id'],
                    data['x'],
                    data['y'],
                    data['health']
                )

        elif msg_type == MSG_ENEMY_DEATH:
            # Ennemi mort
            if self.on_enemy_death:
                self.on_enemy_death(data['enemy_id'])

        elif msg_type == MSG_GAME_STATE:
            # État complet du jeu (synchronisation initiale)
            if self.on_game_state:
                self.on_game_state(data)

        elif msg_type == MSG_HEARTBEAT:
            # Heartbeat du serveur (on ne fait rien)
            pass

    # ===== Méthodes pour envoyer des mises à jour =====

    def send_player_update(self, x, y, health, hunger):
        """
        Envoie une mise à jour de position du joueur
        Args:
            x, y: Position
            health: Points de vie
            hunger: Niveau de faim
        """
        if self.connected and self.player_id:
            msg = PlayerUpdateMessage.create(self.player_id, x, y, health, hunger)
            self.send_message(msg)

    def send_inventory_update(self, inventory):
        """
        Envoie une mise à jour de l'inventaire
        Args:
            inventory: Dictionnaire inventaire
        """
        if self.connected:
            msg = InventoryUpdateMessage.create(inventory)
            self.send_message(msg)

    def send_building_place(self, building_type, grid_x, grid_y):
        """
        Envoie un placement de bâtiment
        Args:
            building_type: Type de bâtiment
            grid_x, grid_y: Position
        """
        if self.connected:
            msg = BuildingMessage.create_place(building_type, grid_x, grid_y)
            self.send_message(msg)

    def send_enemy_spawn(self, enemy_id, enemy_type, spawn_x, spawn_y):
        """
        Envoie un spawn d'ennemi
        Args:
            enemy_id: ID de l'ennemi
            enemy_type: Type d'ennemi
            spawn_x, spawn_y: Position
        """
        if self.connected:
            msg = EnemyMessage.create_spawn(enemy_id, enemy_type, spawn_x, spawn_y)
            self.send_message(msg)

    def send_enemy_death(self, enemy_id):
        """
        Envoie une mort d'ennemi
        Args:
            enemy_id: ID de l'ennemi
        """
        if self.connected:
            msg = EnemyMessage.create_death(enemy_id)
            self.send_message(msg)
