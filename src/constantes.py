'''
Created on 30 de ago. de 2016

@author: gbelloca
'''

#Rutas basicas del fotomaton
imgPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/raw/'
composicionesPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/composiciones/'
marcosPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/marcos/'
thumb_loc = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/thumb/'
rawPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/raw/'


FPS = 25

#COLORES
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

thumb_size = (400,300)
thumb_time = 2
thumb_last_sw = 0
thumb_index = 1
thumb_strip = []
thumb_files_number = 0

# font sizes in grid units
basic_font_size    = 4
big_font_size      = 8
huge_font_size     = 50

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
