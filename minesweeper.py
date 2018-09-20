import pygame, random, sys
from pygame.locals import *
from collections import deque

WINDOWWIDTH = 960
WINDOWHEIGHT = 960
TEXTCOLOR = (255,69,0)
NUMBERCOLOR = (0,0,0)
BACKGROUNDCOLOR = (0,0,0)
FPS = 60
TILESIZE = 60
TILERESOLUTION = 16
MINESONMAP = 40
FLAGLIMIT = MINESONMAP


def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: #Pressing ESC quits
                    terminate()
                return

def drawText(text, font, surface, x, y,color):
    textObj = font.render(text, 1, color)
    textrect = textObj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textObj, textrect)

def makeNearTilesListAndBombs(tile,neighbours):#make list of tile neighbours, check if there is a bomb and count them
    x_tile = tile['position'][0]
    y_tile = tile['position'][1]
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x_tile + x in range(0, TILERESOLUTION) and y_tile + y in range(0, TILERESOLUTION):
                if x == 0 and y == 0:
                    continue
                tile['near_tiles'].append(neighbours[x_tile + x][y_tile + y])
                neighbour = neighbours[x_tile + x][y_tile + y]
                if neighbour['is_mined'] == True:#counting near bombs
                    tile['near_mines'] = tile['near_mines'] + 1

def discloseEmpty(tile):#show 'free' tiles chain like on windows version
    checked_list = []
    checked_list.append(tile)

    search_queue = deque()
    search_queue += tile['near_tiles']

    while search_queue:
        curr_cell = search_queue.popleft()
        curr_cell['is_visible'] = True
        if curr_cell['near_mines'] == 0 and curr_cell not in checked_list:
            search_queue += curr_cell['near_tiles']
        checked_list.append(curr_cell)

def discloseEmpty_2(tile,checked):# MUCH QUICKER VERSION
    tile['is_visible'] = True
    checked.append(tile)
    if tile['near_mines'] == 0:
        for neigh in tile['near_tiles']:
            if neigh not in checked:
                discloseEmpty_2(neigh,checked)

def areAllFlagged(mines):
    for mine in mines:
        if not mine['is_flagged']:
            return False
        else:
            continue
    return True

def didPlayerWin(tiles):
    for row in range(TILERESOLUTION):
        for col in range(TILERESOLUTION):
            if tiles[row][col]['is_visible'] == False:
                if tiles[row][col]['is_mined'] == False:
                    return False
    return True

def drawAllBombs(mines):
    for mine in mines:
        mine['is_visible'] = True
        windowSurface.blit(bombTileImg, mine['rect'])

########################################################################################################################

# Set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
pygame.display.set_caption('Minesweeper v1.1')

# Set up the fonts
font = pygame.font.SysFont(None, 48)
fontSign = pygame.font.SysFont(None, 24)

# Set up sounds
####### TODO

# Set up images
startScreenImg = pygame.image.load('img/startScreen.png')
normalTileImg = pygame.image.load('img/cell.png')
emptyTileImg = pygame.image.load('img/empty.png')
flaggedTileImg = pygame.image.load('img/flagged.png')
bombTileImg = pygame.image.load('img/bomb.png')
tileRect = normalTileImg.get_rect()

# Show the 'Start' screenwindowSurface.blit(normalTileImg,tiles[row][col]['rect'])
windowSurface.fill(BACKGROUNDCOLOR)
windowSurface.blit(startScreenImg,startScreenImg.get_rect())
drawText('Minesweeper',font,windowSurface,(WINDOWWIDTH / 3), (WINDOWHEIGHT / 3), TEXTCOLOR)
drawText('Press a key to start', font, windowSurface, (WINDOWWIDTH/3.5), (WINDOWHEIGHT/2), TEXTCOLOR)
drawText('Author: Filip Gajewski', fontSign, windowSurface, (WINDOWWIDTH*0.8), (WINDOWHEIGHT*0.8), BACKGROUNDCOLOR)
pygame.display.update()
waitForPlayerToPressKey()

###starting game TODO: timer
while True:
    # Set up the start of the game
    BOOM = False
    all_flagged = False
    victory = False
    tiles = []
    mines = []

    # Generating tiles grid
    for row in range(TILERESOLUTION):
        tiles.append([])
        for col in range(TILERESOLUTION):
            newTile = {'is_mined': False,
                       'is_flagged': False,
                       'is_visible': False,
                       'near_mines': 0,
                       'near_tiles': [],
                       'position': (row,col),
                       'surface': normalTileImg,
                       'rect': pygame.Rect(TILESIZE * col, TILESIZE * row, TILESIZE, TILESIZE)}
            tiles[row].append(newTile)

    # Put mines on the map
    for mine in range(MINESONMAP):
        row = random.randint(0,TILERESOLUTION - 1)
        col = random.randint(0,TILERESOLUTION - 1)
        if mine not in mines:
            tiles[row][col]['is_mined'] = True
            mines.append(tiles[row][col])

    # Counting mines near the every tile without bomb
    for row in range(TILERESOLUTION):
        for col in range(TILERESOLUTION):
            makeNearTilesListAndBombs(tiles[row][col],tiles)

    while True: # The game loop runs while the game part is playing

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row = pos[1] // TILESIZE
                column = pos[0] // TILESIZE
                if event.button == 1:
                    discloseEmpty_2(tiles[row][column],[])
                    victory = didPlayerWin(tiles)
                    if victory:
                        for mine in mines:
                            mine['is_flagged'] = True
                    if tiles[row][column]['is_mined'] == True:
                        BOOM = True
                if event.button == 3:
                    if not tiles[row][column]['is_visible']:
                        tiles[row][column]['is_flagged'] = not tiles[row][column]['is_flagged']
                        if tiles[row][column]['is_flagged'] :
                            all_flagged = areAllFlagged(mines)  # Return true if all bombs are flagged
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_q:
                    pass

        # Draw the game world on the window
        windowSurface.fill(BACKGROUNDCOLOR)

        # Draw the tiles
        for row in range(TILERESOLUTION):
            for col in range(TILERESOLUTION):
                if tiles[row][col]['is_visible'] == False:
                    windowSurface.blit(normalTileImg,tiles[row][col]['rect'])
                if tiles[row][col]['is_visible'] == True:
                    if tiles[row][col]['is_mined'] == True:
                        drawAllBombs(mines)
                    else:
                        windowSurface.blit(emptyTileImg, tiles[row][col]['rect'])
                        num = str(tiles[row][col]['near_mines'])
                        if num != '0':
                            drawText(num,font,windowSurface,col*TILESIZE+TILESIZE/3,row*TILESIZE+TILESIZE/3,NUMBERCOLOR)
                if tiles[row][col]['is_flagged'] == True:
                    windowSurface.blit(flaggedTileImg, tiles[row][col]['rect'])

        pygame.display.update()

        # Checking the end-game conditions
        if BOOM == True:# Stop the game if you hit a bomb
           # for mine in mines:
            #    mine['is_visible'] = True
            break
        if victory:
            break

        mainClock.tick(FPS)

    # End game message
    if BOOM == True:
        drawText('YOU LOST :(', font, windowSurface, (WINDOWWIDTH/3),(WINDOWHEIGHT/3),TEXTCOLOR)
    elif victory:
        drawText('CONGRATULATIONS !!!', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3), TEXTCOLOR)
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 110,TEXTCOLOR)
    drawText('ESC to quit.', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 180,TEXTCOLOR)
    pygame.display.update()
    waitForPlayerToPressKey()