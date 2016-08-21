# Copyright (c) 2011, Xabier (slok) Larrakoetxea
# Copyright (c) 2011, Iraide (Sharem) Diaz
#
# 3 clause/New BSD license: 
#   opensource: http://www.opensource.org/licenses/BSD-3-Clause
#   wikipedia: http://en.wikipedia.org/wiki/BSD_licenses
#
#-----------------------------------------------------------------------
# This script  allows to upload to Fileserve with FTP various files at the same time
#
# Use:
#   python ./ftpFilserveUploader.py ./Downloads/xxx.y ./yyyy.z  /home/xxx/yyyy.zz
#
from ftplib import FTP
import pysftp
import os


########### DATOS ACCESO ########################

USER = 'guilleserver'
PASS = 'Gbc2015Gbc'

########### MODIFY IF YOU WANT ############

SERVER = '192.168.1.103'
PORT = 22
BINARY_STORE = True # if False then line store (not valid for binary files (videos, music, photos...))

###########################################

srv = pysftp.Connection(host=SERVER, port=PORT, username=USER, password=PASS, private_key='None')

# Get the directory and file listing
data = srv.listdir()

# Closes the connection
srv.close()

# Prints out the directories and files, line by line
for i in data:
    print (i)
