#!/usr/bin/python
from __future__ import division
import os, pygame, time, picamera, io, sys, Image, shutil#, cups
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
BGCOLOR = DARKBLUE

# printout size
print_2x6 = False
print_2up = False
print_width = 2 if print_2x6 else 6 #inches
print_height = 6 if print_2x6 else 4 #inches
print_w_dpi = 330
print_h_dpi = 330
print_size = (print_width * print_w_dpi, print_height * print_h_dpi)

#printer
printer_name = "Sony_UP-DR200"
printer_copies = 1

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
thumb_strip_width  = 20
thumb_strip_height = grid_height
thumb_photo_width  = thumb_strip_width - 2 * thumb_strip_pad
thumb_photo_height = thumb_photo_width * 3 / 4

# font sizes in grid units
basic_font_size    = 4
big_font_size      = 8
huge_font_size     = 50

thumb_size = (400,300)
thumb_time = 2
thumb_last_sw = 0
thumb_index = 1
thumb_loc = '/usr/photobooth/photos_thumb/'
thumb_strip = []

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
    WINDOWWIDTH = pygame.display.Info().current_w
    GRID_W_PX   = int(WINDOWWIDTH / grid_width)
    WINDOWHEIGHT = pygame.display.Info().current_h
    GRID_H_PX    = int(WINDOWHEIGHT / grid_height)
    FPSCLOCK = pygame.time.Clock()
    pygame.mouse.set_visible(False) #hide the mouse cursor
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN, 32)
    BASICFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * basic_font_size))
    BIGFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * big_font_size))
    HUGEFONT = pygame.font.Font('freesansbold.ttf', int(GRID_H_PX * huge_font_size))
    pygame.display.set_caption('Photobooth')
    
    CAMERA = picamera.PiCamera()
    CAMERA.drc_strength = ('medium')
    showTextScreen('Photobooth','Loading...')

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
                print(event.key)
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
    CAMERA.preview_alpha = preview_alpha
    readySurf, readyRect = makeTextObjs('Get Ready', BIGFONT, WHITE)
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
            numphotosSurf, numphotosRect = makeTextObjs('Taking Photo ' + str(photo+1) + ' of ' + str(numPhotos),BIGFONT,WHITE)
            numphotosRect.midbottom = (WINDOWWIDTH / 2, WINDOWHEIGHT - GRID_H_PX * 4)
            DISPLAYSURF.blit(numphotosSurf, numphotosRect)
            pygame.display.update()
            time.sleep(0.7) # each number shows for this amount of time
        # Clear the Screen
        DISPLAYSURF.fill(BLACK)
        takephotoSurf, takephotoRect = makeTextObjs('Taking Photo ' + str(photo+1),BIGFONT,WHITE)
        takephotoRect.midbottom = (WINDOWWIDTH/2,WINDOWHEIGHT/10*9)
        DISPLAYSURF.blit(takephotoSurf, takephotoRect)
        pygame.display.update()
        image.append(takePhoto()) # take the photo
    DISPLAYSURF.fill(BLACK) # clear the screen
    pygame.display.update()
    CAMERA.stop_preview()
    showTextScreen('Photobooth','Processing...')
    processPhoto(image)
    printPhoto('/usr/photobooth/print_image.jpg',image)
    CAMERA.resolution = preview_resolution
    CAMERA.preview_fullscreen = False
    CAMERA.start_preview()
    
def processPhoto(photos):
    save_name = str(time.time())
    montage = Image.new('RGBA',print_size,WHITE)
    paste_x = 0
    paste_y = 0
    if print_2x6 :
        for photo in photos:
            photo_w = print_size[0]
            photo_h = int(photo_w * (photo.size[1] / photo.size[0]))
            resized = photo.resize((photo_w,photo_h),Image.ANTIALIAS)
            montage.paste(resized,(0,paste_y))
            paste_y += photo_h
    else:
        for photo in photos:
            photo.save('/usr/photobooth/raw_images/'+save_name+'-'+str(paste_x)+str(paste_y)+'.jpg','JPEG',quality=80)
            photo_h = int(print_size[1]/2)
            photo_w = int(photo_h * (photo.size[0] / photo.size[1]))-10
            resized = photo.resize((photo_w,photo_h),Image.ANTIALIAS)
            montage.paste(resized,(paste_x+20,paste_y))
            if paste_x == 0 and paste_y == 0 :
                paste_x = photo_w
            elif paste_x > 0 and paste_y == 0 :
                paste_x = 0
                paste_y = photo_h
            else :
                paste_x = photo_w
                paste_y = photo_h
        logo = Image.open("/usr/photobooth/4x6_logo.jpg")
        montage.paste(logo,(print_size[0]-220-20,0))
    montage.save("/usr/photobooth/print_image.jpg","JPEG",quality=100)
    #shutil.copyfile("/usr/photobooth/print_image.jpg","/usr/photobooth/montages/" + str(time.time()) + ".jpg")
    
