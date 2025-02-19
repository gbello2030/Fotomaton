#!/usr/bin/python
##from __future__ import division
import os, pygame, time, picamera, io, sys
import PIL
from PIL import Image
from pygame.locals import *
import RPi.GPIO as GPIO


FPS = 25
#               R    G    B    A
WHITE       = (255, 255, 255, 255)
GRAY        = (185, 185, 185, 255)
BLACK       = (  0,   0,   0, 255)
DARKBLUE    = (  0,   0, 100, 255)
TEXTSHADOWCOLOR = GRAY
TEXTCOLOR = WHITE
BGCOLOR = WHITE

# layout - each "grid" is 8x8px at 640x480
grid_width = 80
grid_height = 60

# photo preview in grid units
preview_pad    = 1
preview_x      = 4
preview_y      = 17
preview_width  = 48
preview_height = 40

# thumb strip in grid units
thumb_strip_pad    = 1
thumb_strip_x      = 54
thumb_strip_y      = 0
thumb_strip_width  = 25
thumb_strip_height = grid_height
thumb_photo_width  = thumb_strip_width - 2 * thumb_strip_pad
thumb_photo_height = thumb_photo_width * 5/6

# font sizes in grid units
basic_font_size    = 4
big_font_size      = 8
huge_font_size     = 50

#Rutas basicas del fotomaton
imgPath = '/home/pi/fotomaton/imagenes/'
marcosPath = '/home/pi/fotomaton/imagenes/marcos/'
composicionesPath = '/home/pi/fotomaton/imagenes/composiciones/'
rawPath = '/home/pi/fotomaton/imagenes/raw/'
thumb_loc = '/home/pi/fotomaton/imagenes/thumb/'

thumb_size = (400,300)
thumb_time = 2
thumb_last_sw = 0
thumb_index = 1
thumb_strip = []
thumb_files_number = 0

preview_resolution = (1296,972)
preview_alpha  = 200
blank_thumb = (20,20,20,255)

# GPIO 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
io_start_bttn  = 26
io_start_light = 21
io_enter_bttn  = 16
io_enter_light = 19
io_up_bttn     = 20
io_up_light    = 5
io_dn_bttn     = 12
io_dn_light    = 6
io_cameara_led = 18

# setup GPIO
GPIO.setup(io_start_bttn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(io_enter_bttn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(io_up_bttn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(io_dn_bttn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(io_start_light, GPIO.OUT)
GPIO.output(io_start_light, False)
GPIO.setup(io_enter_light, GPIO.OUT)
GPIO.output(io_enter_light, True)
GPIO.setup(io_up_light, GPIO.OUT)
GPIO.output(io_up_light, True)
GPIO.setup(io_dn_light, GPIO.OUT)
GPIO.output(io_dn_light, True)
GPIO.setup(io_cameara_led, GPIO.OUT)
GPIO.output(io_cameara_led, True)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, HUGEFONT, WINDOWWIDTH, WINDOWHEIGHT, CAMERA, GRID_W_PX, GRID_H_PX
    setupDisplay()
    pygame.init()

    # TAMAÑO DE LA PANTALLA
    WINDOWWIDTH = pygame.display.Info().current_w
    WINDOWHEIGHT = pygame.display.Info().current_h

    GRID_W_PX   = int(WINDOWWIDTH / grid_width)
    GRID_H_PX    = int(WINDOWHEIGHT / grid_height)

    FPSCLOCK = pygame.time.Clock()
    
    pygame.mouse.set_visible(True) #hide the mouse cursor
##    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN, 32)
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.RESIZABLE, 32)
    BASICFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * basic_font_size))
    BIGFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * big_font_size))
    HUGEFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * huge_font_size))
    pygame.display.set_caption('Itzi y Guille 17-09-2016')
    
    CAMERA = picamera.PiCamera()
    CAMERA.drc_strength = ('medium')
    showTextScreen('Fotomatón','Cargando...')

    loadThumbs()
    GPIO.add_event_detect(io_start_bttn, GPIO.FALLING, callback=buttonEvent, bouncetime=1000)
    GPIO.add_event_detect(io_enter_bttn, GPIO.FALLING, callback=buttonEvent, bouncetime=1000)
    GPIO.add_event_detect(io_up_bttn, GPIO.FALLING, callback=buttonEvent, bouncetime=1000)
    GPIO.add_event_detect(io_dn_bttn, GPIO.FALLING, callback=buttonEvent, bouncetime=1000)
    pygame.event.clear()
    
    while True:
        #checkForQuit()
        GPIO.output(io_start_light, False)
        GPIO.output(io_enter_light, False)
        GPIO.output(io_up_light, False)
        GPIO.output(io_dn_light, False)
        GPIO.output(io_cameara_led, False)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                GPIO.output(io_start_light, False)
                if event.key == K_ESCAPE:
                    pygame.event.clear()
                    powerOff() # terminate if the KEYUP event was for the Esc key
                elif event.key == K_SPACE:
                    pygame.event.clear()
                    photoShoot(4)
                    pygame.event.clear()
                elif event.key == K_e:
                    pygame.event.clear()
                    terminate()
        GPIO.output(io_start_light, True)
        idleScreen()
    terminate()
    
