from twython import Twython
from authTwitter import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

message = "Prueba para crear un Tweet desde python!"
twitter.update_status(status=message)
print("Tweeted: %s" % message)

message = "Prueba para crear un Tweet con imagen desde python!"
with open('C:/Users/gbelloca/Pictures/Cargas de cámara/2012-01-16 15.19.56-2.jpg', 'rb') as photo:
    twitter.update_status_with_media(status=message, media=photo)