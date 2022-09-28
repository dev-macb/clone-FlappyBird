# Importação de bibliotecas
import sys
import pygame
import random
from pygame.locals import *
from itertools import cycle

# Declaração de constantes
FPS = 30

TELA_LARGURA = 288
TELA_ALTURA = 512
TAMANHO_VAO_TUBO = 100 # gap between upper and lower part of pipe
BASEY        = TELA_ALTURA * 0.79
# image, sound and hitmask  dicts
IMAGENS, SONS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
LISTA_JOGADORES = (
    ('assets/sprites/redbird-upflap.png', 'assets/sprites/redbird-midflap.png', 'assets/sprites/redbird-downflap.png'),
    ('assets/sprites/bluebird-upflap.png', 'assets/sprites/bluebird-midflap.png', 'assets/sprites/bluebird-downflap.png'),
    ('assets/sprites/yellowbird-upflap.png', 'assets/sprites/yellowbird-midflap.png', 'assets/sprites/yellowbird-downflap.png')
)

# list of backgrounds
LISTA_FUNDOS = ('assets/sprites/background-day.png', 'assets/sprites/background-night.png')

# list of pipes
LISTA_TUBOS = ('assets/sprites/pipe-green.png', 'assets/sprites/pipe-red.png')


try:
    xrange
except NameError:
    xrange = range


def principal():
    global JANELA, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    JANELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pygame.display.set_caption('Flappy Bird')
    pygame_icon = pygame.image.load('assets/flappy.ico')
    pygame.display.set_icon(pygame_icon)

    # numbers sprites for score display
    IMAGENS['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGENS['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome JANELA
    IMAGENS['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGENS['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # SONS
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SONS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SONS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SONS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SONS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SONS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(LISTA_FUNDOS) - 1)
        IMAGENS['background'] = pygame.image.load(LISTA_FUNDOS[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(LISTA_JOGADORES) - 1)
        IMAGENS['player'] = (
            pygame.image.load(LISTA_JOGADORES[randPlayer][0]).convert_alpha(),
            pygame.image.load(LISTA_JOGADORES[randPlayer][1]).convert_alpha(),
            pygame.image.load(LISTA_JOGADORES[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        index_tubo = random.randint(0, len(LISTA_TUBOS) - 1)
        IMAGENS['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(LISTA_TUBOS[index_tubo]).convert_alpha(), False, True),
            pygame.image.load(LISTA_TUBOS[index_tubo]).convert_alpha(),
        )

        # hitmask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGENS['pipe'][0]),
            getHitmask(IMAGENS['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGENS['player'][0]),
            getHitmask(IMAGENS['player'][1]),
            getHitmask(IMAGENS['player'][2]),
        )

        info_movimento = mostrarAnimacaoBoasVindas()
        crashInfo = jogoPrincipal(info_movimento)
        showGameOverJANELA(crashInfo)


def mostrarAnimacaoBoasVindas():
    """Shows welcome JANELA animation of flappy bird"""
    # index of player to blit on JANELA
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(TELA_LARGURA * 0.2)
    playery = int((TELA_ALTURA - IMAGENS['player'][0].get_height()) / 2)

    messagex = int((TELA_LARGURA - IMAGENS['message'].get_width()) / 2)
    messagey = int(TELA_ALTURA * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGENS['base'].get_width() - IMAGENS['background'].get_width()

    # player shm for up-down motion on welcome JANELA
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for jogoPrincipal
                SONS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        JANELA.blit(IMAGENS['background'], (0,0))
        JANELA.blit(IMAGENS['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        JANELA.blit(IMAGENS['message'], (messagex, messagey))
        JANELA.blit(IMAGENS['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def jogoPrincipal(info_movimento):
    score = playerIndex = loopIter = 0
    playerIndexGen = info_movimento['playerIndexGen']
    playerx, playery = int(TELA_LARGURA * 0.2), info_movimento['playery']

    basex = info_movimento['basex']
    baseShift = IMAGENS['base'].get_width() - IMAGENS['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': TELA_LARGURA + 200, 'y': newPipe1[0]['y']},
        {'x': TELA_LARGURA + 200 + (TELA_LARGURA / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': TELA_LARGURA + 200, 'y': newPipe1[1]['y']},
        {'x': TELA_LARGURA + 200 + (TELA_LARGURA / 2), 'y': newPipe2[1]['y']},
    ]

    dt = FPSCLOCK.tick(FPS)/1000
    pipeVelX = -128 * dt

    # player velocity, max velocity, downward acceleration, acceleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward acceleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGENS['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SONS['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGENS['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGENS['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SONS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGENS['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of JANELA
        if 3 > len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the JANELA
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGENS['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        JANELA.blit(IMAGENS['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            JANELA.blit(IMAGENS['pipe'][0], (uPipe['x'], uPipe['y']))
            JANELA.blit(IMAGENS['pipe'][1], (lPipe['x'], lPipe['y']))

        JANELA.blit(IMAGENS['base'], (basex, BASEY))
        # print score so player overlaps the score
        mostrarPontuacao(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGENS['player'][playerIndex], visibleRot)
        JANELA.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverJANELA(crashInfo):
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = TELA_LARGURA * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGENS['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die SONS
    SONS['hit'].play()
    if not crashInfo['groundCrash']:
        SONS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        JANELA.blit(IMAGENS['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            JANELA.blit(IMAGENS['pipe'][0], (uPipe['x'], uPipe['y']))
            JANELA.blit(IMAGENS['pipe'][1], (lPipe['x'], lPipe['y']))

        JANELA.blit(IMAGENS['base'], (basex, BASEY))
        mostrarPontuacao(score)

        playerSurface = pygame.transform.rotate(IMAGENS['player'][1], playerRot)
        JANELA.blit(playerSurface, (playerx,playery))
        JANELA.blit(IMAGENS['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """ Oscila o valor de playerShm['val'] entre 8 e -8. """
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """ Retorna um pipe gerado aleatoriamente. """
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - TAMANHO_VAO_TUBO))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGENS['pipe'][0].get_height()
    pipeX = TELA_LARGURA + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # Tubo superior
        {'x': pipeX, 'y': gapY + TAMANHO_VAO_TUBO}, # Tubo inferior
    ]


def mostrarPontuacao(score):
    """ Exibe pontuação no centro da janela. """
    totalWidth  = 0 # Largura total de todos os números a serem impressos
    scoreDigits = [ int(x) for x in list(str(score)) ]
    
    for digit in scoreDigits:
        totalWidth += IMAGENS['numbers'][digit].get_width()

    Xoffset = (TELA_LARGURA - totalWidth) / 2

    for digit in scoreDigits:
        JANELA.blit(IMAGENS['numbers'][digit], (Xoffset, TELA_ALTURA * 0.1))
        Xoffset += IMAGENS['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """ Retorna True se o jogador colidir com a base ou nos tubos. """
    pi = player['index']
    player['w'] = IMAGENS['player'][0].get_width()
    player['h'] = IMAGENS['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGENS['pipe'][0].get_width()
        pipeH = IMAGENS['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """ Verifica se dois objetos colidem e não apenas seus retos. """
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False


def getHitmask(image):
    """ Retorna uma hitmask usando o alfa de uma imagem. """
    mascara = []
    for x in xrange(image.get_width()):
        mascara.append([])
        for y in xrange(image.get_height()):
            mascara[x].append(bool(image.get_at((x,y))[3]))
    return mascara


if __name__ == '__main__':
    principal()
