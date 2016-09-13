'''
Created on 30 de ago. de 2016

@author: gbelloca
'''
#!/usr/bin/python
# #from __future__ import division
import os, pygame, time, picamera, io
#import PIL
from PIL import Image
from pygame.locals import *
import RPi.GPIO as GPIO
import threading



FPS = 25

#COLORES
# R    G    B    A
BLANCO = (255, 255, 255, 255)
GRIS = (185, 185, 185, 255)
NEGRO = (0, 0, 0, 255)

COLOR_SOMBRA_TEXTO = GRIS
COLOR_TEXTO = BLANCO

BGCOLOR = BLANCO

# layout - each "grid" is 8x8px at 640x480
grid_width = 80
grid_height = 60

# photo preview in grid units
preview_pad = 1
preview_x = 4
preview_y = 17
preview_width = 48
preview_height = 40

preview_resolution = (1296, 972)
preview_alpha = 200
blank_thumb = (20, 20, 20, 255)


tiempoPrevisualizarComposicion = 5

# thumb strip in grid units
thumb_strip_pad = 1
thumb_strip_x = 54
thumb_strip_y = 0
thumb_strip_width = 25
thumb_strip_height = grid_height
thumb_photo_width = thumb_strip_width - 2 * thumb_strip_pad
thumb_photo_height = thumb_photo_width * 5 / 6

# font sizes in grid units
basic_font_size = 4
big_font_size = 8
huge_font_size = 50

# Rutas basicas del fotomaton
imgPath = '/home/pi/fotomaton/imagenes/'
marcosPath = '/home/pi/fotomaton/imagenes/marcos/'
composicionesPath = '/home/pi/fotomaton/imagenes/composiciones/'
composicionesPolaroidPath = '/home/pi/fotomaton/imagenes/composiciones/polaroid'
rawPath = '/home/pi/fotomaton/imagenes/raw/'
thumbPath = '/home/pi/fotomaton/imagenes/thumb/'

thumb_size = (400, 300)
thumb_time = 2
thumb_last_sw = 0
thumb_index = 1
thumb_strip = []
thumb_files_number = 0

# GPIO 

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#BOTONES IN
botonAmarillo = 4
botonRojo = 17
botonVerde = 27
botonAzul = 22

#Luz botones OUT
luzBtnAmarillo = 18
luzBtnRojo = 23
luzBtnVerde = 24
luzBtnAzul = 25

#LuzFlash OUT
luzFlash = 12

#variable para saber si la luz está encendida
luzEncendida = False


