"""
MAIN_MULTIPLAYER.PY
===================
Version multijoueur du jeu. Supporte le mode coopératif via réseau local (Hamachi).
"""

import pygame
import sys
import random
from constants import *
from player import Player
from world import World
from buildings import BUILDING_TYPES, Turret
from ui import UserInterface
from enemies import spawn_zombie_randomly, spawn_mutant_randomly, spawn_wolf_randomly, Zombie, Mutant, Wolf
from quests import QuestManager
from crafting import CraftingSystem, CraftingQueue
from save_system import SaveSystem
from network.client import NetworkClient
from network.protocol import *


class RemotePlayer:
    """Représente un joueur distant"""

    def __init__(self, player_id, x, y):
        self.player_id = player_id
        self.position_x = x
        self.position_y = y
        self.health_points = 100
        self.hunger_level = 100
        self.player_size = 32

    def update(self, x, y, health, hunger):
        """Met à jour les données du joueur distant"""
        self.position_x = x
        self.position_y = y
        self.health_points = health
        self.hunger_level = hunger

    def draw(self, screen, camera_offset_x, camera_offset_y):
        """Dessine le joueur distant"""
        screen_x = self.position_x - camera_offset_x
        screen_y = self.position_y - camera_offset_y

        # Dessiner le joueur (carré cyan pour le différencier)
        player_rect = pygame.Rect(screen_x, screen_y, self.player_size, self.player_size)
        pygame.draw.rect(screen, (0, 255, 255), player_rect)  # Cyan
        pygame.draw.rect(screen, COLOR_WHITE, player_rect, 2)

        # Barre de vie
        health_bar_width = self.player_size
        health_bar_height = 4
        health_percentage = self.health_points / 100

        pygame.draw.rect(screen, COLOR_RED, (screen_x, screen_y - 8, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, COLOR_GREEN, (screen_x, screen_y - 8, health_bar_width * health_percentage, health_bar_height))

        # ID du joueur au-dessus
        font = pygame.font.Font(None, 20)
        id_text = font.render(f"P{self.player_id}", True, COLOR_WHITE)
        screen.blit(id_text, (screen_x, screen_y - 20))


class Game:
    """Classe principale du jeu"""

    def __init__(self):
        """Initialise le jeu et tous ses composants"""
        # Initialiser Pygame
        pygame.init()

        # Créer la fenêtre
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frontier Forge - Prototype de Gestion")

        # Horloge pour contrôler les FPS
        self.clock = pygame.time.Clock()

        # Variables de temps
        self.delta_time = 0  # Temps écoulé depuis la dernière frame
        self.total_elapsed_time = 0  # Temps total de jeu

        # État du jeu
        self.is_running = True
        self.game_state = "playing"  # "playing", "victory", "game_over"

        # Initialiser les composants du jeu
        self.initialize_game()

    def initialize_game(self):
        """Initialise tous les éléments du jeu"""
        # Créer le monde
        self.world = World()

        # Créer le joueur au centre de la carte
        start_position_x = (GRID_SIZE * TILE_SIZE) // 2
        start_position_y = (GRID_SIZE * TILE_SIZE) // 2
        self.player = Player(start_position_x, start_position_y)

        # Listes des entités
        self.buildings_list = []  # Liste de tous les bâtiments construits
        self.enemies_list = []  # Liste de tous les ennemis

        # Interface utilisateur
        self.user_interface = UserInterface()

        # Système de quêtes
        self.quest_manager = QuestManager()

        # Système de crafting
        self.crafting_system = CraftingSystem()
        self.crafting_queue = CraftingQueue()
        self.crafting_menu_open = False

        # Statistiques pour le suivi des quêtes
        self.stats = {
            'metal_collected': 0,
            'food_collected': 0,
            'wood_collected': 0,
            'stone_collected': 0,
            'mines_built': 0,
            'farms_built': 0,
            'generators_built': 0,
            'turrets_built': 0,
            'rockets_built': 0,
            'hospitals_built': 0,
            'laboratories_built': 0,
            'enemies_killed': 0,
            'days_survived': 0
        }

        # Caméra (suit le joueur)
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        # Timers
        self.zombie_spawn_timer = 0  # Timer pour faire apparaître des zombies
        self.mutant_spawn_timer = 0  # Timer pour faire apparaître des mutants
        self.wolf_spawn_timer = 0  # Timer pour faire apparaître des loups

        # Victoire
        self.has_won = False

        # === MULTIJOUEUR ===
        self.is_multiplayer = False
        self.network_client = None
        self.my_player_id = None
        self.remote_players = {}  # {player_id: RemotePlayer}
        self.last_network_update = 0  # Timer pour limiter les mises à jour réseau
        self.next_enemy_id = 1  # ID unique pour les ennemis en multijoueur

    def setup_multiplayer(self, server_host, server_port):
        """
        Configure le mode multijoueur
        Args:
            server_host: IP du serveur
            server_port: Port du serveur
        Returns:
            bool: True si connexion réussie
        """
        self.network_client = NetworkClient()

        # Définir les callbacks
        self.network_client.on_connect = self.on_network_connect
        self.network_client.on_disconnect = self.on_network_disconnect
        self.network_client.on_player_update = self.on_network_player_update
        self.network_client.on_inventory_update = self.on_network_inventory_update
        self.network_client.on_building_place = self.on_network_building_place
        self.network_client.on_enemy_spawn = self.on_network_enemy_spawn
        self.network_client.on_enemy_update = self.on_network_enemy_update
        self.network_client.on_enemy_death = self.on_network_enemy_death
        self.network_client.on_game_state = self.on_network_game_state

        # Se connecter
        if self.network_client.connect(server_host, server_port):
            self.is_multiplayer = True
            print("🌐 Mode multijoueur activé")
            return True
        else:
            print("❌ Échec de connexion au serveur")
            return False

    # === CALLBACKS RÉSEAU ===

    def on_network_connect(self, player_id):
        """Appelé quand on reçoit notre ID du serveur"""
        self.my_player_id = player_id
        print(f"✅ Connecté en tant que Joueur {player_id}")

    def on_network_disconnect(self, player_id):
        """Appelé quand un autre joueur se déconnecte"""
        if player_id in self.remote_players:
            del self.remote_players[player_id]
            print(f"👋 Joueur {player_id} déconnecté")

    def on_network_player_update(self, data):
        """Appelé quand on reçoit une mise à jour d'un autre joueur"""
        player_id = data['player_id']

        # Ignorer notre propre mise à jour
        if player_id == self.my_player_id:
            return

        # Créer ou mettre à jour le joueur distant
        if player_id not in self.remote_players:
            self.remote_players[player_id] = RemotePlayer(
                player_id,
                data['x'],
                data['y']
            )
        else:
            self.remote_players[player_id].update(
                data['x'],
                data['y'],
                data['health'],
                data['hunger']
            )

    def on_network_inventory_update(self, inventory):
        """Appelé quand l'inventaire partagé est mis à jour"""
        # Mettre à jour notre inventaire avec celui du serveur
        for resource, amount in inventory.items():
            self.player.inventory[resource] = amount

    def on_network_building_place(self, building_type, grid_x, grid_y):
        """Appelé quand un bâtiment est placé par un autre joueur"""
        # Ajouter le bâtiment localement
        if building_type in BUILDING_TYPES:
            building_class = BUILDING_TYPES[building_type]['class']
            new_building = building_class(grid_x, grid_y)
            self.buildings_list.append(new_building)
            print(f"🏗️ Bâtiment {building_type} placé en ({grid_x}, {grid_y})")

    def on_network_enemy_spawn(self, enemy_id, enemy_type, spawn_x, spawn_y):
        """Appelé quand un ennemi apparaît (spawné par un autre client)"""
        # Créer l'ennemi localement selon son type
        enemy_classes = {
            'zombie': Zombie,
            'mutant': Mutant,
            'wolf': Wolf
        }

        if enemy_type in enemy_classes:
            enemy = enemy_classes[enemy_type](spawn_x, spawn_y)
            # Stocker l'ID réseau pour la synchronisation
            enemy.network_id = enemy_id
            self.enemies_list.append(enemy)
            print(f"👾 Ennemi {enemy_type} (ID:{enemy_id}) spawné à ({spawn_x}, {spawn_y})")

    def on_network_enemy_update(self, enemy_id, x, y, health):
        """Appelé quand un ennemi est mis à jour"""
        # Trouver l'ennemi par son ID réseau
        for enemy in self.enemies_list:
            if hasattr(enemy, 'network_id') and enemy.network_id == enemy_id:
                enemy.position_x = x
                enemy.position_y = y
                enemy.health_points = health
                break

    def on_network_enemy_death(self, enemy_id):
        """Appelé quand un ennemi meurt"""
        # Retirer l'ennemi de la liste
        for i, enemy in enumerate(self.enemies_list):
            if hasattr(enemy, 'network_id') and enemy.network_id == enemy_id:
                self.enemies_list.pop(i)
                print(f"💀 Ennemi (ID:{enemy_id}) tué")
                break

    def on_network_game_state(self, data):
        """Appelé quand on reçoit l'état complet du jeu (synchronisation initiale)"""
        print("📥 Synchronisation de l'état du jeu...")

        # Charger les joueurs distants
        for player_id_str, player_data in data['players'].items():
            player_id = int(player_id_str)
            if player_id != self.my_player_id:
                self.remote_players[player_id] = RemotePlayer(
                    player_id,
                    player_data['x'],
                    player_data['y']
                )
                self.remote_players[player_id].update(
                    player_data['x'],
                    player_data['y'],
                    player_data['health'],
                    player_data['hunger']
                )

        # Charger les bâtiments
        for building_data in data['buildings']:
            building_type = building_data['type']
            if building_type in BUILDING_TYPES:
                building_class = BUILDING_TYPES[building_type]['class']
                new_building = building_class(
                    building_data['grid_x'],
                    building_data['grid_y']
                )
                self.buildings_list.append(new_building)

        # Charger les ennemis
        enemy_classes = {
            'zombie': Zombie,
            'mutant': Mutant,
            'wolf': Wolf
        }
        for enemy_id_str, enemy_data in data.get('enemies', {}).items():
            enemy_id = int(enemy_id_str)
            enemy_type = enemy_data['type']
            if enemy_type in enemy_classes:
                enemy = enemy_classes[enemy_type](enemy_data['x'], enemy_data['y'])
                enemy.health_points = enemy_data.get('health', 30)
                enemy.network_id = enemy_id
                self.enemies_list.append(enemy)

        # Charger l'inventaire partagé
        for resource, amount in data['inventory'].items():
            self.player.inventory[resource] = amount

        print(f"✅ Synchronisation complète ({len(self.remote_players)} autres joueurs, {len(self.buildings_list)} bâtiments, {len(self.enemies_list)} ennemis)")

    def load_game_state(self, save_data):
        """
        Restaure l'état du jeu depuis les données de sauvegarde
        Args:
            save_data: Dictionnaire contenant les données sauvegardées
        """
        # Restaurer le joueur
        self.player.position_x = save_data['player']['position_x']
        self.player.position_y = save_data['player']['position_y']
        self.player.inventory = save_data['player']['inventory']
        self.player.health_points = save_data['player']['health_points']
        self.player.hunger_level = save_data['player']['hunger_level']
        self.player.is_alive = save_data['player']['is_alive']

        # Restaurer le monde (terrain)
        self.world.grid_terrain = save_data['world']['grid_terrain']
        self.world.original_terrain = save_data['world'].get('original_terrain', self.world.grid_terrain)
        # Restaurer les tiles épuisées
        depleted_data = save_data['world'].get('depleted_tiles', [])
        self.world.depleted_tiles = {(entry[0], entry[1]): entry[2] for entry in depleted_data}

        # Restaurer les bâtiments
        self.buildings_list = []
        for building_data in save_data['buildings']:
            building_type = building_data['type']
            building_class = BUILDING_TYPES[building_type]['class']
            building = building_class(building_data['grid_x'], building_data['grid_y'])
            building.production_timer = building_data.get('production_timer', 0)

            # Restaurer niveau de recherche pour laboratoire
            if hasattr(building, 'research_level'):
                building.research_level = building_data.get('research_level', 0)

            self.buildings_list.append(building)

        # Restaurer les ennemis
        enemy_classes = {'zombie': Zombie, 'mutant': Mutant, 'wolf': Wolf}
        self.enemies_list = []
        for enemy_data in save_data['enemies']:
            enemy_type = enemy_data['type']
            if enemy_type in enemy_classes:
                enemy_class = enemy_classes[enemy_type]
                enemy = enemy_class(enemy_data['position_x'], enemy_data['position_y'])
                enemy.health_points = enemy_data['health_points']
                enemy.is_alive = enemy_data['is_alive']
                self.enemies_list.append(enemy)

        # Restaurer les timers
        self.total_elapsed_time = save_data['timers']['total_elapsed_time']
        self.zombie_spawn_timer = save_data['timers']['zombie_spawn_timer']
        self.mutant_spawn_timer = save_data['timers'].get('mutant_spawn_timer', 0)
        self.wolf_spawn_timer = save_data['timers'].get('wolf_spawn_timer', 0)

        # Restaurer l'état du jeu
        self.game_state = save_data['game_state']
        self.has_won = save_data['has_won']

        # Restaurer les stats
        self.stats = save_data.get('stats', self.stats)

        # Restaurer les quêtes
        self.quest_manager.active_quests = save_data.get('active_quests', [])
        self.quest_manager.completed_quests = save_data.get('completed_quests', [])

        # Restaurer la queue de crafting
        self.crafting_queue.queue = save_data.get('crafting_queue', [])

        print("Partie chargée avec succès !")

    def handle_events(self):
        """Gère tous les événements (clavier, souris, etc.)"""
        for event in pygame.event.get():
            # Fermeture de la fenêtre
            if event.type == pygame.QUIT:
                self.is_running = False

            # Touches du clavier
            if event.type == pygame.KEYDOWN:
                # Échap pour quitter
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                # Touche E pour manger
                if event.key == pygame.K_e:
                    if self.player.eat_food():
                        print("Vous avez mangé de la nourriture !")

                # Touche M pour utiliser médecine
                if event.key == pygame.K_m:
                    if self.player.use_medicine():
                        print(f"Vous avez utilisé une médecine ! (+{MEDICINE_HEAL_AMOUNT} HP)")
                    else:
                        print("Vous n'avez pas de médecine !")

                # Touche C pour toggle menu crafting
                if event.key == pygame.K_c:
                    self.crafting_menu_open = not self.crafting_menu_open

                # F5 pour sauvegarder
                if event.key == pygame.K_F5:
                    SaveSystem.save_game(self)

                # F9 pour charger
                if event.key == pygame.K_F9:
                    save_data = SaveSystem.load_game()
                    if save_data:
                        self.load_game_state(save_data)

                # Touches 1-9 et 0 pour sélectionner un bâtiment à construire
                building_keys = {
                    pygame.K_1: 'mine',
                    pygame.K_2: 'farm',
                    pygame.K_3: 'generator',
                    pygame.K_4: 'turret',
                    pygame.K_5: 'rocket',
                    pygame.K_6: 'hospital',
                    pygame.K_7: 'laboratory',
                    pygame.K_8: 'wall',
                    pygame.K_9: 'warehouse',
                    pygame.K_0: 'factory'
                }

                if event.key in building_keys:
                    selected_building = building_keys[event.key]
                    # Toggle : si déjà sélectionné, désélectionner
                    if self.user_interface.build_mode == selected_building:
                        self.user_interface.build_mode = None
                    else:
                        self.user_interface.build_mode = selected_building

            # Clic de souris
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    self.handle_left_click()

    def handle_left_click(self):
        """Gère le clic gauche de la souris (récolte, construction ou crafting)"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Si le menu crafting est ouvert, gérer les clics dans le menu
        if self.crafting_menu_open:
            self.handle_crafting_click(mouse_x, mouse_y)
            return

        # Si on est en mode construction
        if self.user_interface.build_mode:
            self.try_build_building(mouse_x, mouse_y)
        else:
            # Sinon, essayer de récolter une ressource
            # Sauvegarder l'inventaire avant récolte pour tracker ce qui a été récolté
            old_inventory = self.player.inventory.copy()
            harvested = self.player.harvest_resource(
                self.world,
                mouse_x,
                mouse_y,
                self.camera_offset_x,
                self.camera_offset_y
            )

            # Mettre à jour les statistiques de récolte
            if harvested:
                for resource in [RESOURCE_METAL, RESOURCE_FOOD, RESOURCE_WOOD, RESOURCE_STONE]:
                    if self.player.inventory[resource] > old_inventory[resource]:
                        stat_key = f"{resource}_collected"
                        if stat_key in self.stats:
                            self.stats[stat_key] += (self.player.inventory[resource] - old_inventory[resource])

    def try_build_building(self, mouse_x, mouse_y):
        """
        Tente de construire un bâtiment à la position de la souris
        Args:
            mouse_x, mouse_y: Position de la souris à l'écran
        """
        building_type = self.user_interface.build_mode
        building_info = BUILDING_TYPES[building_type]

        # Vérifier si le joueur a les ressources
        if not self.player.has_resources(building_info['cost']):
            print(f"Pas assez de ressources pour construire {building_info['name']}")
            return

        # Convertir la position souris en position grille
        grid_x = (mouse_x + self.camera_offset_x) // TILE_SIZE
        grid_y = (mouse_y + self.camera_offset_y) // TILE_SIZE

        # Vérifier que c'est dans les limites
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return

        # Vérifier que la case est libre
        if not self.world.is_tile_buildable(grid_x, grid_y, self.buildings_list):
            print("Emplacement déjà occupé !")
            return

        # Construire le bâtiment
        building_class = building_info['class']
        new_building = building_class(grid_x, grid_y)
        self.buildings_list.append(new_building)

        # Dépenser les ressources
        self.player.spend_resources(building_info['cost'])

        # Mettre à jour les statistiques de construction
        stat_key = f"{building_type}s_built"
        if stat_key in self.stats:
            self.stats[stat_key] += 1

        # Vérifier si c'est une fusée (victoire)
        if building_type == 'rocket':
            self.has_won = True
            self.game_state = "victory"

        print(f"{building_info['name']} construit(e) à ({grid_x}, {grid_y})")

        # Envoyer au serveur en multijoueur
        if self.is_multiplayer and self.network_client and self.network_client.connected:
            self.network_client.send_building_place(building_type, grid_x, grid_y)

    def handle_movement(self):
        """Gère le déplacement du joueur avec les touches du clavier"""
        keys = pygame.key.get_pressed()

        direction_x = 0
        direction_y = 0

        # ZQSD ou flèches pour se déplacer
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            direction_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            direction_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction_y = 1

        # Déplacer le joueur
        if direction_x != 0 or direction_y != 0:
            self.player.move(direction_x, direction_y, self.world)

    def update(self):
        """Met à jour tous les éléments du jeu"""
        # Ne rien mettre à jour si le jeu est terminé
        if self.game_state != "playing":
            return

        # Mettre à jour le joueur
        self.player.update(self.delta_time)

        # Mettre à jour le monde (régénération des ressources)
        self.world.update(self.delta_time)

        # Vérifier si le joueur est mort
        if not self.player.is_alive:
            self.game_state = "game_over"
            return

        # Mettre à jour tous les bâtiments (production)
        for building in self.buildings_list:
            building.update(self.delta_time, self.player.inventory)

            # Si c'est une tourelle, elle attaque les ennemis
            if isinstance(building, Turret):
                building.attack_enemies(self.enemies_list, self.delta_time)

        # Traiter les demandes de craft automatique des usines
        if '_factory_craft' in self.player.inventory and self.player.inventory['_factory_craft']:
            for recipe_id in self.player.inventory['_factory_craft']:
                # Essayer de crafter la recette
                if self.crafting_system.can_craft(recipe_id, self.player.inventory):
                    # Consommer les ressources
                    recipe = self.crafting_system.get_recipe(recipe_id)
                    if recipe:
                        for resource, amount in recipe.ingredients.items():
                            self.player.inventory[resource] -= amount
                        # Ajouter le produit
                        self.player.inventory[recipe.result] = self.player.inventory.get(recipe.result, 0) + recipe.result_amount
                        print(f"Usine a fabriqué : {recipe.result} x{recipe.result_amount}")
            # Vider la liste des crafts de l'usine
            self.player.inventory['_factory_craft'] = []

        # Appliquer les soins des hôpitaux
        if '_hospital_heal' in self.player.inventory and self.player.inventory['_hospital_heal'] > 0:
            heal_amount = self.player.inventory['_hospital_heal']
            self.player.health_points = min(PLAYER_INITIAL_HEALTH, self.player.health_points + heal_amount)
            self.player.inventory['_hospital_heal'] = 0

        # Mettre à jour tous les ennemis
        for enemy in self.enemies_list:
            enemy.update(self.delta_time, self.player, self.buildings_list)

        # Compter les ennemis tués avant de les retirer
        enemies_before = len(self.enemies_list)

        # Envoyer les morts d'ennemis en multijoueur
        if self.is_multiplayer and self.network_client and self.network_client.connected:
            for enemy in self.enemies_list:
                if not enemy.is_alive and hasattr(enemy, 'network_id'):
                    self.network_client.send_enemy_death(enemy.network_id)

        self.enemies_list = [enemy for enemy in self.enemies_list if enemy.is_alive]
        enemies_after = len(self.enemies_list)
        enemies_killed = enemies_before - enemies_after
        if enemies_killed > 0:
            self.stats['enemies_killed'] += enemies_killed

        # Retirer les murs détruits
        walls_before = len([b for b in self.buildings_list if hasattr(b, 'is_obstacle') and b.is_obstacle])
        self.buildings_list = [
            building for building in self.buildings_list
            if not (hasattr(building, 'durability') and building.durability <= 0)
        ]
        walls_after = len([b for b in self.buildings_list if hasattr(b, 'is_obstacle') and b.is_obstacle])
        walls_destroyed = walls_before - walls_after
        if walls_destroyed > 0:
            print(f"{walls_destroyed} mur(s) détruit(s) !")

        # Calculer si c'est la nuit pour spawn accéléré
        day_progress = (self.total_elapsed_time % SECONDS_PER_DAY) / SECONDS_PER_DAY
        is_night = day_progress > DAY_PHASE_DURATION
        spawn_multiplier = NIGHT_ENEMY_SPAWN_MULTIPLIER if is_night else 1.0

        # Faire apparaître des zombies périodiquement (plus rapide la nuit)
        self.zombie_spawn_timer += self.delta_time * spawn_multiplier
        if self.zombie_spawn_timer >= ZOMBIE_SPAWN_INTERVAL:
            self.zombie_spawn_timer = 0
            map_size = GRID_SIZE * TILE_SIZE
            new_zombie = spawn_zombie_randomly(map_size)

            # Assigner un ID réseau en multijoueur
            if self.is_multiplayer:
                new_zombie.network_id = self.next_enemy_id
                self.next_enemy_id += 1
                # Envoyer au serveur
                if self.network_client and self.network_client.connected:
                    self.network_client.send_enemy_spawn(
                        new_zombie.network_id,
                        'zombie',
                        new_zombie.position_x,
                        new_zombie.position_y
                    )

            self.enemies_list.append(new_zombie)
            print("Un zombie est apparu !")

        # Faire apparaître des mutants périodiquement (plus rapide la nuit)
        self.mutant_spawn_timer += self.delta_time * spawn_multiplier
        if self.mutant_spawn_timer >= MUTANT_SPAWN_INTERVAL:
            self.mutant_spawn_timer = 0
            map_size = GRID_SIZE * TILE_SIZE
            new_mutant = spawn_mutant_randomly(map_size)

            # Assigner un ID réseau en multijoueur
            if self.is_multiplayer:
                new_mutant.network_id = self.next_enemy_id
                self.next_enemy_id += 1
                # Envoyer au serveur
                if self.network_client and self.network_client.connected:
                    self.network_client.send_enemy_spawn(
                        new_mutant.network_id,
                        'mutant',
                        new_mutant.position_x,
                        new_mutant.position_y
                    )

            self.enemies_list.append(new_mutant)
            print("Un mutant est apparu !")

        # Faire apparaître des loups périodiquement en meutes (plus rapide la nuit)
        self.wolf_spawn_timer += self.delta_time * spawn_multiplier
        if self.wolf_spawn_timer >= WOLF_SPAWN_INTERVAL:
            self.wolf_spawn_timer = 0
            map_size = GRID_SIZE * TILE_SIZE
            pack_size = random.randint(1, 3)  # Meute de 1 à 3 loups
            for _ in range(pack_size):
                new_wolf = spawn_wolf_randomly(map_size)

                # Assigner un ID réseau en multijoueur
                if self.is_multiplayer:
                    new_wolf.network_id = self.next_enemy_id
                    self.next_enemy_id += 1
                    # Envoyer au serveur
                    if self.network_client and self.network_client.connected:
                        self.network_client.send_enemy_spawn(
                            new_wolf.network_id,
                            'wolf',
                            new_wolf.position_x,
                            new_wolf.position_y
                        )

                self.enemies_list.append(new_wolf)
            print(f"Une meute de {pack_size} loup(s) est apparue !")

        # Mettre à jour la caméra (centrer sur le joueur)
        self.update_camera()

        # Mettre à jour la queue de crafting
        completed_crafts = self.crafting_queue.update(self.delta_time, self.player.inventory, self.crafting_system)
        if completed_crafts > 0:
            print(f"{completed_crafts} craft(s) terminé(s) !")

        # Incrémenter le temps total
        self.total_elapsed_time += self.delta_time

        # Mettre à jour les jours survécus
        current_day = int(self.total_elapsed_time // SECONDS_PER_DAY) + 1
        self.stats['days_survived'] = current_day

        # Mettre à jour la progression des quêtes
        self.quest_manager.update_all_progress(self.stats)

        # Vérifier la complétion des quêtes
        for quest_id in list(self.quest_manager.active_quests):
            quest = self.quest_manager.quests[quest_id]
            if quest.check_completion() and not quest.is_completed:
                # Compléter la quête et donner les récompenses
                rewards = self.quest_manager.complete_quest(quest_id)
                for resource, amount in rewards.items():
                    self.player.inventory[resource] = self.player.inventory.get(resource, 0) + amount
                print(f"Quête complétée : {quest.title} !")

                # Activer les quêtes suivantes selon la progression
                if quest_id == 'tutorial_1':
                    self.quest_manager.activate_quest('tutorial_2')
                elif quest_id == 'tutorial_2':
                    self.quest_manager.activate_quest('defense_1')
                    self.quest_manager.activate_quest('survival_1')
                elif quest_id == 'defense_1' or quest_id == 'survival_1':
                    if 'expansion_1' not in self.quest_manager.active_quests and 'expansion_1' not in self.quest_manager.completed_quests:
                        self.quest_manager.activate_quest('expansion_1')

        # Vérifier la victoire par survie
        if current_day > SURVIVAL_DAYS_TO_WIN and not self.has_won:
            self.has_won = True
            self.game_state = "victory"

        # === MISE À JOUR RÉSEAU ===
        if self.is_multiplayer and self.network_client and self.network_client.connected:
            # Envoyer notre position toutes les 0.1 secondes
            self.last_network_update += self.delta_time
            if self.last_network_update >= 0.1:
                self.last_network_update = 0
                self.network_client.send_player_update(
                    self.player.position_x,
                    self.player.position_y,
                    self.player.health_points,
                    self.player.hunger_level
                )

                # Envoyer l'inventaire partagé
                self.network_client.send_inventory_update(self.player.inventory)

    def update_camera(self):
        """Met à jour la position de la caméra pour suivre le joueur"""
        # Centrer la caméra sur le joueur
        self.camera_offset_x = self.player.position_x - SCREEN_WIDTH // 2
        self.camera_offset_y = self.player.position_y - SCREEN_HEIGHT // 2

        # Limiter la caméra aux bords de la carte
        map_width = GRID_SIZE * TILE_SIZE
        map_height = GRID_SIZE * TILE_SIZE

        self.camera_offset_x = max(0, min(self.camera_offset_x, map_width - SCREEN_WIDTH))
        self.camera_offset_y = max(0, min(self.camera_offset_y, map_height - SCREEN_HEIGHT))

    def render(self):
        """Dessine tous les éléments du jeu à l'écran"""
        # Fond noir
        self.screen.fill(COLOR_BLACK)

        # Dessiner le monde (grille de terrain)
        self.world.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # Dessiner tous les bâtiments
        for building in self.buildings_list:
            building.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # Dessiner tous les ennemis
        for enemy in self.enemies_list:
            enemy.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # Dessiner le joueur
        self.player.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # Dessiner les joueurs distants (multijoueur)
        if self.is_multiplayer:
            for remote_player in self.remote_players.values():
                remote_player.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # Appliquer l'overlay de nuit si c'est la nuit
        day_progress = (self.total_elapsed_time % SECONDS_PER_DAY) / SECONDS_PER_DAY
        self.is_night = day_progress > DAY_PHASE_DURATION
        if self.is_night:
            night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            night_overlay.fill((*NIGHT_TINT_COLOR, NIGHT_TINT_ALPHA))
            self.screen.blit(night_overlay, (0, 0))

        # Dessiner l'interface utilisateur
        self.user_interface.draw_player_stats(self.screen, self.player)
        self.user_interface.draw_inventory(self.screen, self.player)
        self.user_interface.draw_building_menu(self.screen, self.player)
        self.user_interface.draw_game_time(self.screen, self.total_elapsed_time)
        self.user_interface.draw_controls_help(self.screen)
        self.user_interface.draw_quest_panel(self.screen, self.quest_manager)

        # Dessiner le menu de crafting si ouvert
        if self.crafting_menu_open:
            self.user_interface.draw_crafting_menu(self.screen, self.crafting_system, self.player.inventory)

        # Dessiner les écrans de fin
        if self.game_state == "victory":
            self.user_interface.draw_victory_screen(self.screen)
        elif self.game_state == "game_over":
            self.user_interface.draw_game_over_screen(self.screen)

        # Mettre à jour l'affichage
        pygame.display.flip()

    def handle_crafting_click(self, mouse_x, mouse_y):
        """
        Gère les clics dans le menu de crafting
        Args:
            mouse_x, mouse_y: Position de la souris
        """
        # Dimensions et position du menu
        menu_width = 600
        menu_height = 500
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        # Vérifier si le clic est dans le menu
        if not (menu_x <= mouse_x <= menu_x + menu_width and menu_y <= mouse_y <= menu_y + menu_height):
            return

        # Position de départ des recettes
        y_offset = menu_y + 100
        box_height = 80

        # Vérifier sur quelle recette on a cliqué
        recipes = self.crafting_system.get_all_recipes()
        for i, recipe in enumerate(recipes):
            box_y = y_offset + i * (box_height + 10)

            # Vérifier si le clic est dans cette boîte de recette
            if box_y <= mouse_y <= box_y + box_height:
                # Vérifier si on peut crafter
                if self.crafting_system.can_craft(recipe.recipe_id, self.player.inventory):
                    # Consommer les ingrédients immédiatement
                    for resource, amount in recipe.ingredients.items():
                        self.player.inventory[resource] -= amount

                    # Ajouter à la queue de crafting (le résultat viendra après craft_time)
                    self.crafting_queue.add_to_queue(recipe.recipe_id, recipe.craft_time)
                    print(f"Craft de {recipe.name} commencé ({recipe.craft_time}s)...")
                else:
                    print(f"Pas assez de ressources pour {recipe.name}")
                break

    def run(self):
        """Boucle principale du jeu"""
        print("=== FRONTIER FORGE - Prototype de Gestion ===")
        print("Objectifs : Construire une fusée OU survivre 10 jours")
        print("Contrôles : ZQSD/Flèches pour bouger, Clic gauche pour récolter")
        print("            1-7 pour sélectionner un bâtiment, E pour manger, C pour crafting")
        print("            F5 pour sauvegarder, F9 pour charger")
        print("Bon courage, commandant !")
        print("=" * 50)

        # Vérifier si une sauvegarde existe
        if SaveSystem.save_exists():
            print("\n[!] Une sauvegarde existe ! Appuyez sur F9 pour charger ou continuez pour une nouvelle partie.\n")

        while self.is_running:
            # Calculer le temps écoulé depuis la dernière frame (en secondes)
            self.delta_time = self.clock.tick(FRAMES_PER_SECOND) / 1000.0

            # Gérer les événements
            self.handle_events()

            # Gérer le déplacement
            self.handle_movement()

            # Mettre à jour le jeu
            self.update()

            # Dessiner le jeu
            self.render()

        # Fermer Pygame proprement
        pygame.quit()
        sys.exit()


# Point d'entrée du programme
if __name__ == "__main__":
    print("=" * 60)
    print("🎮 FRONTIER FORGE - MODE MULTIJOUEUR COOPÉRATIF")
    print("=" * 60)
    print()
    print("📋 Instructions:")
    print("  - L'hôte doit lancer le serveur (start_server.py) d'abord")
    print("  - Les autres joueurs rejoignent via l'IP Hamachi de l'hôte")
    print("  - Consultez MULTIPLAYER_GUIDE.md pour plus de détails")
    print()

    # Demander l'IP et le port du serveur
    server_host = input("IP du serveur (localhost pour hôte, ou IP Hamachi): ").strip()
    if not server_host:
        server_host = "localhost"

    server_port_input = input("Port du serveur (défaut: 5555): ").strip()
    try:
        server_port = int(server_port_input) if server_port_input else 5555
    except:
        server_port = 5555

    print()
    print("🚀 Démarrage du jeu multijoueur...")
    print()

    # Créer le jeu
    game = Game()

    # Configurer le multijoueur
    if game.setup_multiplayer(server_host, server_port):
        print("✅ Prêt à jouer en multijoueur !")
        print()
        game.run()
    else:
        print("❌ Impossible de se connecter au serveur.")
        print("Vérifiez que:")
        print("  1. Le serveur est démarré (start_server.py)")
        print("  2. L'IP et le port sont corrects")
        print("  3. Hamachi est connecté au même réseau")
        print("  4. Le pare-feu autorise la connexion")

