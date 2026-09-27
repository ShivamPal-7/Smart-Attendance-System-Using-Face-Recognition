import cv2

print("Starting live camera test...")

camera_index = 0

cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("[ERROR] Camera could not be opened.")
    exit()

print("[OK] Camera opened successfully.")
print("Press Q or ESC to close the camera.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("[ERROR] Could not read frame.")
        break

    # Show live camera
    cv2.imshow("Live Camera Test", frame)

    # Wait 1 millisecond for keyboard input
    key = cv2.waitKey(1) & 0xFF

    # Press Q or ESC to exit
    if key == ord("q") or key == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("Camera test completed.")