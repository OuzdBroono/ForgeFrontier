"""
MAIN.PY
=======
Fichier principal du jeu. Contient la boucle de jeu et gère tous les systèmes.
C'est ici que tout s'orchestre : mise à jour des entités, rendu, gestion des événements.
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


class Game:
    """Classe principale du jeu"""

    def __init__(self):
        """Initialise le jeu et tous ses composants"""
        # Initialiser Pygame
        pygame.init()

        # Détecter la résolution de l'écran et calculer la taille de la fenêtre
        self.screen_width, self.screen_height = self.get_optimal_screen_size()

        # Créer la fenêtre (mode fenêtré par défaut)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Frontier Forge - Prototype de Gestion")

        print(f"🖥️ Résolution de la fenêtre : {self.screen_width}x{self.screen_height}")

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

    def get_optimal_screen_size(self):
        """
        Détecte la résolution de l'écran et calcule la taille optimale de la fenêtre
        Returns:
            tuple: (largeur, hauteur) optimales
        """
        # Obtenir les informations sur l'écran
        display_info = pygame.display.Info()
        monitor_width = display_info.current_w
        monitor_height = display_info.current_h

        # Calculer la taille de la fenêtre (85% de la hauteur de l'écran)
        target_height = int(monitor_height * SCREEN_SCALE_PERCENT)
        # Garder le ratio 2:1 (comme 1800:900)
        target_width = target_height * 2

        # S'assurer que la largeur ne dépasse pas 90% de l'écran
        max_width = int(monitor_width * 0.9)
        if target_width > max_width:
            target_width = max_width
            target_height = target_width // 2

        print(f"📺 Résolution écran : {monitor_width}x{monitor_height}")
        print(f"🎮 Taille fenêtre : {target_width}x{target_height} ({int(SCREEN_SCALE_PERCENT*100)}% de l'écran)")

        return target_width, target_height

    def toggle_fullscreen(self):
        """Bascule entre mode fenêtré et plein écran"""
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            # Mode plein écran
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Obtenir la taille réelle en plein écran
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
            print(f"🖥️ Mode plein écran : {self.screen_width}x{self.screen_height}")
        else:
            # Mode fenêtré
            self.screen_width, self.screen_height = self.get_optimal_screen_size()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            print(f"🪟 Mode fenêtré : {self.screen_width}x{self.screen_height}")

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

                # F11 pour basculer plein écran
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

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
            self.enemies_list.append(new_zombie)
            print("Un zombie est apparu !")

        # Faire apparaître des mutants périodiquement (plus rapide la nuit)
        self.mutant_spawn_timer += self.delta_time * spawn_multiplier
        if self.mutant_spawn_timer >= MUTANT_SPAWN_INTERVAL:
            self.mutant_spawn_timer = 0
            map_size = GRID_SIZE * TILE_SIZE
            new_mutant = spawn_mutant_randomly(map_size)
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

    def update_camera(self):
        """Met à jour la position de la caméra pour suivre le joueur"""
        # Centrer la caméra sur le joueur
        self.camera_offset_x = self.player.position_x - self.screen_width // 2
        self.camera_offset_y = self.player.position_y - self.screen_height // 2

        # Limiter la caméra aux bords de la carte
        map_width = GRID_SIZE * TILE_SIZE
        map_height = GRID_SIZE * TILE_SIZE

        self.camera_offset_x = max(0, min(self.camera_offset_x, map_width - self.screen_width))
        self.camera_offset_y = max(0, min(self.camera_offset_y, map_height - self.screen_height))

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

        # Appliquer l'overlay de nuit si c'est la nuit
        day_progress = (self.total_elapsed_time % SECONDS_PER_DAY) / SECONDS_PER_DAY
        self.is_night = day_progress > DAY_PHASE_DURATION
        if self.is_night:
            night_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
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
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2

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
    game = Game()
    game.run()

