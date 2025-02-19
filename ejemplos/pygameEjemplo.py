#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Módulos
import sys, pygame
from pygame.locals import *
 
# Constantes
WIDTH = 640
HEIGHT = 480

ejemploImgPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/ejemplos/'
 
# Clases
# ---------------------------------------------------------------------
class Bola(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(ejemploImgPath + 'ball.png', True)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2
        self.speed = [0.5, -0.5]
   
    def actualizar(self, time, pala_jug, pala_cpu, puntos):
        self.rect.centerx += self.speed[0] * time
        self.rect.centery += self.speed[1] * time
    
        if self.rect.left <= 0:
            puntos[1] += 1
            print('PUNTUACION: ' + str(puntos[0]) + ' - ' + str(puntos[1]))
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT / 2
            self.speed = [-0.5, 0.5]
        if self.rect.right >= WIDTH:
            puntos[0] += 1
            print('PUNTUACION: ' + str(puntos[0]) + ' - ' + str(puntos[1]))
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT / 2
            self.speed = [0.5, -0.5]

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed[0] = -self.speed[0]
            self.rect.centerx += self.speed[0] * time
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed[1] = -self.speed[1]
            self.rect.centery += self.speed[1] * time
    
        if pygame.sprite.collide_rect(self, pala_jug):
            self.speed[0] = -self.speed[0]
            self.rect.centerx += self.speed[0] * time
    
        if pygame.sprite.collide_rect(self, pala_cpu):
            self.speed[0] = -self.speed[0]
            self.rect.centerx += self.speed[0] * time
    
        return puntos


class Pala(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(ejemploImgPath + 'pala.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = HEIGHT / 2
        self.speed = 0.4

    def mover(self, time, keys):
        if self.rect.top >= 0:
            if keys[K_UP]:
                self.rect.centery -= self.speed * time
        if self.rect.bottom <= HEIGHT:
            if keys[K_DOWN]:
                self.rect.centery += self.speed * time

    def ia(self, time, ball):
        if ball.speed[0] >= 0 and ball.rect.centerx >= WIDTH/2:
            if self.rect.centery < ball.rect.centery:
                self.rect.centery += self.speed * time
            if self.rect.centery > ball.rect.centery:
                self.rect.centery -= self.speed * time
# ---------------------------------------------------------------------
 
# Funciones
# ---------------------------------------------------------------------
def load_image(filename, transparent=False):
    try: image = pygame.image.load(filename)
    except pygame.error:
            raise Exception('ERROR AL CARGAR LA IMAGEN')
            raise SystemExit
            
    image = image.convert()
    if transparent:
            color = image.get_at((0,0))
            image.set_colorkey(color, RLEACCEL)
    return image


def texto(texto, posx, posy, color=(255, 255, 255)):
    fuente = pygame.font.Font(ejemploImgPath + 'DroidSans.ttf', 25)
    salida = pygame.font.Font.render(fuente, texto, 1, color)
    salida_rect = salida.get_rect()
    salida_rect.centerx = posx
    salida_rect.centery = posy
    return salida, salida_rect

def showTextScreen(text):

    #variables para el texto
    GRAY        = (185, 185, 185, 255)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 20)
        
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, GRAY)
    titleRect.center = (int(WIDTH / 2), 10)
    screen.blit(titleSurf, titleRect)

    pygame.display.update()

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()
# ---------------------------------------------------------------------
 
def main():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pruebas Pygame")
 
    background_image = load_image(ejemploImgPath + 'fondo_pong.png')
    bola = Bola()
    pala_jug = Pala(30)
    pala_cpu = Pala(WIDTH - 30)
 
    clock = pygame.time.Clock()

    puntos = [0,0]
 
    while True:
        time = clock.tick(60)
        keys = pygame.key.get_pressed()
        for eventos in pygame.event.get():
            if eventos.type == QUIT:
                sys.exit(0)
 
        puntos = bola.actualizar(time, pala_jug, pala_cpu, puntos)
        showTextScreen('MARCADOR')
        pala_jug.mover(time, keys)
        pala_cpu.ia(time, bola)

        p_jug, p_jug_rect = texto(str(puntos[0]), WIDTH/4, 40)
        p_cpu, p_cpu_rect = texto(str(puntos[1]), WIDTH-WIDTH/4, 40)

        screen.blit(background_image, (0, 0))
        screen.blit(bola.image, bola.rect)
        screen.blit(pala_jug.image, pala_jug.rect)
        screen.blit(pala_cpu.image, pala_cpu.rect)
        pygame.display.flip()
    return 0

# ---------------------------------------------------------------------
 
if __name__ == '__main__':
    pygame.init()
    main()