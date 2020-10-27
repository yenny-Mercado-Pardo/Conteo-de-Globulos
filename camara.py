import cv2
link = "http://192.168.0.3:8080/video"
cap = cv2.VideoCapture(link)

while(True):
    ret, frame = cap.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break