# setup GPIO IN
GPIO.setup(botonAmarillo, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(botonRojo, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(botonVerde, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(botonAzul, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# setup GPIO OUT
GPIO.setup(luzBtnAmarillo, GPIO.OUT)
GPIO.output(luzBtnAmarillo, False)

GPIO.setup(luzBtnRojo, GPIO.OUT)
GPIO.output(luzBtnRojo, False)

GPIO.setup(luzBtnVerde, GPIO.OUT)
GPIO.output(luzBtnVerde, False)

GPIO.setup(luzBtnAzul, GPIO.OUT)
GPIO.output(luzBtnAzul, False)

GPIO.setup(luzFlash, GPIO.OUT)
GPIO.output(luzFlash, False)


########################################################################################
########################################################################################


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, HUGEFONT, WINDOWWIDTH, WINDOWHEIGHT, CAMERA, GRID_W_PX, GRID_H_PX
    configurarPantalla()
    pygame.init()


    # TAMAÑO DE LA PANTALLA
    WINDOWWIDTH = pygame.display.Info().current_w
    WINDOWHEIGHT = pygame.display.Info().current_h

    GRID_W_PX = int(WINDOWWIDTH / grid_width)
    
    GRID_H_PX = int(WINDOWHEIGHT / grid_height)
    FPSCLOCK = pygame.time.Clock()
    
    pygame.mouse.set_visible(True)  # hide the mouse cursor
    
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN, 32)
##    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE, 32)
    BASICFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * basic_font_size))
    BIGFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * big_font_size))
    HUGEFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * huge_font_size))
    pygame.display.set_caption('Itzi y Guille 17-09-2016')
    
    CAMERA = picamera.PiCamera()
    CAMERA.drc_strength = ('medium')
    mostarTextoEnPantalla('Fotomatón', 'Cargando...')

    #Carga de los thumbnails de las imagenes que se han ido sacando
    cargarImagenesGaleria()
    GPIO.add_event_detect(botonAmarillo, GPIO.FALLING, callback=eventosBoton, bouncetime=1000)
    GPIO.add_event_detect(botonRojo, GPIO.FALLING, callback=eventosBoton, bouncetime=1000)
    GPIO.add_event_detect(botonVerde, GPIO.FALLING, callback=eventosBoton, bouncetime=1000)
    GPIO.add_event_detect(botonAzul, GPIO.FALLING, callback=eventosBoton, bouncetime=1000)
    pygame.event.clear()
    
    while True:
        checkForQuit()
        
        #se configura el estado de las luces de los botones
        GPIO.output(luzBtnAmarillo, True)
        GPIO.output(luzBtnRojo, True)
        GPIO.output(luzBtnVerde, True)
        GPIO.output(luzBtnAzul, False)
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                GPIO.output(luzFlash, False)
                if event.key == K_ESCAPE:
                    pygame.event.clear()
                    terminate()  # terminate if the KEYUP event was for the Esc key
                elif event.key == K_c:  #Leido el evento para crear una composicion de imagenes
                    pygame.event.clear()
                    sacarFotosMultiple(4)
                    pygame.event.clear()
                elif event.key == K_p:  #Leido el evento para crear una foto polaroid
                    pygame.event.clear()
                    sacarFotoPolaroid()
                    pygame.event.clear()
                elif event.key == K_l:  #Leido el evento para encendere las luces
                    pygame.event.clear()
                    #Se comprueba el estado de la luz para hacer la inversa
                    if luzEncendida:
                        GPIO.output(luzFlash, False)
                        luzEncendida = False
                    else:
                        GPIO.output(luzFlash, True)
                        luzEncendida = True
                        
                    pygame.event.clear()
                elif event.key == K_t: #Leido el evento para compartir la imagen en twitter
                    pygame.event.clear()
                    sacarFotoPolaroid()
                    pygame.event.clear()
                elif event.key == K_e:
                    pygame.event.clear()
                    terminate()
        
        pantallaPrincipal()
    terminate()



########################################################################################
########################################################################################


# Turn GPIO (button) events into pygame key down events
def eventosBoton(channel):
    # time.sleep(0.001)
    if GPIO.input(channel) == 1 :
        if channel == botonRojo:
            event = pygame.event.Event(KEYDOWN, key=K_c)
        elif channel == botonVerde:
            event = pygame.event.Event(KEYDOWN, key=K_p)
        elif channel == luzBtnAmarillo:
            event = pygame.event.Event(KEYDOWN, key=K_l)
        elif channel == luzBtnAzul:
            event = pygame.event.Event(KEYDOWN, key=K_t)
        else:
            event = pygame.event.Event(NOEVENT)
    else:
        event = pygame.event.Event(NOEVENT)
    pygame.event.post(event)


########################################################################################
########################################################################################


def sacarFotosMultiple(numPhotos):
    #Apagamos la luz de los botones
    GPIO.output(luzBtnAmarillo, False)
    GPIO.output(luzBtnRojo, False)
    GPIO.output(luzBtnVerde, False)
    imageArray = []
    DISPLAYSURF.fill(NEGRO)
    CAMERA.preview_fullscreen = True
