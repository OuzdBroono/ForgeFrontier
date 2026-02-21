"""
ANIMATIONS.PY
=============
Système d'animations simples basé sur des frames.
Permet d'animer les sprites avec plusieurs frames.
"""

import pygame


class Animation:
    """Animation simple basée sur des frames"""

    def __init__(self, frames, frame_duration=0.1, loop=True):
        """
        Initialise une animation
        Args:
            frames: Liste de pygame.Surface (frames de l'animation)
            frame_duration: Durée d'une frame en secondes
            loop: Si True, l'animation boucle, sinon s'arrête à la dernière frame
        """
        self.frames = frames if frames else []
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.frame_timer = 0
        self.playing = True
        self.finished = False

    def update(self, delta_time):
        """
        Met à jour l'animation
        Args:
            delta_time: Temps écoulé depuis dernière frame
        """
        if not self.playing or len(self.frames) <= 1 or self.finished:
            return

        self.frame_timer += delta_time

        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    self.playing = False

    def get_current_frame(self):
        """Retourne la frame actuelle"""
        if self.frames and 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None

    def reset(self):
        """Remet l'animation au début"""
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False
        self.playing = True

    def play(self):
        """Démarre l'animation"""
        self.playing = True

    def pause(self):
        """Met l'animation en pause"""
        self.playing = False


class AnimatedSprite:
    """Sprite avec plusieurs animations (idle, walk, attack, etc.)"""

    def __init__(self):
        """Initialise un sprite animé"""
        self.animations = {}  # {'idle': Animation, 'walk': Animation, ...}
        self.current_animation = None
        self.default_animation = None

    def add_animation(self, name, animation, is_default=False):
        """
        Ajoute une animation nommée
        Args:
            name: Nom de l'animation (ex: 'idle', 'walk')
            animation: Instance d'Animation
            is_default: Si True, utilise cette animation par défaut
        """
        self.animations[name] = animation
        if is_default or self.default_animation is None:
            self.default_animation = name
            if self.current_animation is None:
                self.current_animation = name

    def play_animation(self, name, force_restart=False):
        """
        Joue une animation spécifique
        Args:
            name: Nom de l'animation
            force_restart: Si True, redémarre l'animation même si déjà en cours
        """
        if name in self.animations:
            if self.current_animation != name or force_restart:
                self.current_animation = name
                self.animations[name].reset()

    def update(self, delta_time):
        """Met à jour l'animation actuelle"""
        if self.current_animation and self.current_animation in self.animations:
            self.animations[self.current_animation].update(delta_time)

    def get_current_frame(self):
        """Retourne la frame actuelle à dessiner"""
        if self.current_animation and self.current_animation in self.animations:
            return self.animations[self.current_animation].get_current_frame()
        return None

    def reset_to_default(self):
        """Retourne à l'animation par défaut"""
        if self.default_animation:
            self.play_animation(self.default_animation)
