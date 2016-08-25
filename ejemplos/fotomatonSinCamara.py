#!/usr/bin/python
##from __future__ import division
import os, pygame, time, sys
import PIL
from PIL import Image
from pygame.locals import *

FPS = 25
#               R    G    B    A
WHITE       = (255, 255, 255, 255)
GRAY        = (185, 185, 185, 255)
BLACK       = (  0,   0,   0, 255)
DARKBLUE    = (  0,   0, 100, 255)
TEXTSHADOWCOLOR = GRAY
TEXTCOLOR = WHITE
BGCOLOR = DARKBLUE

# layout - each "grid" is 8x8px at 640x480
grid_width = 80
grid_height = 60

# photo preview in grid units
preview_pad    = 1
preview_x      = 4
preview_y      = 14
preview_width  = 48
preview_height = 40

# thumb strip in grid units
thumb_strip_pad    = 1
thumb_strip_x      = 54
thumb_strip_y      = 0
thumb_strip_width  = 28
thumb_strip_height = grid_height
thumb_photo_width  = thumb_strip_width - 2 * thumb_strip_pad
thumb_photo_height = thumb_photo_width * 3 / 4

# font sizes in grid units
basic_font_size    = 4
big_font_size      = 8
huge_font_size     = 50

#Rutas basicas del fotomaton



imgPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/raw/'
composicionesPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/composiciones/'
marcosPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/marcos/'
thumb_loc = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/thumb/'
rawPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/raw/'

thumb_size = (400,300)
thumb_time = 2
thumb_last_sw = 0
thumb_index = 1
thumb_strip = []
thumb_files_number = 0

preview_resolution = (1296,972)
preview_alpha  = 200
blank_thumb = (20,20,20,255)


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, HUGEFONT, WINDOWWIDTH, WINDOWHEIGHT, GRID_W_PX, GRID_H_PX
    setupDisplay()
    pygame.init()

    # TAMAÑO DE LA PANTALLA
    WINDOWWIDTH = pygame.display.Info().current_w
    WINDOWHEIGHT = pygame.display.Info().current_h

    GRID_W_PX   = int(WINDOWWIDTH / grid_width)
    
    GRID_H_PX    = int(WINDOWHEIGHT / grid_height)
    FPSCLOCK = pygame.time.Clock()
    pygame.mouse.set_visible(True) #hide the mouse cursor
    #DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN, 32)
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE, 32)
    BASICFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * basic_font_size))
    BIGFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * big_font_size))
    HUGEFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * huge_font_size))
    pygame.display.set_caption('Itzi y Guille 17-09-2016')
    
    showTextScreen('Fotomatón','Cargando...')

    loadThumbs()
    pygame.event.clear()
    
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.clear()
                   
                elif event.key == K_SPACE:
                    pygame.event.clear()
                    
                    pygame.event.clear()
                elif event.key == K_e:
                    pygame.event.clear()
                    
        idleScreen()



def displayImage(image):
    image = pygame.transform.scale(pygame.image.load(image),(WINDOWWIDTH,WINDOWHEIGHT))
    DISPLAYSURF.blit(image,(0,0))
    pygame.display.update()
    sleep(5)

def idleScreen():
    global thumb_last_sw
    
    DISPLAYSURF.fill(BGCOLOR)

    background_image = cargar_imagen( marcosPath + 'marco_motos.jpg')
    DISPLAYSURF.blit(background_image, (0, 0))
    
    border = pygame.Surface((GRID_W_PX * preview_width, GRID_H_PX * preview_height))
    border.fill(BLACK)
    borderRect = DISPLAYSURF.blit(border,(GRID_W_PX * preview_x, GRID_H_PX * preview_y))
    startSurf, startRect = makeTextObjs('Press Start', BASICFONT, WHITE)
    startRect.midbottom = (borderRect[2]/2+borderRect[0],borderRect[3]+borderRect[1]-10)
    DISPLAYSURF.blit(startSurf, startRect)
    titleSurf, titleRect = makeTextObjs('Fotomaton', BIGFONT, GRAY)
    titleRect.bottomleft = (borderRect[0] + preview_pad * GRID_W_PX ,borderRect[1])
    DISPLAYSURF.blit(titleSurf, titleRect)

    pygame.display.update()
    thumb_last_sw = 0
    while not pygame.event.peek(KEYDOWN):
        pygame.display.update(filmStrip())
        FPSCLOCK.tick(FPS)

def filmStrip():
    global thumb_index, thumb_last_sw

    if len(os.listdir(rawPath)) > thumb_files_number:
        loadThumbs()

    if time.time() - thumb_time > thumb_last_sw:
        thumb_last_sw = time.time()
        strip = pygame.Surface((thumb_strip_width * GRID_W_PX, thumb_strip_height * GRID_H_PX),pygame.SRCALPHA)
        strip.fill(BLACK)
        thumb_h_pos = (thumb_photo_height + thumb_strip_pad) * GRID_H_PX
        thumb_index += 1
        for i in range (0,thumb_files_number):
            strip.blit(thumb_strip[i],(thumb_strip_pad * GRID_W_PX,((thumb_index+i)%thumb_files_number)*thumb_h_pos))
        return DISPLAYSURF.blit(strip,(GRID_W_PX * thumb_strip_x, GRID_H_PX * thumb_strip_y))
        
def loadThumbs():
    global thumb_strip
    del thumb_strip[:] # ELIMINA EL CONTENIDO DEL ARRAY DE IMAGENES LATERALES
    
    global thumb_files_number

    thumb_size = (int(thumb_photo_width * GRID_W_PX), int(thumb_photo_height * GRID_H_PX))
    for dirName, subdirList, fileList in os.walk(rawPath):
        thumb_files_number = len(fileList)
        for fname in fileList:
            try:
               thumb_strip.append(pygame.transform.smoothscale(pygame.image.load(rawPath + fname).convert(),thumb_size))
            except:
                thumb_strip.append(pygame.Surface(thumb_size))
                thumb_strip[i].fill(blank_thumb)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def showTextScreen(text, text2):
    # This function displays large text in the
    DISPLAYSURF.fill(BLACK)
    
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs(text2, BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    pygame.display.update()


def cargar_imagen(filename, transparent=False):
    try: 
        image = pygame.transform.smoothscale(pygame.image.load(filename).convert(),(WINDOWWIDTH,WINDOWHEIGHT))
        #image = pygame.image.load(filename)
    except pygame.error:
            raise Exception('ERROR AL CARGAR LA IMAGEN')
            raise SystemExit
            
    image = image.convert()
    if transparent:
            color = image.get_at((0,0))
            image.set_colorkey(color, RLEACCEL)
    return image

def setupDisplay():
    disp_no = os.getenv("DISPLAY")
    pygame.display.init()
    


if __name__ == '__main__':
    main()