##    CAMERA.preview_fullscreen = False
    CAMERA.preview_alpha = preview_alpha
    readySurf, readyRect = crearObjetosTexto('Preparados...', BIGFONT, BLANCO)
    readyRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT / 10 * 9)
    DISPLAYSURF.blit(readySurf, readyRect)
    pygame.display.update()
    time.sleep(1.4)
    
    for photo in range (0, numPhotos):
        time.sleep(0.1)
        # Cuenta atrás para sacar la foto, muestra los numeros en grande en la pantalla.
        for i in range (5, 0, -1):
            DISPLAYSURF.fill(NEGRO)
            numSurf, numRect = crearObjetosTexto(str(i), HUGEFONT, BLANCO)
            numRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 - GRID_H_PX)
            DISPLAYSURF.blit(numSurf, numRect)
            numphotosSurf, numphotosRect = crearObjetosTexto('Foto ' + str(photo + 1) + ' de ' + str(numPhotos), BIGFONT, BLANCO)
            numphotosRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT - GRID_H_PX * 4)
            DISPLAYSURF.blit(numphotosSurf, numphotosRect)
            pygame.display.update()
            time.sleep(0.8)  # cada numero se muestra este tiempo
        
        # Se limpia la pantalla.
        DISPLAYSURF.fill(NEGRO)
        takephotoSurf, takephotoRect = crearObjetosTexto('Capturando foto ' + str(photo + 1), BIGFONT, BLANCO)
        takephotoRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT / 10 * 9)
        DISPLAYSURF.blit(takephotoSurf, takephotoRect)
        pygame.display.update()
        imageArray.append(capturarFoto())  # Se captura la foto
        
    DISPLAYSURF.fill(NEGRO)  # Se limpia la pantalla.
    pygame.display.update()
    CAMERA.stop_preview()
    mostarTextoEnPantalla('Fotomaton', 'Procesando...')

    crearComposicionCuadricula(imageArray)
    
    CAMERA.resolution = preview_resolution
    CAMERA.preview_fullscreen = False
    CAMERA.start_preview()
    CAMERA.awb_mode = 'auto'
    CAMERA.exposure_mode = 'auto'


########################################################################################
########################################################################################

def sacarFotoPolaroid():
    
    #Apagamos la luz de los botones
    GPIO.output(luzBtnAmarillo, False)
    GPIO.output(luzBtnRojo, False)
    GPIO.output(luzBtnVerde, False)
    
    DISPLAYSURF.fill(NEGRO)
    CAMERA.preview_fullscreen = True
##    CAMERA.preview_fullscreen = False
    CAMERA.preview_alpha = preview_alpha
    readySurf, readyRect = crearObjetosTexto('Preparados...', BIGFONT, BLANCO)
    readyRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT / 10 * 9)
    DISPLAYSURF.blit(readySurf, readyRect)
    pygame.display.update()
    time.sleep(1.4)
    

    # Cuenta atrás para sacar la foto, muestra los numeros en grande en la pantalla.
    for i in range (5, 0, -1):
        DISPLAYSURF.fill(NEGRO)
        numSurf, numRect = crearObjetosTexto(str(i), HUGEFONT, BLANCO)
        numRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 - GRID_H_PX)
        DISPLAYSURF.blit(numSurf, numRect)
        pygame.display.update()
        time.sleep(0.8)  # cada numero se muestra este tiempo
        
    # Se limpia la pantalla.
    DISPLAYSURF.fill(NEGRO)
    takephotoSurf, takephotoRect = crearObjetosTexto('Capturando foto... ', BIGFONT, BLANCO)
    takephotoRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT / 10 * 9)
    DISPLAYSURF.blit(takephotoSurf, takephotoRect)
    pygame.display.update()
    foto = capturarFoto()  # Se captura la foto
        
    DISPLAYSURF.fill(NEGRO)  # Se limpia la pantalla.
    pygame.display.update()
    CAMERA.stop_preview()
    mostarTextoEnPantalla('Fotomaton', 'Procesando...')

    crearComposicionPolaroid(foto)
    
    CAMERA.resolution = preview_resolution
    CAMERA.preview_fullscreen = False
    CAMERA.start_preview()
    CAMERA.awb_mode = 'auto'
    CAMERA.exposure_mode = 'auto'

########################################################################################
########################################################################################
    
def crearComposicionCuadricula(imageArray):
    marco = Image.open(marcosPath + "/marco_motos.jpg")
    img_size = [467, 373]
    nombreComposicion = str(time.time())
    composicion = Image.new('RGBA', marco.size, BLANCO)
    paste_x = 182
    paste_y = 33

    composicion.paste(marco, (0, 0))

    for imagen in imageArray:
        nombreFoto = str(time.time())
        imagen.save(rawPath + nombreFoto + '.jpg', 'JPEG', quality=100)
        resized = imagen.resize((img_size[0], img_size[1]), Image.ANTIALIAS)
        
        #Se lanza en otro hilo de ejecucion el redimensionado de la imagen para los Thumb
        hiloCrearThumb = threading.Thread(target=guardarImagenThumb, name='Redimensionado', args=(imagen, nombreFoto,))
        hiloCrearThumb.start()
        
        composicion.paste(resized, (paste_x, paste_y))
        if paste_x == 182 and paste_y == 33 :
            paste_x = 689
        elif paste_x == 689 and paste_y == 33 :
            paste_x = 182
            paste_y = 529
        else :
            paste_x = 689
            paste_y = 530

    
    composicion.save(composicionesPath + '/' + nombreComposicion + ".jpg", "JPEG", quality=100)
    mostrarImagen(composicionesPath + '/' + nombreComposicion + ".jpg")
    time.sleep(tiempoPrevisualizarComposicion) #Se muestra la imagen creada durante el numero de segundos indicado


