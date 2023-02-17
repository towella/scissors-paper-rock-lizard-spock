# - libraries -
import pygame
import random
# - general -
from game_data import fonts, start_num
from support import *
# - tiles -
from tiles import CollideableTile
# - systems -
from text import Font


class Level:
    def __init__(self, screen_surface, screen_rect, type_numbers):
        #self.dev_debug = False

        # level setup
        self.screen_surface = screen_surface  # main screen surface
        self.screen_rect = screen_rect
        self.screen_width = screen_surface.get_width()
        self.screen_height = screen_surface.get_height()

        self.type_numbers = type_numbers
        self.entities = self.create_tile_group()
        self.won = None

        self.pause = False
        self.pause_pressed = False

        # text setup
        self.small_font = Font(fonts['small_font'], 'white')
        self.large_font = Font(fonts['large_font'], 'white')
        self.number_font = Font(fonts['number_font'], 'white', True)

        # images
        self.bg_img = pygame.image.load(resource_path('../assets/background.png'))
        scale = 5
        self.start_up_numbers = [
            pygame.transform.scale(self.large_font.get_surf('3', 'black'), (9 * scale, 18 * scale)).convert(24),
            pygame.transform.scale(self.large_font.get_surf('2', 'black'), (9 * scale, 18 * scale)).convert(24),
            pygame.transform.scale(self.large_font.get_surf('1', 'black'), (9 * scale, 18 * scale)).convert(24)]

        self.level_timer = 0
        self.start_sequence_max = 60

# -- set up room methods --

    # creates all the neccessary types of tiles seperately and places them in individual layer groups
    def create_tile_group(self):
        sprite_group = pygame.sprite.Group()
        path = '../assets/'
        surfaces = {'spock': pygame.image.load(resource_path(path + 'spock.png')),
                    'lizard': pygame.image.load(resource_path(path + 'lizard.png')),
                    'scissors': pygame.image.load(resource_path(path + 'scissors.png')),
                    'paper': pygame.image.load(resource_path(path + 'paper.png')),
                    'rock': pygame.image.load(resource_path(path + 'rock.png'))}

        # gets layer from tmx and creates StaticTile for every tile in the layer, putting them in both SpriteGroups
        for obj_type in self.type_numbers:
            for i in range(self.type_numbers[obj_type]):
                x = random.randint(0, self.screen_width - tile_size)
                y = random.randint(0, self.screen_height)

                # ensures no entities spawn on top of each other
                loop = True
                while loop:
                    loop = False
                    for tile in sprite_group:
                        if tile.hitbox.collidepoint((x, y)):
                            x = random.randint(0, self.screen_width - tile_size)
                            y = random.randint(0, self.screen_height)
                            loop = True
                            break

                tile = CollideableTile((x, y), tile_size, surfaces, self.screen_surface, obj_type)
                sprite_group.add(tile)
        return sprite_group

    def start_up_sequence(self):
        time_offset = 0

        if self.level_timer == 1:
            for surf in self.start_up_numbers:
                surf.set_alpha(0)

        # switch out number surface and time_offset
        if self.level_timer <= self.start_sequence_max // 3:
            surf = self.start_up_numbers[0]
            time_offset = 0
        elif self.level_timer <= self.start_sequence_max // 3 * 2:
            surf = self.start_up_numbers[1]
            time_offset = self.start_sequence_max // 3
        else:
            surf = self.start_up_numbers[2]
            time_offset = self.start_sequence_max // 3 * 2

        # determine when to fade in and fade out
        if self.level_timer - time_offset < self.start_sequence_max//3 // 1.7:
            surf.set_alpha(surf.get_alpha() + 23)
        else:
            surf.set_alpha(surf.get_alpha() - 20)

        # amplitude * sin(time * speed)
        y = (self.screen_height - 50) * math.sin((self.level_timer - time_offset) * 0.025) + 20

        return [surf, y]

# -- check methods --

    def get_input(self):
        keys = pygame.key.get_pressed()

        # pause pressed prevents holding key and rapidly switching between T and F
        if keys[pygame.K_p] or keys[pygame.K_SPACE]:
            if not self.pause_pressed:
                self.pause = not self.pause
            self.pause_pressed = True
        # if not pressed
        else:
            self.pause_pressed = False

        '''# TODO testing, remove
        if keys[pygame.K_z] and keys[pygame.K_LSHIFT]:
            self.dev_debug = False
        elif keys[pygame.K_z]:
            self.dev_debug = True'''

    def get_won(self):
        return self.won

# -- visual --

    # draw tiles in tile group but only if in camera view (in tile.draw method)
    def draw_tile_group(self, group):
        for tile in group:
            # render tile
            tile.draw()

            # TODO testing, remove
            '''if self.dev_debug:
                pygame.draw.rect(self.screen_surface, 'red', tile.hitbox, 1)'''

# -- menus --

    def pause_menu(self):
        pause_surf = pygame.Surface((self.screen_surface.get_width(), self.screen_surface.get_height()))
        pause_surf.fill((40, 40, 40))
        self.screen_surface.blit(pause_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        width = self.large_font.width('PAUSED')
        self.large_font.render('PAUSED', self.screen_surface, (center_object_x_surf(width, self.screen_surface), 20), 'black')

# -------------------------------------------------------------------------------- #

    # updates the level allowing tile scroll and displaying tiles to screen
    # order is equivalent of layers
    def update(self):
        # #### INPUT > GAME(checks THEN UPDATE) > RENDER ####

        # -- INPUT --
        self.get_input()

        # -- CHECKS (For the previous frame)  --
        if not self.pause:
            if self.level_timer >= self.start_sequence_max:
            # -- UPDATES -- player needs to be before tiles for scroll to function properly
                self.entities.update(self.entities)

            self.level_timer += 1

            # CHECK IF GAME OVER
            types = {'scissors': 0, 'paper': 0, 'rock': 0, 'lizard': 0, 'spock': 0}
            for obj in self.entities:
                types[obj.type] += 1

            for type in types:
                if types[type] == start_num * 5:
                    self.won = type
                    break

        # -- RENDER --
        # Draw
        self.screen_surface.blit(self.bg_img, (0, 0))
        if self.level_timer <= self.start_sequence_max:
            num = self.start_up_sequence()
            self.screen_surface.blit(num[0], (center_object_x_surf(num[0].get_width(), self.screen_surface), num[1]))
        else:
            self.draw_tile_group(self.entities)

        # must be after other renders to ensure menu is drawn last
        if self.pause:
            self.pause_menu()

        # Dev Tools
        '''if self.dev_debug:
            # put debug tools here
            pass'''
