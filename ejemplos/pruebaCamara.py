from picamera import PiCamera, Color
from time import sleep

camera = PiCamera()

camera.resolution = (800, 600)
##camera.framerate = 15

##camera.rotation = 90

##para hacer que el preview tenga transparencia
camera.start_preview() #(alpha=250)
camera.annotate_background = Color('blue')
camera.annotate_foreground = Color('yellow')
camera.annotate_text_size = 50
camera.image_effect = 'colorswap'
camera.annotate_text = "     FOTON     "
sleep(4)
camera.annotate_text = ""
##camera.capture('/home/pi/fotomaton/src/pruebasCamara/max.jpg')
camera.stop_preview()


##efectosCamera = ['negative', 'solarize', 'sketch', 'denoise', 'emboss', 'oilpaint', 'hatch', 'gpen', 'pastel', 'watercolor', 'film', 'blur', 'saturation', 'colorswap', 'washedout', 'posterise', 'colorpoint', 'colorbalance', 'cartoon', 'deinterlace1', 'deinterlace2']

##camera.start_preview()
##for  effect in camera.IMAGE_EFFECTS:
##    camera.annotate_text = "Efecto de la foto: %s " % effect
##    camera.image_effect = effect
##    sleep(2)

camera.image_effect = 'none'

camera.start_preview()

for  modo in camera.AWB_MODES:
    camera.annotate_text = "Modo de la foto: %s " % modo
    camera.awb_mode = modo
    sleep(2)

camera.awb_mode = 'off'

for expo in camera.EXPOSURE_MODES:
    camera.annotate_text = "Exposicion de la foto: %s " % expo
    camera.exposure_mode = expo
    
camera.stop_preview()




