import imagezmq
import cv2
import socket
import time
import imutils
import numpy as np

img = cv2.imread('rpi1.jpg')

ADDR = '*'
PORT = 3234

SERVER_ADDR = 'localhost'   # Bu yerga server_hub_zmq.py ishga tushurilgan kompyuter ip manzili kiritilsin.
SERVER_PORT = 2345

imgsender = imagezmq.ImageSender(connect_to='tcp://{}:{}'.format(SERVER_ADDR, SERVER_PORT), REQ_REP=True)
imgreader = imagezmq.ImageHub(open_port='tcp://{}:{}'.format(ADDR, PORT), REQ_REP=True)
dev_name = socket.gethostname()
dev_addr = socket.gethostbyname(dev_name)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]


print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt', 'MobileNetSSD_deploy.caffemodel')

CONSIDER = set(["dog", "person", "car"])
objCount = {obj: 0 for obj in CONSIDER}
frameDict = {}

ESTIMATED_NUM_PIS = 4
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

print("[INFO] detecting: {}...".format(", ".join(obj for obj in CONSIDER)))

data_addr = dev_addr + ':' + str(PORT)
print('{}: {}'.format(dev_name, data_addr))
imgsender.send_image(data_addr, img)

k = 0

while True:
    data, frame = imgreader.recv_image()
    imgreader.send_reply()
    k = k + 1
    print ('{} - from ImageHub'.format(k))
    if data == 'exit':
        imgsender.send_image('exit', frame)
        break
    
    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)    

    net.setInput(blob)
    detections = net.forward()
    
    objCount = {obj: 0 for obj in CONSIDER}
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.2:
            idx = int(detections[0, 0, i, 1])
            if CLASSES[idx] in CONSIDER:
                objCount[CLASSES[idx]] += 1
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
    
    label = ", ".join("{}: {}".format(obj, count) for (obj, count) in objCount.items())
    cv2.putText(frame, label, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)
    
    imgsender.send_image(dev_name, frame)

print ('Shutting down...')
