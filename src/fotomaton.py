import numpy as np
import picamera
import time
import datetime
import PIL
from PIL import Image

imgPath = '/home/pi/fotomaton/imagenes'
composicionesPath = '/home/pi/fotomaton/composiciones'

##-------------------------------------------------------------------------

def sacarFotos(nombreFotos):
    with picamera.PiCamera() as cam:
        counter = 0
        for each in range(4):
            counter = counter + 1
            cam.start_preview()
            if counter == 1: #length of preview time for first picture
                time.sleep(1)
            if counter > 1: #length of preview time for pictures 2-4
                time.sleep(5)
            nombreFoto = imgPath + '/image' + str(datetime.datetime.now()) + '.jpg'
            print(nombreFoto)
            cam.capture(nombreFoto)
            nombreFotos.append(nombreFoto)
            cam.stop_preview()
    

##-------------------------------------------------------------------------

list_im = list()
sacarFotos(list_im)


imgs    = [ Image.open(i) for i in list_im ]
# pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]

imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
imgs_comb = Image.fromarray( imgs_comb)

# Creo una imagen para hacer la composicion
marcaAgua = Image.open(imgPath + '/mask_H.png')
imgH = round((imgs_comb.size[1] + marcaAgua.size[1]) * 1.1)
imgW = imgs_comb.size[0]
imageComposite_H = Image.new("RGBA", (imgW, imgH), 'white')
imageComposite_H.paste(imgs_comb, (0,0)) #each image is offset 200px to account for boarder
imageComposite_H.paste(marcaAgua, (imgW // 2 - marcaAgua.size[0] //2, round(imgs_comb.size[1] * 1.05)))
imageComposite_H.save( composicionesPath + '/composicionHorizontal.png' )



# for a vertical stacking it is simple: use vstack
imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
imgs_comb = Image.fromarray( imgs_comb)

marcaAgua_V = Image.open(imgPath + '/mask_V.png')

imgH = imgs_comb.size[1]
if(imgH < marcaAgua_V.size[1]):
    imgH = marcaAgua_V.size[1]

imgW = round((imgs_comb.size[0] + marcaAgua_V.size[0]) * 1.1)
imageComposite_V = Image.new("RGBA", (imgW, imgH), 'white')
imageComposite_V.paste(marcaAgua_V, (0,0))
imageComposite_V.paste(imgs_comb, (round(marcaAgua_V.size[0] * 1.05), imgH // 2 - imgs_comb.size[1] //2))
imageComposite_V.save( composicionesPath + '/composicionVertical.png')
         


print('FINALIZADO')
