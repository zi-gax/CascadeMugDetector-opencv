import cv2

# Load cascade classifier
cascade = cv2.CascadeClassifier("cascade/cascade.xml")

if cascade.empty():
    print("Error: Could not load cascade file.")
    exit()

# Open camera (0 = default camera)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    objects = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=50,
        minSize=(60, 60)
    )

    for (x, y, w, h) in objects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Detector", frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
