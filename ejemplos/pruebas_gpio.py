from gpiozero import LED, Button
from time import sleep
from signal import pause
from picamera import PiCamera
import random

led = LED(17)
button = Button(4)

efectosCamera = ['negative', 'solarize', 'sketch', 'denoise',
                 'emboss', 'oilpaint', 'hatch', 'gpen', 'pastel',
                 'watercolor', 'film', 'blur', 'saturation',
                 'colorswap', 'washedout', 'posterise',
                 'colorpoint', 'colorbalance', 'cartoon',
                 'deinterlace1', 'deinterlace2']


with PiCamera() as camera:
    camera.start_preview()
    frame = 0
    while True:
        button.wait_for_press()
        camera.image_effect = efectosCamera[frame]
        if(frame == 20):
            exit
        else:
            frame += 1
