import pygame
import random
import bisect

pygame.font.init()

# Global Variables
scene_width = 800
scene_height = 800
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (scene_width - play_width) // 2
top_left_y = scene_height - play_height - 50

temp = False
# Pieces represented as nested string lists
# 0's represent an occupied block and is a vacant space
# Pieces follow tetris naming convention
# Lists are used to represent the different rotations
piece_S = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

piece_Z = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

piece_I = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

piece_O = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

piece_J = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

piece_L = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

piece_T = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

# Organizes the shapes to match its designated color
# Shapes 0-6
shapes = [piece_S, piece_Z, piece_I, piece_O, piece_J, piece_L, piece_T]
shape_colors = [(7, 225, 27), (255, 50, 19), (10, 233, 245),
                (255, 213, 0), (9, 68, 230), (255, 151, 28), (204, 37, 207)]


# Piece includes the location (coordinates), shape, color, and rotation
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# Initialize the grid
# Return the updated grid with proper values for the occupancy and colors
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    # Create a row in each of the columns

    # Used to draw the grid, determine the occupancy and color
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid


# Manages the rotation of the pieces
def convert_shape_format(shape):
    positions = []
    formatshape = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(formatshape):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


# Determine whether a space is already occupied, disables invalid moves
    # and detects collisions
def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i]
                     [j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos and pos[1] > -1:
            return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


# Returns a random piece
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# Helper function to get the text in the correct location
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2),
                         top_left_y + play_height/2 - label.get_height()/2))


# Draws the grid used for the game
def draw_grid(surface, grid):
    # Determines the starting coordinates to draw the game
    sx = top_left_x
    sy = top_left_y

    # The lines for the grid
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy +
                                                    i*block_size), (sx+play_width, sy + i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j *
                                                        block_size, sy), (sx + j*block_size, sy + play_height))


# If a row is full, this removes the blocks and moves the above values down
def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


# Display for the next shape indicator
def draw_next_shape(shape, surface):
    # Text for the indicator
    font = pygame.font.SysFont('arial', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    # Location of the next shape graphic
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    formatshape = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(formatshape):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size,
                                                        sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


# Write the end score in the text document if it is highest
def update_score(nscore):
    score = max_score()

#    f = open('scores.txt', 'w')
#    if int(score) > nscore:
#        f.write(str(score))
#    else:
#        f.write(str(nscore))


# Read the high score from the text document
def max_score():
#    f = open('scores.txt', 'r')
#    lines = f.readlines()
#    score = lines[0].strip()

    return '0'


# Displays the game window
def draw_window(surface, grid, score=0, last_score=0):
    # Create a blank canvas
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('arial', 60)
    label = font.render('CS 4701', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width /
                         2 - (label.get_width() / 2), 30))

    # Current score
    font = pygame.font.SysFont('arial', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # High score
    label = font.render('High Score: ' + last_score, 1, (255, 255, 255))

    sx = top_left_x - 240
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size,
                                                   top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 255, 255), (top_left_x,
                                                top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    # pygame.display.update()


def main(win):
    last_score = max_score()
    locked_positions = {}

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    temp = False

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005


        if fall_time/1000 > fall_speed:
            fall_time = 0
            temp = True
            #current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        #if temp:
        #    a_left = pygame.event.Event(pygame.KEYDOWN, unicode = "left",key = pygame.K_LEFT, mod=pygame.KMOD_NONE)
        #    pygame.event.post(a_left)
        #    a_rotate = pygame.event.Event(pygame.KEYDOWN, unicode = "up",key = pygame.K_UP, mod=pygame.KMOD_NONE)
        #    pygame.event.post(a_rotate)
            #current_piece.x -= 1
            #if not(valid_space(current_piece, grid)):
            #    current_piece.x += 1
        #    temp = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            # Controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                        current_piece.y -= 1
                        change_piece = True
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                # Quick Drop
                if event.key == pygame.K_SPACE:
                    while (valid_space(current_piece, grid)):
                        current_piece.y += 1
                    if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                        current_piece.y -= 1
                        change_piece = True
                if event.key == pygame.K_a:
                    moves = ai(current_piece, next_piece, grid)
                    move = moves[0]
                    current_piece.rotation = move.rotation
                    current_piece.y = move.y
                    current_piece.x = move.x
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "Game Over", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


# Main menu screen
def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


class Move (object):
    def __init__(self, x, y, shape, rotation, value):
        self.shape = shape
        self.x = x
        self.y = y
        self.rotation = rotation
        self.value = value


def heur_height(current_piece):
    shape = convert_shape_format(current_piece)
    height = sorted(shape, key=lambda x: x[1])
    max_height = height[0]
    if (max_height > 10):
        return max_height * -2
    else:
        return max_height * -5


def heur_gaps(current_piece, grid):
    gap = 0
    shape = convert_shape_format(current_piece)
    accepted_pos = [[(j, i) for j in range(10) if grid[i]
                    [j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    for (j, i) in shape:
        y = i
        while (y < 19):
            if (j, y) in accepted_pos:
                gap += 1
            y += 1
    return gap * -5


def heur_rows(current_piece, grid):
    grid_temp = grid
    shape_pos = convert_shape_format(current_piece)
    locked_positions = {}
    for pos in shape_pos:
        p = (pos[0], pos[1])
        locked_positions[p] = current_piece.color
    return clear_rows(grid_temp, locked_positions)


def ai(current_piece, next_piece, grid):
    moves = []
    rotation = len(current_piece.shape)
    while (rotation > 0):
        while (valid_space(current_piece, grid)):
            current_piece.x -= 1
        while (valid_space(current_piece, grid)):
            current_piece.x += 1
            while (valid_space(current_piece, grid)):
                current_piece.y += 1
            if not(valid_space(current_piece, grid)):
                current_piece.y -= 1
            value = heur_height(current_piece) + heur_gaps(current_piece, grid)
            + heur_rows(current_piece, grid)
            move = Move(current_piece.shape, current_piece.x, current_piece.y,
                        current_piece.rotation, value)
            move.append(move)
            moves.sort(move.value, True)
            current_piece.y = 0
        rotation -= 1
        current_piece.rotation += 1
    return moves


win = pygame.display.set_mode((scene_width, scene_height))
pygame.display.set_caption('CS 4701: Tetris')
main_menu(win)
