import cv2
import time

capture = cv2.VideoCapture(0)

k = 0
fps = 0.0
kfps = 0

while True:
    start = time.time()
    ret, frame = capture.read()
    end = time.time()
    k = k + 1
    if k > 20:
        kfps = fps * 20
        k = 0
        fps = 0
    elif k != 0 and k <= 20:
        fps = (fps + (1.0 / (end - start))) / k
    cv2.putText(frame, '{} fps'.format(round(kfps, 2)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()