"""
CRAFTING.PY
===========
Ce fichier gère le système de crafting du jeu.
Permet de combiner des ressources pour créer de nouveaux items.
"""

from constants import *


class CraftingRecipe:
    """Représente une recette de crafting"""

    def __init__(self, recipe_id, name, ingredients, output, craft_time=0):
        """
        Initialise une recette
        Args:
            recipe_id: Identifiant unique
            name: Nom de la recette
            ingredients: Dict des ressources nécessaires {resource: amount}
            output: Dict des ressources produites {resource: amount}
            craft_time: Temps de fabrication en secondes (0 = instantané)
        """
        self.recipe_id = recipe_id
        self.name = name
        self.ingredients = ingredients
        self.output = output
        self.craft_time = craft_time


class CraftingSystem:
    """Gère toutes les recettes de crafting"""

    def __init__(self):
        """Initialise le système de crafting"""
        self.recipes = {}
        self._initialize_recipes()

    def _initialize_recipes(self):
        """Définit toutes les recettes disponibles"""
        # Outils (métal + bois)
        self.recipes['tools'] = CraftingRecipe(
            'tools',
            "Outils",
            {RESOURCE_METAL: 5, RESOURCE_WOOD: 3},
            {'tools': 1},
            craft_time=2.0
        )

        # Composants (métal + pierre)
        self.recipes['components'] = CraftingRecipe(
            'components',
            "Composants",
            {RESOURCE_METAL: 3, RESOURCE_STONE: 2},
            {'components': 1},
            craft_time=3.0
        )

        # Médecine (nourriture + composants)
        self.recipes['medicine'] = CraftingRecipe(
            'medicine',
            "Médecine",
            {RESOURCE_FOOD: 5, 'components': 1},
            {'medicine': 1},
            craft_time=4.0
        )

        # Matériaux avancés (métal + pierre + composants)
        self.recipes['advanced_materials'] = CraftingRecipe(
            'advanced_materials',
            "Matériaux Avancés",
            {RESOURCE_METAL: 10, RESOURCE_STONE: 10, 'components': 2},
            {'advanced_materials': 1},
            craft_time=5.0
        )

        # Conversions de ressources
        # Fondre de la pierre en métal
        self.recipes['metal_from_stone'] = CraftingRecipe(
            'metal_from_stone',
            "Fondre du Métal",
            {RESOURCE_STONE: 5, RESOURCE_ENERGY: 2},
            {RESOURCE_METAL: 3},
            craft_time=3.0
        )

        # Brûler du bois pour énergie
        self.recipes['energy_from_wood'] = CraftingRecipe(
            'energy_from_wood',
            "Brûler du Bois",
            {RESOURCE_WOOD: 3},
            {RESOURCE_ENERGY: 2},
            craft_time=1.0
        )

    def can_craft(self, recipe_id, inventory):
        """
        Vérifie si une recette peut être craftée
        Args:
            recipe_id: ID de la recette
            inventory: Inventaire du joueur
        Returns:
            bool: True si craftable
        """
        if recipe_id not in self.recipes:
            return False

        recipe = self.recipes[recipe_id]
        for resource, amount_needed in recipe.ingredients.items():
            if inventory.get(resource, 0) < amount_needed:
                return False
        return True

    def craft(self, recipe_id, inventory):
        """
        Effectue le craft (instantané)
        Args:
            recipe_id: ID de la recette
            inventory: Inventaire du joueur (modifié en place)
        Returns:
            bool: True si craft réussi
        """
        if not self.can_craft(recipe_id, inventory):
            return False

        recipe = self.recipes[recipe_id]

        # Consommer les ingrédients
        for resource, amount in recipe.ingredients.items():
            inventory[resource] -= amount

        # Ajouter les produits
        for resource, amount in recipe.output.items():
            inventory[resource] = inventory.get(resource, 0) + amount

        return True

    def get_all_recipes(self):
        """Retourne toutes les recettes"""
        return list(self.recipes.values())

    def get_craftable_recipes(self, inventory):
        """Retourne les recettes craftables actuellement"""
        return [r for r in self.recipes.values() if self.can_craft(r.recipe_id, inventory)]


class CraftingQueue:
    """Gère la file d'attente de crafting (pour crafts temporisés)"""

    def __init__(self):
        """Initialise la queue"""
        self.queue = []  # [(recipe_id, time_remaining), ...]

    def add_to_queue(self, recipe_id, craft_time):
        """Ajoute une recette à la queue"""
        self.queue.append({'recipe_id': recipe_id, 'time_remaining': craft_time})

    def update(self, delta_time, inventory, crafting_system):
        """
        Met à jour les timers de craft
        Args:
            delta_time: Temps écoulé
            inventory: Inventaire du joueur
            crafting_system: Système de crafting
        Returns:
            int: Nombre d'items complétés
        """
        completed = []

        for i, craft_job in enumerate(self.queue):
            craft_job['time_remaining'] -= delta_time

            if craft_job['time_remaining'] <= 0:
                # Craft terminé
                recipe = crafting_system.recipes[craft_job['recipe_id']]
                for resource, amount in recipe.output.items():
                    inventory[resource] = inventory.get(resource, 0) + amount
                completed.append(i)

        # Retirer les crafts complétés (en ordre inverse pour éviter problèmes d'index)
        for i in reversed(completed):
            self.queue.pop(i)

        return len(completed)
