# ============================================================
#  modules/recognize_face.py
#  Real-time face detection and recognition using webcam
# ============================================================

import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FACE_CASCADE_PATH, FACE_CONFIDENCE_THRESHOLD, MODEL_PATH
from modules.database    import execute_query
from modules.attendance_manager import mark_attendance


def load_model():
    """Load trained LBPH model. Returns recognizer or None."""
    if not os.path.exists(MODEL_PATH):
        print("[ERROR] Model not found. Please train the model first.")
        return None
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)
    return recognizer


def get_student_name(student_id):
    """Fetch student name from DB by ID."""
    result = execute_query(
        "SELECT name, roll_no FROM students WHERE student_id = %s",
        (student_id,), fetch=True
    )
    if result:
        return result[0]["name"], result[0]["roll_no"]
    return "Unknown", ""


def start_recognition(subject_id, on_recognized=None, stop_event=None):
    """
    Opens webcam, detects and recognizes faces in real-time.
    Marks attendance automatically for recognized students.

    subject_id     : which subject session is active
    on_recognized  : callback(name, roll_no, student_id) called on each new recognition
    stop_event     : threading.Event — set it to stop the loop externally
    """

    recognizer   = load_model()
    if not recognizer:
        return False, "Model not loaded."

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + FACE_CASCADE_PATH
    )
    cap          = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Webcam not accessible."

    marked_today = set()   # avoid duplicate marks in same session
    print("[INFO] Recognition started. Press Q to stop.")

    while True:
        if stop_event and stop_event.is_set():
            break

        ret, frame = cap.read()
        if not ret:
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Enhance contrast for low-light rooms
        gray  = cv2.equalizeHist(gray)

        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))

            student_id, confidence = recognizer.predict(face_roi)
            confidence_pct = round(100 - confidence, 1)

            if confidence < FACE_CONFIDENCE_THRESHOLD:
                # ── Recognized ───────────────────────────────
                name, roll_no = get_student_name(student_id)
                color         = (0, 200, 0)   # green

                if student_id not in marked_today:
                    success = mark_attendance(student_id, subject_id)
                    if success:
                        marked_today.add(student_id)
                        print(f"[MARKED] {name} ({roll_no}) — {confidence_pct}% match")
                        if on_recognized:
                            on_recognized(name, roll_no, student_id)

                label = f"{name}  {confidence_pct}%"
            else:
                # ── Unknown ───────────────────────────────────
                label  = "Unknown"
                color  = (0, 0, 255)   # red

            # Draw bounding box and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-32), (x+w, y), color, -1)
            cv2.putText(frame, label, (x+4, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # Status bar
        cv2.putText(frame,
                    f"Marked: {len(marked_today)} student(s)  |  Press Q to stop",
                    (10, frame.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Smart Attendance — Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[DONE] Session ended. Total marked: {len(marked_today)}")
    return True, f"Session complete. {len(marked_today)} student(s) marked present."
