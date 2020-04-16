import cv2
import imagezmq
import socket
import time
from threading import Thread, Lock

ADDR = '*'      # mana shu dastur ishga tushirilayotgan kompyuter ip manzili kiritiladi
PORT = 2345

imgHub = imagezmq.ImageHub(open_port='tcp://*:2345'.format(PORT), REQ_REP=True)
print('Create server: tcp://{}:{}'.format(socket.gethostbyname(socket.gethostname()), PORT))

capture = cv2.VideoCapture(0)
dev_name = socket.gethostname()
dev_addr = socket.gethostbyname(dev_name)

SENDERS_COUNT = 2

clist = []

while True:
    data, img = imgHub.recv_image()
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
    Imagesenders.append(imagezmq.ImageSender('tcp://{}'.format(cli)))

print ('Connected {} devices: {}'.format(len(clist), len(Imagesenders)))

for k in range(len(clist)):    
    print ('Sender[{}]: '.format(k), Imagesenders[k].get_info())

def view_recvs ():
    print ('Start thread.')
    k = 0
    while True:
        start = time.time()
        (name, frame) = imgHub.recv_image()
        imgHub.send_reply(b'OK')
        if (name == 'exit'):
            break
        k = k + 1
        end = time.time()
        fps = round(1.0 / (end - start), 2)
        print ('{}: Read from <<< {}. {} fps'.format(k, name, fps))
        cv2.imshow('From network', frame)
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

    print ('Shutting down...')
    capture.release()

if __name__ == "__main__":
    main()
