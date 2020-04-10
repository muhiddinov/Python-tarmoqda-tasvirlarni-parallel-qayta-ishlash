import cv2
import imagezmq
import socket
import time
from threading import Thread, Lock

imgHub = imagezmq.ImageHub(open_port='tcp://*:2345', REQ_REP=True)
print('Create server: tcp://{}:2345'.format(socket.gethostbyname(socket.gethostname())))

capture = cv2.VideoCapture(0)
dev_name = socket.gethostname()
dev_addr = socket.gethostbyname(dev_name)

SENDERS_COUNT = 2

clist = []

while True:
    data, img = imgHub.recv_image()
    print (data)
    imgHub.send_reply()

    if len(clist) == 0:
        clist.append(data)
    else:
        for cli in clist:
            if data != cli:
                clist.append(data)

    if len(clist) >= SENDERS_COUNT:
        break

Imagesenders = []

for cli in clist:
    print('\t->{}'.format(cli))
    Imagesenders.append(imagezmq.ImageSender('tcp://{}:21567'.format(cli)))

print ('Connected {} devices: {}'.format(len(clist), len(Imagesenders)))

for k in range(len(clist)):    
    print ('Sender[{}]: %s'.format(k), Imagesenders[k].get_info())


print ('Have been sended message and image')

img2sender = None

def view_recvs ():
    print ('Start thread.')
    k = 0
    while True:
        (name, frame) = imgHub.recv_image()
        imgHub.send_reply(b'OK')
        k = k + 1
        print ('{}: Read from <<< {}.'.format(k, name))
        cv2.imshow('Image parallel processing on network', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def main():
    thread1 = Thread(target=view_recvs)
    thread1.start()
    sender_m = 0
    ret, img2sender = capture.read()
    while True:
        ret, img = capture.read()
        Imagesenders[sender_m].send_image(dev_name, img)
        sender_m = sender_m + 1
        sender_m = sender_m % SENDERS_COUNT
    for k in range (SENDERS_COUNT):
        print ('Send (exit) message to sender: {}'.format(Imagesenders[k].get_info()))
    print ('Shutting down...')
    thread1._stop()

if __name__ == "__main__":
    main()
