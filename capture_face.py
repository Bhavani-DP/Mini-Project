import cv2
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Output directory inside your Django MEDIA_ROOT
output_dir = os.path.join("media", "faces")
os.makedirs(output_dir, exist_ok=True)

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Open webcam
cap = cv2.VideoCapture(0)

print("Press 'c' to capture face, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to access camera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Capture Face", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):  # capture
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = frame[y:y+h, x:x+w]
            filename = f"face_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, face)
            print(f"Saved face image: {filepath}")
            # Display the captured face
            cv2.imshow("Captured Face", face)
            cv2.waitKey(2000)  # Display for 2 seconds
            cv2.destroyWindow("Captured Face")
        else:
            print("No face detected. Try again.")
    elif key == ord("q"):  # quit
        break

cap.release()
cv2.destroyAllWindows()