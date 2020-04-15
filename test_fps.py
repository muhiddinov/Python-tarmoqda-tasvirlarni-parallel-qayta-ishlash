import cv2
import time
import imagezmq
import socket
import threading

ImageHub = imagezmq.ImageHub(open_port='tcp://*:1234', REQ_REP=True)
ImageSender = imagezmq.ImageSender(connect_to='tcp://192.168.43.89:2134', REQ_REP=True)
capture = cv2.VideoCapture(0)

def zmq_hendle():
    print ('Start threading...')
    while True:
        start = time.time()
        msg, frame = ImageHub.recv_image()
        
        if (msg == 'exit'):
            break
        
        ImageHub.send_reply()
        end = time.time()
        time_span = end - start
        print ("Frame per second: {}".format(1.0/time_span))
    print ('Shutting down...')

def main():
    thread1 = threading.Thread(target=zmq_hendle)
    thread1.start()
    while True:
        ret, frame = capture.read()
        ImageSender.send_image('main', frame)
        cv2.imshow('Main', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            ImageSender.send_image('exit', frame)
            break
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()    