########################################################################################
########################################################################################


def crearComposicionPolaroid(imagen):
    marco = Image.open(marcosPath +"/marco_motos_polaroid.jpg")
    
    img_size = [781, 827]
    nombreComposicion = 'POLAROID_' +str(time.time())
    paste_x = 107
    paste_y = 127
    
    resized = imagen.resize((img_size[0],img_size[1]),Image.ANTIALIAS)
    marco.paste(resized,(paste_x,paste_y))
    marco.save(composicionesPolaroidPath + '/' + nombreComposicion + ".jpg","JPEG",quality=100)
    
    #Se lanza en otro hilo de ejecucion el redimensionado de la imagen para los Thumb
    hiloCrearThumb = threading.Thread(target=guardarImagenThumb, name='Redimensionado', args=(imagen, nombreComposicion,))
    hiloCrearThumb.start()
    
    mostrarImagen(composicionesPolaroidPath + '/' + nombreComposicion + ".jpg")
    time.sleep(tiempoPrevisualizarComposicion) #Se muestra la imagen creada durante el numero de segundos indicado


########################################################################################
########################################################################################


def guardarImagenThumb(imagen, nombreThumb):
    resized = imagen.resize(thumb_size, Image.ANTIALIAS)
    resized.save(thumbPath + nombreThumb + '.jpg', 'JPEG', quality=100)
    

########################################################################################
########################################################################################


def capturarFoto():
    stream = io.BytesIO()  # IO stream para guardar la imagen
    CAMERA.capture(stream, 'jpeg', False, None, None, quality=100)  # Se saca la foto
    stream.seek(0)  # Se posiciona en el primer byte del IO Stream de la imagen
    foto = Image.open(stream)  # Se crea un objeto de imagen PIL para procesarse luego
    return foto


########################################################################################
########################################################################################


def pantallaPrincipal():
    global thumb_last_sw
    CAMERA.preview_fullscreen = False
    CAMERA.resolution = preview_resolution
    CAMERA.preview_window = (GRID_W_PX * (preview_x + preview_pad), GRID_H_PX * (preview_y + preview_pad), GRID_W_PX * (preview_width - (2 * preview_pad)), GRID_H_PX * (preview_height - (2 * preview_pad)))
    CAMERA.preview_alpha = preview_alpha
    CAMERA.led = False
    DISPLAYSURF.fill(BGCOLOR)
    
    # Ponemos el fondo que queramos
    background_image = cargar_imagen(marcosPath + 'fondo_fotomaton.jpg', False, False)
    DISPLAYSURF.blit(background_image, (0, 0))

    # En este bloque se definen los parametros de la previsualización de la camara
    border = pygame.Surface((GRID_W_PX * preview_width, GRID_H_PX * preview_height))
    border.fill(NEGRO)
    borderRect = DISPLAYSURF.blit(border, (GRID_W_PX * preview_x, GRID_H_PX * preview_y))
    startSurf, startRect = crearObjetosTexto('Pulsa el rojo', BASICFONT, BLANCO)
    startRect.midbottom = (borderRect[2] / 2 + borderRect[0], borderRect[3] + borderRect[1] - 10)
    DISPLAYSURF.blit(startSurf, startRect)

    CAMERA.start_preview()
    CAMERA.awb_mode = 'auto'
    CAMERA.exposure_mode = 'auto'

    pygame.display.update()
    thumb_last_sw = 0
    while not pygame.event.peek(KEYDOWN):
        pygame.display.update(galeriaImagenesLateral())
        FPSCLOCK.tick(FPS)


########################################################################################
########################################################################################


