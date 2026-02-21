"""
SERVER.PY
=========
Serveur de jeu multijoueur pour Frontier Forge.
Gère la connexion des clients, synchronise l'état du jeu.
"""

import socket
import threading
import time
from protocol import *


class GameServer:
    """Serveur de jeu multijoueur"""

    def __init__(self, host='0.0.0.0', port=5555, max_players=4):
        """
        Initialise le serveur
        Args:
            host: Adresse IP du serveur (0.0.0.0 = toutes interfaces)
            port: Port d'écoute
            max_players: Nombre maximum de joueurs
        """
        self.host = host
        self.port = port
        self.max_players = max_players
        self.server_socket = None
        self.running = False

        # État du jeu (autorité serveur)
        self.clients = {}  # {client_socket: {'id': player_id, 'addr': addr, 'data': player_data}}
        self.next_player_id = 1
        self.game_state = {
            'players': {},
            'buildings': [],
            'enemies': {},
            'inventory': {
                'metal': 50,  # Inventaire partagé de départ
                'food': 30,
                'energy': 10,
                'wood': 20,
                'stone': 20
            },
            'elapsed_time': 0.0,
            'next_enemy_id': 1
        }

        print(f"🎮 Serveur Frontier Forge initialisé")
        print(f"📡 IP: {host}, Port: {port}")
        print(f"👥 Joueurs max: {max_players}")

    def start(self):
        """Démarre le serveur"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_players)
        self.running = True

        print(f"✅ Serveur démarré et en écoute...")
        print(f"⏳ En attente de connexions...")

        # Thread pour accepter les connexions
        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.daemon = True
        accept_thread.start()

        # Thread pour envoyer des heartbeats
        heartbeat_thread = threading.Thread(target=self.send_heartbeats)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

        # Boucle principale du serveur
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            self.stop()

    def accept_clients(self):
        """Accepte les connexions des clients"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()

                if len(self.clients) >= self.max_players:
                    print(f"❌ Connexion refusée de {address} (serveur plein)")
                    client_socket.close()
                    continue

                player_id = self.next_player_id
                self.next_player_id += 1

                self.clients[client_socket] = {
                    'id': player_id,
                    'addr': address,
                    'buffer': ''
                }

                # Initialiser les données du joueur dans l'état du jeu
                self.game_state['players'][player_id] = {
                    'x': 500.0,
                    'y': 500.0,
                    'health': 100,
                    'hunger': 100
                }

                print(f"✅ Joueur {player_id} connecté depuis {address}")
                print(f"👥 Joueurs connectés: {len(self.clients)}/{self.max_players}")

                # Envoyer l'état initial au nouveau joueur
                self.send_initial_state(client_socket, player_id)

                # Thread pour recevoir les messages du client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                if self.running:
                    print(f"❌ Erreur lors de l'acceptation: {e}")

    def send_initial_state(self, client_socket, player_id):
        """
        Envoie l'état initial du jeu au nouveau joueur
        Args:
            client_socket: Socket du client
            player_id: ID du joueur
        """
        # Message de connexion avec l'ID du joueur
        connect_msg = NetworkMessage.encode(MSG_CONNECT, {'player_id': player_id})
        self.send_to_client(client_socket, connect_msg)

        # État complet du jeu
        game_state_msg = GameStateMessage.create(
            players=self.game_state['players'],
            buildings=self.game_state['buildings'],
            enemies=self.game_state['enemies'],
            inventory=self.game_state['inventory'],
            elapsed_time=self.game_state['elapsed_time']
        )
        self.send_to_client(client_socket, game_state_msg)

    def handle_client(self, client_socket):
        """
        Gère les messages d'un client
        Args:
            client_socket: Socket du client
        """
        try:
            while self.running and client_socket in self.clients:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                # Ajouter au buffer
                self.clients[client_socket]['buffer'] += data

                # Traiter les messages complets (séparés par \n)
                while '\n' in self.clients[client_socket]['buffer']:
                    message, self.clients[client_socket]['buffer'] = \
                        self.clients[client_socket]['buffer'].split('\n', 1)

                    if message:
                        self.process_message(client_socket, message)

        except Exception as e:
            print(f"❌ Erreur avec client: {e}")
        finally:
            self.disconnect_client(client_socket)

    def process_message(self, client_socket, message):
        """
        Traite un message reçu d'un client
        Args:
            client_socket: Socket du client
            message: Message à traiter
        """
        msg_type, data = NetworkMessage.decode(message)
        if msg_type is None:
            return

        player_id = self.clients[client_socket]['id']

        if msg_type == MSG_PLAYER_UPDATE:
            # Mettre à jour la position du joueur
            self.game_state['players'][player_id] = {
                'x': data['x'],
                'y': data['y'],
                'health': data['health'],
                'hunger': data['hunger']
            }
            # Relayer aux autres clients
            self.broadcast(message, exclude=client_socket)

        elif msg_type == MSG_INVENTORY_UPDATE:
            # Mettre à jour l'inventaire partagé
            self.game_state['inventory'] = data['inventory']
            # Relayer à tous les clients
            self.broadcast(message)

        elif msg_type == MSG_BUILDING_PLACE:
            # Ajouter le bâtiment à l'état du jeu
            building_data = {
                'type': data['building_type'],
                'grid_x': data['grid_x'],
                'grid_y': data['grid_y']
            }
            self.game_state['buildings'].append(building_data)
            # Relayer à tous les clients
            self.broadcast(message)

        elif msg_type == MSG_ENEMY_SPAWN:
            # Ajouter l'ennemi à l'état du jeu (si le serveur gère les ennemis)
            enemy_id = data.get('enemy_id', self.game_state['next_enemy_id'])
            self.game_state['next_enemy_id'] += 1
            self.game_state['enemies'][enemy_id] = {
                'type': data['enemy_type'],
                'x': data['spawn_x'],
                'y': data['spawn_y'],
                'health': 30  # HP par défaut
            }
            # Relayer à tous les clients
            self.broadcast(message)

        elif msg_type == MSG_ENEMY_DEATH:
            # Retirer l'ennemi
            enemy_id = data['enemy_id']
            if enemy_id in self.game_state['enemies']:
                del self.game_state['enemies'][enemy_id]
            # Relayer à tous les clients
            self.broadcast(message)

        elif msg_type == MSG_HEARTBEAT:
            # Répondre au heartbeat
            pass

    def send_to_client(self, client_socket, message):
        """
        Envoie un message à un client
        Args:
            client_socket: Socket du client
            message: Message à envoyer
        """
        try:
            client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"❌ Erreur envoi au client: {e}")

    def broadcast(self, message, exclude=None):
        """
        Envoie un message à tous les clients
        Args:
            message: Message à envoyer
            exclude: Socket à exclure (optionnel)
        """
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude:
                self.send_to_client(client_socket, message)

    def send_heartbeats(self):
        """Envoie des heartbeats périodiques"""
        while self.running:
            time.sleep(5)
            heartbeat = NetworkMessage.encode(MSG_HEARTBEAT, {})
            self.broadcast(heartbeat)

    def disconnect_client(self, client_socket):
        """
        Déconnecte un client
        Args:
            client_socket: Socket du client
        """
        if client_socket in self.clients:
            player_id = self.clients[client_socket]['id']
            addr = self.clients[client_socket]['addr']

            # Retirer le joueur de l'état du jeu
            if player_id in self.game_state['players']:
                del self.game_state['players'][player_id]

            # Retirer le client de la liste
            del self.clients[client_socket]

            # Notifier les autres clients
            disconnect_msg = NetworkMessage.encode(MSG_DISCONNECT, {'player_id': player_id})
            self.broadcast(disconnect_msg)

            print(f"❌ Joueur {player_id} déconnecté ({addr})")
            print(f"👥 Joueurs restants: {len(self.clients)}/{self.max_players}")

        try:
            client_socket.close()
        except:
            pass

    def stop(self):
        """Arrête le serveur"""
        self.running = False

        # Fermer toutes les connexions clients
        for client_socket in list(self.clients.keys()):
            self.disconnect_client(client_socket)

        # Fermer le socket serveur
        if self.server_socket:
            self.server_socket.close()

        print("✅ Serveur arrêté")


if __name__ == "__main__":
    # Démarrer le serveur
    print("=" * 50)
    print("🎮 FRONTIER FORGE - SERVEUR MULTIJOUEUR")
    print("=" * 50)
    print()

    # Demander le port
    try:
        port = input("Port du serveur (défaut: 5555): ").strip()
        port = int(port) if port else 5555
    except:
        port = 5555

    server = GameServer(host='0.0.0.0', port=port, max_players=4)
    server.start()
