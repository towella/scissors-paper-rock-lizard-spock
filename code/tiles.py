import pygame
from support import import_folder
import random


# base tile class with block fill image
class StaticTile(pygame.sprite.Sprite):
    def __init__(self, pos, size, screen):
        super().__init__()
        self.image = pygame.Surface((size, size))  # creates square tile
        self.image.fill('grey')  # makes tile grey
        self.rect = self.image.get_rect(topleft=pos)  # postions the rect and image
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

    def draw(self):
        self.screen.blit(self.image, self.rect)


# terrain tile type, inherits from main tile and can be assigned an image
class CollideableTile(StaticTile):
    def __init__(self, pos, size, surfaces, screen, type):
        super().__init__(pos, size, screen)  # passing in variables to parent class

        self.GAME_RULES = {('scissors', 'paper'): 'scissors',
                           ('paper', 'rock'): 'paper',
                           ('rock', 'scissors'): 'rock'}

        self.type = type
        self.surfaces = surfaces
        self.image = self.surfaces[self.type]
        self.hitbox = self.image.get_rect()
        self.hitbox.topleft = pos
        self.move_speed = 1
        self.randdir_timer_max = 20
        self.randdir_timer = self.randdir_timer_max
        self.velocity = [0, 0]

    def check_collision(self, entities):
        # check collision with other entities
        for obj in entities:
            if self.hitbox.colliderect(obj.hitbox) and self.type != obj.type:
                for rule in self.GAME_RULES:
                    if self.type in rule and obj.type in rule and self.type != self.GAME_RULES[rule]:
                        self.type = self.GAME_RULES[rule]
                        break

    def update_image(self):
        self.image = self.surfaces[self.type]

    def update(self, entities):
        self.check_collision(entities)
        self.update_image()

        if self.randdir_timer == self.randdir_timer_max:
            choices = [-self.move_speed, self.move_speed]
            self.velocity[0] = random.choice(choices)
            self.velocity[1] = random.choice(choices)
            self.randdir_timer = 0

        self.hitbox.x += self.velocity[0]
        self.hitbox.y += self.velocity[1]

        if self.hitbox.left < 0:
            self.hitbox.left = 0
        elif self.hitbox.right > self.screen_width:
            self.hitbox.right = self.screen_width

        if self.hitbox.top < 0:
            self.hitbox.top = 0
        elif self.hitbox.bottom > self.screen_height:
            self.hitbox.bottom = self.screen_height

        self.rect.topleft = self.hitbox.topleft

        self.randdir_timer += 1



class HazardTile(CollideableTile):
    def __init__(self, pos, size, surface, player):
        super().__init__(pos, size, surface)
        self.player = player

    def update(self, scroll_value):
        if self.hitbox.colliderect(self.player.hitbox):
            self.player.invoke_respawn()
        self.apply_scroll(scroll_value)

# animated tile that can be assigned images from a folder to animate
class AnimatedTile(StaticTile):
    def __init__(self, pos, size, path):
        super().__init__(pos, size)
        self.frames = import_folder(path, 'list')
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, scroll_value):
        self.animate()
        self.apply_scroll(scroll_value)


'''class NPC(Tile):
    def __init__(self, pos, size, path):
        super().__init__(pos, size)
        self.text_box
'''

'''class Crate(StaticTile):
    def __init__(self, pos, size, surface, all_tiles):
        super().__init__(pos, size, surface)
        # TODO implement crate specific hitbox
        self.all_tiles = all_tiles

    def collide(self, sprite):
        collision_tolerance = 20

        if sprite.hitbox.colliderect(self.hitbox):
            # abs ensures only the desired side registers collision
            # not having collisions dependant on status allows hitboxes to change size
            if abs(sprite.hitbox.right - self.hitbox.left) < collision_tolerance: #and 'left' in self.status_facing:
                self.hitbox.left = sprite.hitbox.right
            elif abs(sprite.hitbox.left - self.hitbox.right) < collision_tolerance: #and 'right' in self.status_facing:
                self.hitbox.right = sprite.hitbox.left
        # resyncs up rect to the hitbox
        self.rect.midtop = self.hitbox.midtop'''