# Turn GPIO (button) events into pygame key down events
def buttonEvent(channel):
    #time.sleep(0.001)
    if GPIO.input(channel) == 1 :
        if channel == io_start_bttn:
            event = pygame.event.Event(KEYDOWN, key = K_SPACE)
        elif channel == io_enter_bttn:
            event = pygame.event.Event(KEYDOWN, key = K_RETURN)
        elif channel == io_up_bttn:
            event = pygame.event.Event(KEYDOWN, key = K_UP)
        elif channel == io_dn_bttn:
            event = pygame.event.Event(KEYDOWN, key = K_DOWN)
        else:
            event = pygame.event.Event(NOEVENT)
    else:
        event = pygame.event.Event(NOEVENT)
    pygame.event.post(event)
    
def photoShoot(numPhotos):
    image = []
    DISPLAYSURF.fill(BLACK)
    CAMERA.preview_fullscreen = True
##    CAMERA.preview_fullscreen = False
    CAMERA.preview_alpha = preview_alpha
    readySurf, readyRect = makeTextObjs('Preparados...', BIGFONT, WHITE)
    readyRect.midbottom = (WINDOWWIDTH/2,WINDOWHEIGHT/10*9)
    DISPLAYSURF.blit(readySurf, readyRect)
    pygame.display.update()
    time.sleep(3)
    
    for photo in range (0,numPhotos):
        time.sleep(0.1)
        # Count down loop, shows big numbers on the screen
        for i in range (5,0,-1):
            DISPLAYSURF.fill(BLACK)
            numSurf, numRect = makeTextObjs(str(i), HUGEFONT, WHITE)
            numRect.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2- GRID_H_PX)
            DISPLAYSURF.blit(numSurf, numRect)
            numphotosSurf, numphotosRect = makeTextObjs('Foto ' + str(photo+1) + ' de ' + str(numPhotos),BIGFONT,WHITE)
            numphotosRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT - GRID_H_PX * 4)
            DISPLAYSURF.blit(numphotosSurf, numphotosRect)
            pygame.display.update()
            time.sleep(0.7) # each number shows for this amount of time
        # Clear the Screen
        DISPLAYSURF.fill(BLACK)
        takephotoSurf, takephotoRect = makeTextObjs('Capturando foto ' + str(photo+1),BIGFONT,WHITE)
        takephotoRect.midbottom = (WINDOWWIDTH/2,WINDOWHEIGHT/10*9)
        DISPLAYSURF.blit(takephotoSurf, takephotoRect)
        pygame.display.update()
        image.append(takePhoto()) # take the photo
    DISPLAYSURF.fill(BLACK) # clear the screen
    pygame.display.update()
    CAMERA.stop_preview()
    showTextScreen('Fotomaton','Procesando...')

    processPhoto(image)
    #procesarFotos(image)
    
    #printPhoto('/usr/photobooth/print_image.jpg',image)
    CAMERA.resolution = preview_resolution
    CAMERA.preview_fullscreen = False
    CAMERA.start_preview()
    CAMERA.awb_mode = 'auto'
    CAMERA.exposure_mode = 'auto'
    
def processPhoto(photos):
    marco = Image.open(marcosPath +"/marco_motos.jpg")
    img_size = [467,373]
    nombreComposicion = str(time.time())
    composicion = Image.new('RGBA',marco.size,WHITE)
    paste_x = 182
    paste_y = 33

    composicion.paste(marco,(0,0))

    for photo in photos:
        save_name = str(time.time())
        photo.save(rawPath + save_name + '.jpg','JPEG',quality=100)
        resized = photo.resize((img_size[0],img_size[1]),Image.ANTIALIAS)
        composicion.paste(resized,(paste_x,paste_y))
        if paste_x == 182 and paste_y == 33 :
            paste_x = 689
        elif paste_x == 689 and paste_y == 33 :
            paste_x = 182
            paste_y = 529
        else :
            paste_x = 689
            paste_y = 530


    composicion.save(composicionesPath + '/' + nombreComposicion + ".jpg","JPEG",quality=100)
    displayImage(composicionesPath + '/' + nombreComposicion + ".jpg")
    time.sleep(10)

