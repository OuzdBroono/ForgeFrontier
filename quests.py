"""
QUESTS.PY
=========
Ce fichier gère le système de quêtes du jeu.
Les quêtes ont des objectifs à atteindre et donnent des récompenses à leur complétion.
"""

from constants import *


class Quest:
    """Représente une quête individuelle avec objectifs et récompenses"""

    def __init__(self, quest_id, title, description, objectives, rewards):
        """
        Initialise une quête
        Args:
            quest_id: Identifiant unique de la quête
            title: Titre de la quête
            description: Description de la quête
            objectives: Liste de tuples (type_objectif, valeur_cible)
                       ex: ('collect_metal', 50), ('build_mine', 2)
            rewards: Dictionnaire des ressources données en récompense
        """
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives  # [(type, target), ...]
        self.progress = [0] * len(objectives)  # Progression pour chaque objectif
        self.rewards = rewards
        self.is_completed = False
        self.is_active = False

    def check_completion(self):
        """Vérifie si tous les objectifs sont atteints"""
        for i, (obj_type, target) in enumerate(self.objectives):
            if self.progress[i] < target:
                return False
        return True

    def update_progress(self, objective_type, value):
        """
        Met à jour la progression pour un type d'objectif spécifique
        Args:
            objective_type: Type d'objectif (ex: 'collect_metal')
            value: Nouvelle valeur de progression
        """
        for i, (obj_type, target) in enumerate(self.objectives):
            if obj_type == objective_type:
                self.progress[i] = min(value, target)

    def get_progress_text(self):
        """Retourne le texte de progression lisible"""
        lines = []
        for i, (obj_type, target) in enumerate(self.objectives):
            current = self.progress[i]
            obj_name = OBJECTIVE_TYPE_NAMES.get(obj_type, obj_type)
            lines.append(f"  {obj_name}: {current}/{target}")
        return "\n".join(lines)


class QuestManager:
    """Gère toutes les quêtes du jeu"""

    def __init__(self):
        """Initialise le gestionnaire de quêtes"""
        self.quests = {}  # quest_id -> Quest
        self.active_quests = []  # Liste des IDs de quêtes actives
        self.completed_quests = []  # Liste des IDs de quêtes complétées
        self._initialize_quests()

    def _initialize_quests(self):
        """Crée toutes les quêtes disponibles"""
        # Quête tutoriel 1 : Récolte de base
        self.quests['tutorial_1'] = Quest(
            'tutorial_1',
            "Premiers Pas",
            "Récoltez des ressources de base pour survivre",
            [('collect_metal', 20), ('collect_food', 10)],
            {RESOURCE_ENERGY: 5}
        )

        # Quête tutoriel 2 : Construction de base
        self.quests['tutorial_2'] = Quest(
            'tutorial_2',
            "Établir une Base",
            "Construisez vos premières installations de production",
            [('build_mine', 1), ('build_farm', 1)],
            {RESOURCE_METAL: 10, RESOURCE_WOOD: 5}
        )

        # Quête de défense
        self.quests['defense_1'] = Quest(
            'defense_1',
            "Mesures Défensives",
            "Protégez votre base contre les ennemis",
            [('kill_enemies', 5), ('build_turret', 1)],
            {RESOURCE_ENERGY: 10}
        )

        # Quête de survie
        self.quests['survival_1'] = Quest(
            'survival_1',
            "Test d'Endurance",
            "Survivez aux premiers jours",
            [('survive_days', 3)],
            {RESOURCE_FOOD: 20, RESOURCE_METAL: 15}
        )

        # Quête d'expansion
        self.quests['expansion_1'] = Quest(
            'expansion_1',
            "Croissance Industrielle",
            "Développez votre capacité de production",
            [('build_mine', 3), ('build_farm', 2), ('build_generator', 2)],
            {RESOURCE_STONE: 10, RESOURCE_ENERGY: 20}
        )

        # Quête principale : victoire
        self.quests['main_victory'] = Quest(
            'main_victory',
            "Plan d'Évasion",
            "Construisez la fusée pour vous échapper",
            [('build_rocket', 1)],
            {}  # La victoire est la récompense
        )

        # Activer automatiquement la première quête tutoriel
        self.activate_quest('tutorial_1')

    def activate_quest(self, quest_id):
        """
        Active une quête
        Args:
            quest_id: ID de la quête à activer
        """
        if quest_id in self.quests and quest_id not in self.active_quests:
            self.quests[quest_id].is_active = True
            self.active_quests.append(quest_id)

    def update_all_progress(self, stats):
        """
        Met à jour toutes les quêtes actives selon les statistiques de jeu
        Args:
            stats: Dictionnaire contenant les statistiques du jeu
                   ex: {'metal_collected': 50, 'mines_built': 2, ...}
        """
        for quest_id in self.active_quests:
            quest = self.quests[quest_id]

            # Mettre à jour chaque objectif selon les stats
            for obj_type, target in quest.objectives:
                stat_key = self._objective_to_stat_key(obj_type)
                if stat_key in stats:
                    quest.update_progress(obj_type, stats[stat_key])

    def complete_quest(self, quest_id):
        """
        Marque une quête comme complétée et donne les récompenses
        Args:
            quest_id: ID de la quête à compléter
        Returns:
            dict: Récompenses à donner au joueur
        """
        quest = self.quests[quest_id]
        quest.is_completed = True
        self.active_quests.remove(quest_id)
        self.completed_quests.append(quest_id)
        return quest.rewards

    def _objective_to_stat_key(self, objective_type):
        """
        Convertit un type d'objectif en clé de statistique
        Args:
            objective_type: Type d'objectif (ex: 'collect_metal')
        Returns:
            str: Clé correspondante dans le dictionnaire de stats
        """
        mapping = {
            'collect_metal': 'metal_collected',
            'collect_food': 'food_collected',
            'collect_wood': 'wood_collected',
            'collect_stone': 'stone_collected',
            'build_mine': 'mines_built',
            'build_farm': 'farms_built',
            'build_generator': 'generators_built',
            'build_turret': 'turrets_built',
            'build_rocket': 'rockets_built',
            'build_hospital': 'hospitals_built',
            'build_laboratory': 'laboratories_built',
            'kill_enemies': 'enemies_killed',
            'survive_days': 'days_survived'
        }
        return mapping.get(objective_type, objective_type)

    def get_active_quests(self):
        """Retourne la liste des quêtes actives"""
        return [self.quests[qid] for qid in self.active_quests]


# Noms d'affichage pour les objectifs
OBJECTIVE_TYPE_NAMES = {
    'collect_metal': 'Récolter du métal',
    'collect_food': 'Récolter de la nourriture',
    'collect_wood': 'Récolter du bois',
    'collect_stone': 'Récolter de la pierre',
    'build_mine': 'Construire des mines',
    'build_farm': 'Construire des fermes',
    'build_generator': 'Construire des générateurs',
    'build_turret': 'Construire des tourelles',
    'build_rocket': 'Construire la fusée',
    'build_hospital': 'Construire des hôpitaux',
    'build_laboratory': 'Construire des laboratoires',
    'kill_enemies': 'Tuer des ennemis',
    'survive_days': 'Survivre X jours'
}
