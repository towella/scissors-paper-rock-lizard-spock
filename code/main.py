# pyinstaller code/main.py code/camera.py code/game_data.py code/player.py code/level.py code/spawn.py code/support.py code/tiles.py code/trigger.py --onefile --noconsole


# screen resizing tut, dafluffypotato: https://www.youtube.com/watch?v=edJZOQwrMKw

import pygame, sys
from level import Level
from text import Font
from game_data import *
from support import resource_path, center_object_x_surf

# General setup
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
# tells pygame what events to check for
#setallowed
pygame.font.init()
clock = pygame.time.Clock()
game_speed = 20

# window and screen Setup ----- The window is the real pygame window. The screen is the surface that everything is
# placed on and then resized to blit on the window. Allowing larger pixels (art pixel = game pixel)
# https://stackoverflow.com/questions/54040397/pygame-rescale-pixel-size

scaling_factor = 2  # how much the screen is scaled up before bliting on display

# https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
# https://www.reddit.com/r/pygame/comments/r943bn/game_stuttering/
# vsync only works with scaled flag. Scaled flag will only work in combination with certain other flags.
# although resizeable flag is present, window can not be resized, only fullscreened with vsync still on
# vsync prevents screen tearing (multiple frames displayed at the same time creating a shuddering wave)
# screen dimensions are cast to int to prevent float values being passed (-1 is specific to this game getting screen multiple of 16)
window = pygame.display.set_mode((int(screen_width * scaling_factor) - 1, int(screen_height * scaling_factor)), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED, vsync=True)

# all pixel values in game logic should be based on the screen!!!! NO .display FUNCTIONS!!!!!
screen = pygame.Surface((screen_width, screen_height))  # the display surface, re-scaled and blit to the window
screen_rect = screen.get_rect()  # used for camera scroll boundaries

# caption and icon
pygame.display.set_caption('Scissors Paper Rock Simulation - Andrew Towell')
pygame.display.set_icon(pygame.image.load(resource_path('../icon/app_icon.png')))

# font
large_font = Font(fonts['large_font'], 'white')
font = Font(fonts['small_font'], 'black')


def main_menu():
    game()


def win_screen(winner, points):
    # imports
    path = '../assets/'
    surfaces = {'spock': pygame.image.load(resource_path(path + 'spock.png')),
                'lizard': pygame.image.load(resource_path(path + 'lizard.png')),
                'scissors': pygame.image.load(resource_path(path + 'scissors.png')),
                'paper': pygame.image.load(resource_path(path + 'paper.png')),
                'rock': pygame.image.load(resource_path(path + 'rock.png'))}
    bg = pygame.image.load(resource_path('../assets/win.png'))

    # surface
    surf = pygame.Surface(screen_rect.size)

    # draw to surface
    surf.blit(bg, (0, 0))
    title = large_font.get_surf("WINNER", True)
    scale_f = 2
    title = pygame.transform.scale(title, (title.get_width() * scale_f, title.get_height() * scale_f))
    surf.blit(title, (center_object_x_surf(title.get_width(), surf), 40))

    scale_f = 4
    icon = pygame.transform.scale(surfaces[winner], (surfaces[winner].get_width() * scale_f, surfaces[winner].get_height() * scale_f))
    surf.blit(icon, (center_object_x_surf(icon.get_width(), surf), 100))

    y = 200
    y_increment = 22
    icon_offset = 8
    icon_v_offset = 5
    icon_width = surfaces['rock'].get_width()

    text = font.get_surf(f"Scissors: {points['scissors']}")
    x = center_object_x_surf(text.get_width() + icon_width + icon_offset, surf)
    surf.blit(text, (x + icon_width + icon_offset, y))
    surf.blit(surfaces['scissors'], (x, y - icon_v_offset))

    y += y_increment
    text = font.get_surf(f"Papers: {points['paper']}")
    x = center_object_x_surf(text.get_width() + icon_width + icon_offset, surf)
    surf.blit(text, (x + icon_width + icon_offset, y))
    surf.blit(surfaces['paper'], (x, y - icon_v_offset))

    y += y_increment
    text = font.get_surf(f"Rocks: {points['rock']}")
    x = center_object_x_surf(text.get_width() + icon_width + icon_offset, surf)
    surf.blit(text, (x + icon_width + icon_offset, y))
    surf.blit(surfaces['rock'], (x, y - icon_v_offset))

    y += y_increment
    text = font.get_surf(f"Lizards: {points['lizard']}")
    x = center_object_x_surf(text.get_width() + icon_width + icon_offset, surf)
    surf.blit(text, (x + icon_width + icon_offset, y))
    surf.blit(surfaces['lizard'], (x, y - icon_v_offset))

    y += y_increment
    text = font.get_surf(f"Spocks: {points['spock']}")
    x = center_object_x_surf(text.get_width() + icon_width + icon_offset, surf)
    surf.blit(text, (x + icon_width + icon_offset, y))
    surf.blit(surfaces['spock'], (x, y - icon_v_offset))

    return surf.convert(24)


def game():
    click = False
    type_numbers = {'scissors': start_num, 'paper': start_num, 'rock': start_num, 'spock': start_num, 'lizard': start_num}
    points = {'scissors': 0, 'paper': 0, 'rock': 0, 'spock': 0, 'lizard': 0}

    # timers
    timer = 9999
    finish_max_t = 20
    win_max_t = 100
    win_alpha = 0
    reveal_win = 30

    level = Level(screen, screen_rect, type_numbers)
    end_level = False

    running = True
    while running:
        # x and y mouse pos
        mx, my = pygame.mouse.get_pos()

        # Event Checks -- Input --
        click = False
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # debug keys
                if event.key == pygame.K_SLASH:
                    pass
                elif event.key == pygame.K_PERIOD:
                    pass
                elif event.key == pygame.K_COMMA or event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                    level.pause = True
                elif event.key == pygame.K_r:
                    level = Level(screen, screen_rect, type_numbers)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        # -- Update --
        if level.get_won() is not None and not end_level:
            end_level = True
            points[level.get_won()] += 1
            timer = 0
        # if splash screen is over, reset game
        if end_level and timer > win_max_t:
            level = Level(screen, screen_rect, type_numbers)
            end_level = False
            win_alpha = 0

        screen.fill((237, 238, 192))
        level.update()  # runs level processes

        if end_level and timer > finish_max_t:
            surf = win_screen('lizard', points)
            win_alpha += reveal_win
            if win_alpha > 255:
                win_alpha = 255
            surf.set_alpha(win_alpha)
            screen.blit(surf, (0, 0))

        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))  # scale screen to window

        timer += 1

        # -- Render --
        pygame.display.update()
        clock.tick(game_speed)


main_menu()
