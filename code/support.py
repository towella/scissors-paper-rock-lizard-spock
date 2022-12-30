import pygame, os, sys, math
from csv import reader
from game_data import tile_size


# -- import functions --

# allows paths to be used for both normal running in PyCharm and as an .exe
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        relative_path = relative_path[3:]  # slices path if using executable to absolute path. Otherwise use relative for PyCharm
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# https://riptutorial.com/pygame/example/23788/transparency    info on alpha values in surfaces (opacity and clear pixels)

def import_sound(path):
    path = resource_path(path)
    return pygame.mixer.Sound(path)


# returns list of subfolder name strings at a path
def get_subfolders(path):
    path = resource_path(path)
    for folder_name, sub_folders, img_files in os.walk(path):
        return sub_folders

# imports all the images in a single folder. Returns a list of (image_name, image_surface) tuples
def import_folder(path):
    path = resource_path(path)
    surface_dict = {}
    allowed_file_types = ['.png', '.jpg', '.jpeg', '.gif']

    for folder_name, sub_folders, img_files in os.walk(path):
        img_files.sort()
        for image in img_files:
            for type in allowed_file_types:
                if type in image.lower():  # prevents invisible non image files causing error while allowing image type to be flexible (e.g. .DS_Store)
                    full_path = path + '/' + image  # accesses image from directory by creating path name
                    image_surface = pygame.image.load(full_path).convert_alpha()  # adds image to surface (convert alpha is best practice)

                    # strips file type from name and uses as key to image surface in dict for easy accessing
                    for i, char in enumerate(image):
                        if char == '.':
                            image = image[:i]
                    surface_dict[image] = image_surface
                    break  # breaks from checking allowed file types
        return surface_dict


# imports level csvs and returns workable list of lists
def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


# returns a cropped portion of an input surface
def clip(surf, x, y, x_size, y_size):
    clipR = pygame.Rect(x, y, x_size, y_size)  # rectangle area to be clipped
    image = surf.subsurface(clipR)  # creates new surface of pixels within passed rect in subject surf
    return image.copy()


# cuts up tile sheets returning list of tile images
# tiles must have no spacing and consistent dimensions. Art px = game px
def import_tileset(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / tile_size)  # works out how many tiles are on the x and y based on passed value
    tile_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    # keeps track of different segments of tilesheet
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            # x and y refer to x and y tile grid on the imported tileset not the game (top left of tile being sliced)
            x = col * tile_size
            y = row * tile_size
            # makes new surface and places segment of sheet (tile) on new surface
            new_surface = clip(surface, x, y, tile_size, tile_size)
            cut_tiles.append(new_surface)

    return cut_tiles


# -- procedural pixel art --

# black will not work due to masking
def swap_colour(img, old_c, new_c):
    img.set_colorkey(old_c)

    # creates block bg with size of imagee
    surf = img.copy()
    surf.fill(new_c)

    # original image with colourkey onto background
    surf.blit(img, (0, 0))
    surf.set_colorkey((0, 0, 0))
    return surf


# TODO issue with masking out black sections of image
# black will not work due to masking
def outline_image(image, colour='white'):
    # black will not work so change to almost black
    if colour == 'black' or colour == (0, 0, 0):
        colour = (1, 0, 0)

    # make surf for application
    surf = pygame.Surface((image.get_width() + 2, image.get_height() + 2))
    surf.set_colorkey((0, 0, 0))

    # create mask from image (necessary for white outlines)
    mask = pygame.mask.from_surface(image)
    mask_surf = mask.to_surface()
    mask_surf.set_colorkey((0, 0, 0))

    # create outline area
    surf.blit(mask_surf, (0, 1))
    surf.blit(mask_surf, (1, 0))
    surf.blit(mask_surf, (1, 2))
    surf.blit(mask_surf, (2, 1))

    if colour != 'white' and colour != (255, 255, 255):
        surf = swap_colour(surf, 'white', colour)

    # layer original image over outline
    surf.blit(image, (1, 1))
    return surf


def circle_surf(radius, colour):
    radius = int(radius)
    surf = pygame.Surface((radius*2, radius*2))
    pygame.draw.circle(surf, colour, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


# -- physics --
# TODO should be a class??
def raycast(angle, pos, max_distance, tiles):
    angle = angle * math.pi / 180  # angle of the raycast in RADIANS
    x = 0
    y = 0
    max_distance = round(max_distance)
    # stepping by 2 introduces margin of error +-2px but also reduces load on checks
    for hyp in range(0, max_distance, 2):
        # we know theta (dir) and we're trying to find the x and y values for the given point on the ray.
        x = math.cos(angle) * hyp  # cos returns ratio from radians
        y = -(math.sin(angle) * hyp)  # sin returns ratio from radians. Y must be negative because pygame axis is flipped
        for tile in tiles:
            if tile.hitbox.collidepoint((pos[0] + x, pos[1] + y)):
                return (pos[0] + x, pos[1] + y)  # returns collision point

    return (pos[0] + x, pos[1] + y)  # returns maximum coordinate value for ray


# -- utilities --

def get_rect_corners(rect):
    return [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]


# returns angle of point from pos in DEGREES
def get_angle(pos, point):
    angle = math.atan2(point[1] - pos[1], point[0] - pos[0])
    angle *= 180 / math.pi  # converts to degrees

    # makes the angle produced by tan in any qudarant relative to 0 DEG and positive.
    if angle < 0:
        angle = 180 + angle
    if pos[1] - point[1] < 0:
        angle += 180

    return angle


def get_distance(pos, point):
    x = point[0] - pos[0]
    y = point[1] - pos[1]
    return abs(math.hypot(x, y))


# crops a surface out of a larger surface (usefull for images)
def crop(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


# centers an object with a given width on the x axis on a given surface
def center_object_x_surf(width_obj, surf):
    x = surf.get_width()//2 - width_obj//2
    return x


def center_object_x_rect(width_obj, rect):
    width = rect.right - rect.left
    return width//2 + rect.left - width_obj//2


# converts a position refering to topleft to be applicable to surface's center
def pos_for_center(surf, pos):
    x = int(surf.get_width() / 2)
    y = int(surf.get_height() / 2)
    return [pos[0] - x, pos[1] - y]


def scale_hitbox(hitbox_image, scaleup):
    hitbox_width = hitbox_image.get_width()
    hitbox_height = hitbox_image.get_height()
    return pygame.transform.scale(hitbox_image, (hitbox_width * scaleup, hitbox_height * scaleup))