import PIL
from PIL import Image

imgPath = '/home/pi/fotomaton/imagenes/thumb'
marcosPath = '/home/pi/fotomaton/imagenes/marcos'
composicionesPath = '/home/pi/fotomaton/imagenes/composiciones'

ancho_img = 581
alto_img = 584

list_im = [imgPath + '/1.jpg', imgPath + '/2.jpg', imgPath + '/3.jpg', imgPath + '/4.jpg']
imgs    = [ Image.open(i) for i in list_im ]

separador = Image.open( marcosPath + '/separador.jpg')
separador = separador.resize([582,separador.size[1]])
##separador.save( marcosPath + '/composicionVertical.jpg')

marcaAgua_V = Image.open(marcosPath + '/pelicula_VERTICAL-GRANDE.jpg')

imageComposite_V = Image.new("RGBA", (marcaAgua_V.size[0], marcaAgua_V.size[1]), 'white')
imageComposite_V.paste(marcaAgua_V, (0,0))

i = 24
for imagen in imgs:
    imageComposite_V.paste(imagen.resize([ancho_img,alto_img]), (125,i))
    imageComposite_V.paste(separador, (125, i + alto_img))
    i = i + alto_img + separador.size[1]

imageComposite_V.save( composicionesPath + '/composicionVertical.jpg')

print('FINALIZADO')
