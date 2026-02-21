"""
UI.PY
=====
Ce fichier gère l'interface utilisateur : HUD, inventaire, statistiques, menus.
Affiche toutes les informations importantes pour le joueur.
"""

import pygame
from constants import *
from buildings import BUILDING_TYPES


class UserInterface:
    """Classe gérant l'interface utilisateur du jeu"""

    def __init__(self):
        """Initialise l'interface utilisateur"""
        # Police de texte (None = police par défaut, 20 = taille)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 18)

        # Mode de construction actuel (None ou type de bâtiment)
        self.build_mode = None

    def draw_player_stats(self, screen, player):
        """
        Affiche les statistiques du joueur (vie, faim)
        Args:
            screen: Surface Pygame
            player: Instance du joueur
        """
        # Fond semi-transparent pour le HUD
        hud_background = pygame.Surface((300, 120), pygame.SRCALPHA)
        hud_background.fill((0, 0, 0, 180))  # Noir avec transparence
        screen.blit(hud_background, (10, 10))

        # Afficher la vie
        health_text = self.font_normal.render(f"Vie: {int(player.health_points)}/100", True, COLOR_WHITE)
        screen.blit(health_text, (20, 20))

        # Barre de vie
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = player.health_points / 100
        pygame.draw.rect(screen, COLOR_RED, (20, 45, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, COLOR_GREEN, (20, 45, health_bar_width * health_percentage, health_bar_height))
        pygame.draw.rect(screen, COLOR_WHITE, (20, 45, health_bar_width, health_bar_height), 2)

        # Afficher la faim
        hunger_text = self.font_normal.render(f"Faim: {int(player.hunger_level)}/100", True, COLOR_WHITE)
        screen.blit(hunger_text, (20, 75))

        # Barre de faim
        hunger_percentage = player.hunger_level / 100
        pygame.draw.rect(screen, COLOR_RED, (20, 100, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, COLOR_YELLOW, (20, 100, health_bar_width * hunger_percentage, health_bar_height))
        pygame.draw.rect(screen, COLOR_WHITE, (20, 100, health_bar_width, health_bar_height), 2)

    def draw_inventory(self, screen, player):
        """
        Affiche l'inventaire du joueur
        Args:
            screen: Surface Pygame
            player: Instance du joueur
        """
        # Fond pour l'inventaire (coin supérieur droit)
        inventory_x = SCREEN_WIDTH - 220
        inventory_background = pygame.Surface((210, 110), pygame.SRCALPHA)
        inventory_background.fill((0, 0, 0, 180))
        screen.blit(inventory_background, (inventory_x, 10))

        # Titre
        inventory_title = self.font_normal.render("Inventaire:", True, COLOR_WHITE)
        screen.blit(inventory_title, (inventory_x + 10, 20))

        # Afficher les ressources
        vertical_offset = 50
        for resource_name, amount in player.inventory.items():
            # Icône de couleur selon la ressource
            icon_color = COLOR_GRAY if resource_name == RESOURCE_METAL else \
                COLOR_YELLOW if resource_name == RESOURCE_FOOD else \
                COLOR_ORANGE if resource_name == RESOURCE_ENERGY else \
                COLOR_WOOD_BROWN if resource_name == RESOURCE_WOOD else \
                COLOR_STONE_GRAY if resource_name == RESOURCE_STONE else COLOR_WHITE

            # Dessiner un petit carré coloré comme icône
            pygame.draw.rect(screen, icon_color, (inventory_x + 10, vertical_offset, 15, 15))

            # Afficher le nom et la quantité
            resource_text = self.font_small.render(f"{resource_name.capitalize()}: {amount}", True, COLOR_WHITE)
            screen.blit(resource_text, (inventory_x + 35, vertical_offset))

            vertical_offset += 22

    def draw_building_menu(self, screen, player):
        """
        Affiche le menu de construction (en bas de l'écran)
        Args:
            screen: Surface Pygame
            player: Instance du joueur
        """
        menu_height = 120
        menu_y = SCREEN_HEIGHT - menu_height

        # Fond du menu
        menu_background = pygame.Surface((SCREEN_WIDTH, menu_height), pygame.SRCALPHA)
        menu_background.fill((0, 0, 0, 200))
        screen.blit(menu_background, (0, menu_y))

        # Titre
        title_text = self.font_normal.render("Construction (1-8): ", True, COLOR_WHITE)
        screen.blit(title_text, (10, menu_y + 10))

        # Afficher chaque type de bâtiment
        button_width = 95  # Réduit pour afficher 8 bâtiments
        button_height = 70
        button_spacing = 8
        start_x = 10
        start_y = menu_y + 40

        building_keys = ['mine', 'farm', 'generator', 'turret', 'rocket', 'hospital', 'laboratory', 'wall']
        for index, building_key in enumerate(building_keys):
            building_info = BUILDING_TYPES[building_key]
            button_x = start_x + index * (button_width + button_spacing)

            # Vérifier si le joueur a les ressources
            has_resources = player.has_resources(building_info['cost'])
            button_color = COLOR_DARK_GREEN if has_resources else COLOR_DARK_GRAY

            # Surligner si c'est le mode de construction actuel
            if self.build_mode == building_key:
                button_color = COLOR_LIGHT_BLUE

            # Dessiner le bouton
            button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, COLOR_WHITE, button_rect, 2)

            # Nom du bâtiment
            name_text = self.font_small.render(f"{index + 1}. {building_info['name']}", True, COLOR_WHITE)
            screen.blit(name_text, (button_x + 5, start_y + 5))

            # Coût
            cost_y = start_y + 25
            for resource_name, cost_amount in building_info['cost'].items():
                cost_text = self.font_small.render(f"{resource_name}: {cost_amount}", True, COLOR_WHITE)
                screen.blit(cost_text, (button_x + 5, cost_y))
                cost_y += 18

    def draw_game_time(self, screen, elapsed_time):
        """
        Affiche le temps de jeu, le nombre de jours et la phase (Matin/Soir/Nuit)
        Args:
            screen: Surface Pygame
            elapsed_time: Temps écoulé en secondes
        """
        current_day = int(elapsed_time // SECONDS_PER_DAY) + 1

        # Calculer la phase du jour
        day_progress = (elapsed_time % SECONDS_PER_DAY) / SECONDS_PER_DAY
        if day_progress < DAY_PHASE_DURATION * 0.5:
            phase = "Matin"
        elif day_progress < DAY_PHASE_DURATION:
            phase = "Après-midi"
        else:
            phase = "Nuit"

        time_text = self.font_normal.render(f"Jour {current_day}/{SURVIVAL_DAYS_TO_WIN} - {phase}", True, COLOR_WHITE)

        # Afficher en haut au centre
        text_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 20))

        # Fond
        background_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
        background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
        background_surface.fill((0, 0, 0, 180))
        screen.blit(background_surface, background_rect.topleft)

        screen.blit(time_text, text_rect)

    def draw_controls_help(self, screen):
        """
        Affiche l'aide des contrôles (en bas à gauche)
        Args:
            screen: Surface Pygame
        """
        help_x = 10
        help_y = SCREEN_HEIGHT - 250

        # Fond
        help_background = pygame.Surface((250, 100), pygame.SRCALPHA)
        help_background.fill((0, 0, 0, 150))
        screen.blit(help_background, (help_x, help_y))

        # Texte d'aide
        controls = [
            "ZQSD/Flèches: Déplacer",
            "Clic: Récolter/Construire",
            "1-8: Bâtiments | C: Craft",
            "E: Manger | F5: Save",
            "F9: Load | ESC: Quitter"
        ]

        for index, control_text in enumerate(controls):
            text_surface = self.font_small.render(control_text, True, COLOR_WHITE)
            screen.blit(text_surface, (help_x + 10, help_y + 10 + index * 18))

    def draw_victory_screen(self, screen):
        """
        Affiche l'écran de victoire
        Args:
            screen: Surface Pygame
        """
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Texte de victoire
        victory_text = self.font_large.render("VICTOIRE !", True, COLOR_YELLOW)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(victory_text, victory_rect)

        # Sous-texte
        subtitle_text = self.font_normal.render("Vous avez construit la fusée !", True, COLOR_WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(subtitle_text, subtitle_rect)

        # Instructions
        instruction_text = self.font_small.render("Appuyez sur ESC pour quitter", True, COLOR_WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(instruction_text, instruction_rect)

    def draw_game_over_screen(self, screen):
        """
        Affiche l'écran de défaite
        Args:
            screen: Surface Pygame
        """
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Texte de défaite
        game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)

        # Sous-texte
        subtitle_text = self.font_normal.render("Vous êtes mort...", True, COLOR_WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(subtitle_text, subtitle_rect)

        # Instructions
        instruction_text = self.font_small.render("Appuyez sur ESC pour quitter", True, COLOR_WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(instruction_text, instruction_rect)

    def draw_quest_panel(self, screen, quest_manager):
        """
        Affiche le panneau des quêtes actives
        Args:
            screen: Surface Pygame
            quest_manager: Instance du QuestManager
        """
        active_quests = quest_manager.get_active_quests()
        if not active_quests:
            return

        # Position du panneau (côté droit, sous l'inventaire)
        panel_x = SCREEN_WIDTH - 350
        panel_y = 600

        # Calculer la hauteur nécessaire
        # Chaque quête prend environ 60px + 18px par objectif
        total_height = 0
        for quest in active_quests[:3]:  # Maximum 3 quêtes affichées
            total_height += 60 + len(quest.objectives) * 18 + 10

        panel_height = min(400, total_height + 40)

        # Fond semi-transparent
        background = pygame.Surface((300, panel_height), pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))
        screen.blit(background, (panel_x, panel_y))

        # Titre
        title = self.font_normal.render("Quêtes actives:", True, COLOR_YELLOW)
        screen.blit(title, (panel_x + 10, panel_y + 10))

        # Dessiner chaque quête
        y_offset = panel_y + 40
        for quest in active_quests[:3]:  # Montrer maximum 3 quêtes
            # Titre de la quête
            quest_title = self.font_small.render(quest.title, True, COLOR_WHITE)
            screen.blit(quest_title, (panel_x + 10, y_offset))
            y_offset += 20

            # Objectifs avec progression
            from quests import OBJECTIVE_TYPE_NAMES
            for i, (obj_type, target) in enumerate(quest.objectives):
                current = quest.progress[i]
                obj_name = OBJECTIVE_TYPE_NAMES.get(obj_type, obj_type)

                # Couleur selon la complétion
                if current >= target:
                    progress_color = COLOR_GREEN
                else:
                    progress_color = COLOR_LIGHT_BLUE

                progress_text = f"  {obj_name}: {current}/{target}"
                progress_surface = self.font_small.render(progress_text, True, progress_color)
                screen.blit(progress_surface, (panel_x + 15, y_offset))
                y_offset += 18

            y_offset += 10  # Espace entre les quêtes

    def draw_crafting_menu(self, screen, crafting_system, player_inventory):
        """
        Affiche le menu de crafting (overlay modal)
        Args:
            screen: Surface Pygame
            crafting_system: Instance du CraftingSystem
            player_inventory: Inventaire du joueur
        """
        # Dimensions du menu (centré)
        menu_width = 600
        menu_height = 500
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Fond du menu
        menu_background = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_background.fill((0, 0, 0, 220))
        screen.blit(menu_background, (menu_x, menu_y))

        # Titre
        title = self.font_large.render("CRAFTING", True, COLOR_YELLOW)
        screen.blit(title, (menu_x + 20, menu_y + 20))

        # Instructions
        instructions = self.font_small.render("Cliquez sur une recette pour crafter  |  Appuyez sur C pour fermer", True, COLOR_WHITE)
        screen.blit(instructions, (menu_x + 20, menu_y + 60))

        # Liste des recettes
        recipes = crafting_system.get_all_recipes()
        y_offset = menu_y + 100

        for recipe in recipes:
            can_craft = crafting_system.can_craft(recipe.recipe_id, player_inventory)

            # Couleur de fond selon craftabilité
            box_color = (0, 100, 0, 100) if can_craft else (100, 0, 0, 100)

            # Boîte de recette
            box_height = 80
            recipe_box = pygame.Surface((menu_width - 40, box_height), pygame.SRCALPHA)
            recipe_box.fill(box_color)
            screen.blit(recipe_box, (menu_x + 20, y_offset))

            # Nom de la recette
            name_text = self.font_normal.render(recipe.name, True, COLOR_WHITE)
            screen.blit(name_text, (menu_x + 30, y_offset + 10))

            # Ingrédients
            ingredients_list = []
            for resource, amount in recipe.ingredients.items():
                ingredients_list.append(f"{amount} {resource}")
            ingredients_text = " + ".join(ingredients_list)

            ingr_surface = self.font_small.render(f"Nécessite: {ingredients_text}", True, COLOR_LIGHT_BLUE)
            screen.blit(ingr_surface, (menu_x + 30, y_offset + 35))

            # Résultat
            output_list = []
            for resource, amount in recipe.output.items():
                output_list.append(f"{amount} {resource}")
            output_text = " + ".join(output_list)

            out_surface = self.font_small.render(f"Produit: {output_text}", True, COLOR_GREEN)
            screen.blit(out_surface, (menu_x + 30, y_offset + 55))

            y_offset += box_height + 10

            # Arrêter si on dépasse la hauteur du menu
            if y_offset > menu_y + menu_height - 100:
                break