def printPhoto(photo,photos):
    #printer_conn = cups.Connection()
    #################################################################################
    #printer_conn.printFile(printer_name, photo, "PhotoBooth",{"copies": str(printer_copies)})
    #displayImage(photo)
    #time.sleep(10)
    #updateThumb(photos[0])
    #showTextScreen('Printing',str(printer_copies) + ' copies')
    time.sleep(5)

def displayImage(image):
    image = pygame.transform.scale(pygame.image.load(image),(WINDOWWIDTH,WINDOWHEIGHT))
    DISPLAYSURF.blit(image,(0,0))
    pygame.display.update()
    
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
    border = pygame.Surface((GRID_W_PX * preview_width, GRID_H_PX * preview_height))
    border.fill(BLACK)
    borderRect = DISPLAYSURF.blit(border,(GRID_W_PX * preview_x, GRID_H_PX * preview_y))
    startSurf, startRect = makeTextObjs('Press Start', BASICFONT, WHITE)
    startRect.midbottom = (borderRect[2]/2+borderRect[0],borderRect[3]+borderRect[1]-10)
    DISPLAYSURF.blit(startSurf, startRect)
    titleSurf, titleRect = makeTextObjs('Photobooth', BIGFONT, GRAY)
    titleRect.bottomleft = (borderRect[0] + preview_pad * GRID_W_PX ,borderRect[1])
    DISPLAYSURF.blit(titleSurf, titleRect)
    CAMERA.start_preview()
    pygame.display.update()
    thumb_last_sw = 0
    while not pygame.event.peek(KEYDOWN):
        pygame.display.update(filmStrip())
        FPSCLOCK.tick(FPS)

def filmStrip():
    global thumb_index, thumb_last_sw
    if time.time() - thumb_time> thumb_last_sw:
        thumb_last_sw = time.time()
        strip = pygame.Surface((thumb_strip_width * GRID_W_PX, thumb_strip_height * GRID_H_PX),pygame.SRCALPHA)
        strip.fill(BLACK)
        thumb_h_pos = (thumb_photo_height + thumb_strip_pad) * GRID_H_PX
        thumb_index += 1
        for i in range (0,8):
            strip.blit(thumb_strip[i],(thumb_strip_pad * GRID_W_PX,((thumb_index+i)%8)*thumb_h_pos))
        return DISPLAYSURF.blit(strip,(GRID_W_PX * thumb_strip_x, GRID_H_PX * thumb_strip_y))

def updateThumb(image):
    global thumb_strip
    thumb_size = (int(thumb_photo_width * GRID_W_PX), int(thumb_photo_height * GRID_H_PX))
    for i in range (7,0,-1):
        try:
            thumb_strip[i] = thumb_strip[i - 1]
        except:
            thumb_strip[i] = pygame.Surface(thumb_size)
            thumb_strip[i].fill(blank_thumb)
        try:
            os.rename(thumb_loc+str(i)+'.jpg',thumb_loc+str(i+1)+'.jpg')
        except:
            continue
    image.save(thumb_loc+str(1)+'.jpg')
#    photo_edit = pgmagick.Image(image)
#    photo_edit.quality(100)
#    photo_edit.scale(str(thumb_size[0])+'x'+str(thumb_size[1]))
#    photo_edit.write(thumb_loc+'1.jpg')
    thumb_strip[0] = pygame.image.load(thumb_loc+str(1)+'.jpg').convert()
    thumb_strip[0] = pygame.transform.smoothscale(thumb_strip[0],thumb_size)
        
def loadThumbs():
    global thumb_strip
    thumb_size = (int(thumb_photo_width * GRID_W_PX), int(thumb_photo_height * GRID_H_PX))
    for i in range (0,8):
        try:
            thumb_strip.append(pygame.image.load(thumb_loc+str(i+1)+'.jpg').convert())
            thumb_strip[i] = pygame.transform.smoothscale(thumb_strip[i],thumb_size)
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
    sys.exit()

def powerOff():
    CAMERA.stop_preview()
    CAMERA.close()
    showTextScreen('Shutting Down','')
    pygame.quit()
    os.system('poweroff')
    sys.exit()
    
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

def setupDisplay():
    #disp_no = os.getenv("DISPLAY")
    #if disp_no:
        #print "I'm running under X display = {0}".format(disp_no)
    
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
            #print pygame.error
            #print 'Driver: {0} failed.'.format(driver)
            continue
        found = True
        break

    if not found:
        raise Exception('No suitable video driver found!')

if __name__ == '__main__':
    main()