def galeriaImagenesLateral():
    global thumb_index, thumb_last_sw

    if len(os.listdir(thumbPath)) > thumb_files_number:
        cargarImagenesGaleria()

    if time.time() - thumb_time > thumb_last_sw:
        thumb_last_sw = time.time()
        strip = pygame.Surface((thumb_strip_width * GRID_W_PX, thumb_strip_height * GRID_H_PX), pygame.SRCALPHA)
        strip.fill(NEGRO)
        thumb_h_pos = (thumb_photo_height + thumb_strip_pad) * GRID_H_PX
        thumb_index += 1
        for i in range (0, thumb_files_number):
            strip.blit(thumb_strip[i], (thumb_strip_pad * GRID_W_PX, ((thumb_index + i) % thumb_files_number) * thumb_h_pos))
        return DISPLAYSURF.blit(strip, (GRID_W_PX * thumb_strip_x, GRID_H_PX * thumb_strip_y))
        

########################################################################################
########################################################################################


def cargarImagenesGaleria():
    global thumb_strip
    del thumb_strip[:]  # ELIMINA EL CONTENIDO DEL ARRAY DE IMAGENES LATERALES
    
    global thumb_files_number

    thumb_size = (int(thumb_photo_width * GRID_W_PX), int(thumb_photo_height * GRID_H_PX))
    for dirName, subdirList, fileList in os.walk(thumbPath):
        thumb_files_number = len(fileList)
        for fname in fileList:
            try:
               thumb_strip.append(pygame.transform.smoothscale(pygame.image.load(thumbPath + fname).convert(), thumb_size))
            except:
                thumb_strip.append(pygame.Surface(thumb_size))
                thumb_strip[0].fill(blank_thumb)


########################################################################################
########################################################################################


def crearObjetosTexto(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


########################################################################################
########################################################################################


def terminate():
    CAMERA.stop_preview()
    CAMERA.close()
    mostarTextoEnPantalla('Cerrando', '')
    pygame.quit()   


########################################################################################
########################################################################################


def checkForQuit():
    for event in pygame.event.get(QUIT):  # obtiene todos los eventos de tipo QUIT
        terminate()  # llama al terminate si algun evento de tipo QUIT se ha invocado
    for event in pygame.event.get(KEYUP):  # obtiene todos los eventos de tipo KEYUP
        if event.key == K_ESCAPE:
            terminate()  # llama al terminate spulsado la tecla Esc
        pygame.event.post(event)  # Se ponen de nuevo los eventos de tipo KEYUP


########################################################################################
########################################################################################


def mostarTextoEnPantalla(text, text2):
    # This function displays large text in the
    DISPLAYSURF.fill(NEGRO)
    
    # Draw the text drop shadow
    titleSurf, titleRect = crearObjetosTexto(text, BIGFONT, COLOR_SOMBRA_TEXTO)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = crearObjetosTexto(text, BIGFONT, COLOR_TEXTO)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = crearObjetosTexto(text2, BASICFONT, COLOR_TEXTO)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    pygame.display.update()


########################################################################################
########################################################################################


def cargar_imagen(filename, transformar=True, transparent=False):
    try: 
        if transformar:
            image = pygame.transform.smoothscale(pygame.image.load(filename).convert(), (WINDOWWIDTH, WINDOWHEIGHT))
        else:
            image = pygame.image.load(filename)
    except pygame.error:
            raise Exception('ERROR AL CARGAR LA IMAGEN')
            
    # image = image.convert()
    if transparent:
            color = image.get_at((0, 0))
            image.set_colorkey(color, RLEACCEL)
    return image


########################################################################################
########################################################################################


def mostrarImagen(rutaImagen):
    image = pygame.transform.scale(pygame.image.load(rutaImagen), (WINDOWWIDTH, WINDOWHEIGHT))
    DISPLAYSURF.blit(image, (0, 0))
    pygame.display.update()


########################################################################################
########################################################################################


def configurarPantalla():
    disp_no = os.getenv("DISPLAY")

    # Check which frame buffer drivers are available
    # Start with fbcon since directfb hangs with composite output
    drivers = ['fbcon', 'directfb', 'svgalib']
    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
##            print 'Driver: {0} failed.'.format(driver)
            continue
        found = True
        break

    if not found:
        raise Exception('No suitable video driver found!')



########################################################################################
########################################################################################

if __name__ == '__main__':
    main()
