import os
 
# Setteamos el directorio raiz a la variable rootDir
# En realidad la variable se puede llamar como sea :)
 
rootDir = '/home/pi/fotomaton/imagenes/raw'
for dirName, subdirList, fileList in os.walk(rootDir):
    print('Directorio encontrado: %s' % dirName)
    for fname in fileList:
        print('\t%s' % fname)