def procesarFotos(fotos):
    ancho_img = 581
    alto_img = 585

    marcoFoto = Image.open(marcosPath + 'pelicula_VERTICAL-GRANDE.jpg')
    separador = Image.open( marcosPath + 'separador.jpg')
    imageComposite_V = Image.new("RGBA", (marcoFoto.size[0], marcoFoto.size[1]), WHITE)
    imageComposite_V.paste(marcoFoto, (0,0))

    vertical_Px = 24
    horizontal_PX = 125

    for foto in fotos:
        save_name = str(time.time())
        foto.save(rawPath + save_name + '.jpg','JPEG',quality=100)
        imageComposite_V.paste(foto.resize([ancho_img,alto_img]), (horizontal_PX,vertical_Px))
        imageComposite_V.paste(separador, (horizontal_PX, vertical_Px + alto_img))
        vertical_Px = vertical_Px + alto_img + separador.size[1]

    imageComposite_V.save( composicionesPath + str(time.time()) + ".jpg","JPEG",quality=100)


##def displayImage(image):
##    image = pygame.transform.scale(pygame.image.load(image),(WINDOWWIDTH,WINDOWHEIGHT))
##    DISPLAYSURF.blit(image,(0,0))
##    pygame.display.update()
    
def takePhoto():
    stream = io.BytesIO() # create an IO stream to save the image to
    GPIO.output(io_cameara_led, True)
    CAMERA.capture(stream,'jpeg',False, None, None,quality=100) # take the picture
    GPIO.output(io_cameara_led, False)
    stream.seek(0) # "rewind" the IO stream
    photo = Image.open(stream) # create a PIL image to pass for processing
    return photo

def idleScreen():
    global thumb_last_sw
    CAMERA.preview_fullscreen = False
    CAMERA.resolution = preview_resolution
    CAMERA.preview_window = (GRID_W_PX * (preview_x + preview_pad),GRID_H_PX * (preview_y + preview_pad),GRID_W_PX * (preview_width - (2 * preview_pad)),GRID_H_PX * (preview_height - (2 * preview_pad)))
    CAMERA.preview_alpha = preview_alpha
    CAMERA.led = False
    DISPLAYSURF.fill(BGCOLOR)

    #Ponemos el fondo que queramos
    background_image = cargar_imagen( marcosPath + 'fondo_fotomaton.jpg', True, False)
    DISPLAYSURF.blit(background_image, (0, 0))
    
    #En este bloque se definen los parametros de la previsualización de la camara
    border = pygame.Surface((GRID_W_PX * preview_width, GRID_H_PX * preview_height))
    border.fill(BLACK)
    borderRect = DISPLAYSURF.blit(border,(GRID_W_PX * preview_x, GRID_H_PX * preview_y))
    startSurf, startRect = makeTextObjs('Dale al botón ROJO', BASICFONT, WHITE)
    startRect.midbottom = (borderRect[2]/2+borderRect[0],borderRect[3]+borderRect[1]-10)
    DISPLAYSURF.blit(startSurf, startRect)
    #titleSurf, titleRect = makeTextObjs('Fotomaton', BIGFONT, GRAY)
    #titleRect.bottomleft = (borderRect[0] + preview_pad * GRID_W_PX ,borderRect[1])
    #DISPLAYSURF.blit(titleSurf, titleRect)

    CAMERA.start_preview()
    CAMERA.awb_mode = 'auto'
    CAMERA.exposure_mode = 'auto'

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

def terminate():
    CAMERA.stop_preview()
    CAMERA.close()
    pygame.quit()

def powerOff():
    CAMERA.stop_preview()
    CAMERA.close()
    showTextScreen('Shutting Down','')
    pygame.quit()
    
def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            powerOff() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

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


def cargar_imagen(filename, transformar=True, transparent=False):
    try: 
        if transformar:
            image = pygame.transform.smoothscale(pygame.image.load(filename).convert(),(WINDOWWIDTH,WINDOWHEIGHT))
        else:
            image = pygame.image.load(filename)
    except pygame.error:
            raise Exception('ERROR AL CARGAR LA IMAGEN')
            raise SystemExit
            
    #image = image.convert()
    if transparent:
            color = image.get_at((0,0))
            image.set_colorkey(color, RLEACCEL)
    return image

def displayImage(rutaImagen):
    image = pygame.transform.scale(pygame.image.load(rutaImagen),(WINDOWWIDTH,WINDOWHEIGHT))
    DISPLAYSURF.blit(image,(0,0))
    pygame.display.update()
    

def setupDisplay():
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

if __name__ == '__main__':
    main()
