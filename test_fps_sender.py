import time
import socket
import imagezmq

ImageSender = imagezmq.ImageSender(connect_to='tcp://localhost:1234', REQ_REP=True)
ImageHub = imagezmq.ImageHub('tcp://*:2134', REQ_REP=True)

while True:
    msg, frame = ImageHub.recv_image()
    ImageHub.send_reply()
    ImageSender.send_image(msg, frame)
    if (msg == 'exit'):
        ImageSender.send_image(msg, frame)
        break

print ('Shutting down...')