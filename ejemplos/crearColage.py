import time
import PIL
from PIL import Image

imgPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/raw'
composicionesPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/composiciones'
marcosPath = 'D:/Descargas/RaspBerry/proyectos_Python/Fotomaton/imagenes/marcos'

#marco = Image.open(marcosPath +"/marco_motos.jpg")
#
#print_size = [467,373]
#nombreComposicion = str(time.time())
#composicion = Image.new('RGBA',marco.size,"white")
#paste_x = 182
#paste_y = 33
#
#imgs = [imgPath + '/1.jpg', imgPath + '/2.jpg', imgPath + '/3.jpg', imgPath + '/4.jpg']
#photos    = [ Image.open(i) for i in imgs ]
#
#composicion.paste(marco,(0,0))
#
#for photo in photos:
#
#    resized = photo.resize((print_size[0],print_size[1]),Image.ANTIALIAS)
#    composicion.paste(resized,(paste_x,paste_y))
#    if paste_x == 182 and paste_y == 33 :
#        paste_x = 689
#    elif paste_x == 689 and paste_y == 33 :
#        paste_x = 182
#        paste_y = 529
#    else :
#        paste_x = 689
#        paste_y = 530


marco = Image.open(marcosPath +"/marco_motos_polaroid.jpg")

img_size = [781, 827]
nombreComposicion = 'POLAROID'
paste_x = 107
paste_y = 127

photo = Image.open(imgPath + '/1.png')

resized = photo.resize((img_size[0],img_size[1]),Image.ANTIALIAS)
marco.paste(resized,(paste_x,paste_y))


marco.save(composicionesPath + '/' + nombreComposicion + ".jpg","JPEG",quality=100)


print('FINALIZADO')
