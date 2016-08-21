
#Rutas basicas del fotomaton
imgPath = '/home/pi/fotomaton/imagenes/'
marcosPath = '/home/pi/fotomaton/imagenes/marcos/'
composicionesPath = '/home/pi/fotomaton/imagenes/composiciones/'
rawPath = '/home/pi/fotomaton/imagenes/raw/'
thumb_loc = '/home/pi/fotomaton/imagenes/thumb/'


#COLORES
#               R    G    B    A
WHITE       = (255, 255, 255, 255)
GRAY        = (185, 185, 185, 255)
BLACK       = (  0,   0,   0, 255)
DARKBLUE    = (  0,   0, 100, 255)
TEXTSHADOWCOLOR = GRAY
TEXTCOLOR = WHITE
BGCOLOR = DARKBLUE

# font sizes in grid units
basic_font_size    = 4
big_font_size      = 8
huge_font_size     = 50

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
