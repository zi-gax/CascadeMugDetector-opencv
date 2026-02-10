import cv2

cascade = cv2.CascadeClassifier(
    r"C:\Users\khode\Desktop\CascadeMugDetector-opencv\cascade\cascade.xml"
)

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    objects = cascade.detectMultiScale(
        gray,
        scaleFactor=1.35,
        minNeighbors=20,
        minSize=(20,20)
    )

    for (x, y, w, h) in objects:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("Detector", frame)
    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
