# ============================================================
#  modules/register_student.py
#  Registers a new student and captures face samples
# ============================================================

import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FACE_CASCADE_PATH, SAMPLES_PER_STUDENT, IMAGES_PATH
from modules.database import execute_query


def register_student(name, roll_no, class_name, email, phone, progress_callback=None):
    """
    1. Save student record to DB
    2. Capture SAMPLES_PER_STUDENT face images from webcam
    3. Save images to data/student_images/<student_id>/
    Returns: (success: bool, message: str)
    """

    # ── Step 1: Check for duplicate roll number ──────────────
    existing = execute_query(
        "SELECT student_id FROM students WHERE roll_no = %s",
        (roll_no,), fetch=True
    )
    if existing:
        return False, f"Roll No {roll_no} is already registered!"

    # ── Step 2: Insert student into database ─────────────────
    student_id = execute_query(
        "INSERT INTO students (name, roll_no, class, email, phone, image_path) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (name, roll_no, class_name, email, phone, "")
    )
    if not student_id:
        return False, "Failed to save student to database."

    # ── Step 3: Create image folder ──────────────────────────
    folder = os.path.join(IMAGES_PATH, str(student_id))
    os.makedirs(folder, exist_ok=True)

    # ── Step 4: Update image_path in DB ──────────────────────
    execute_query(
        "UPDATE students SET image_path = %s WHERE student_id = %s",
        (folder, student_id)
    )

    # ── Step 5: Capture face samples from webcam ─────────────
    face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + FACE_CASCADE_PATH
)

    print("Cascade file:", cv2.data.haarcascades + FACE_CASCADE_PATH)
    print("Cascade loaded:", not face_cascade.empty())

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return False, "Cannot access webcam. Check connection."

    print("Webcam opened successfully.")
    count = 0
    print(f"[INFO] Capturing {SAMPLES_PER_STUDENT} face samples for {name}...")

    while count < SAMPLES_PER_STUDENT:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
           
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
        )

        print("Faces detected:", len(faces))
        

        for (x, y, w, h) in faces:
    
        
            count += 1
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            img_path = os.path.join(folder, f"{count}.jpg")
            cv2.imwrite(img_path, face_img)
            print("Saved image:", img_path)

            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 0), 2)
            cv2.putText(frame, f"Captured: {count}/{SAMPLES_PER_STUDENT}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)

            if progress_callback:
                progress_callback(count)

            if count >= SAMPLES_PER_STUDENT:
                break

        # Show preview window
        cv2.putText(frame, f"Registering: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, "Press Q to cancel", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imshow("Face Registration", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if count < SAMPLES_PER_STUDENT:
        return False, f"Only {count} samples captured. Registration incomplete."

    print(f"[OK] {count} face samples saved for {name} (ID: {student_id})")
    return True, f"Student '{name}' registered successfully with ID {student_id}!"


def get_all_students():
    """Return all registered students from DB."""
    return execute_query(
        "SELECT student_id, name, roll_no, class, email, phone, registered_on "
        "FROM students ORDER BY registered_on DESC",
        fetch=True
    ) or []


def delete_student(student_id):
    """Delete student record and their face images."""
    import shutil
    student = execute_query(
        "SELECT image_path FROM students WHERE student_id = %s",
        (student_id,), fetch=True
    )
    if student and student[0]["image_path"]:
        folder = student[0]["image_path"]
        if os.path.exists(folder):
            shutil.rmtree(folder)

    execute_query(
        "DELETE FROM students WHERE student_id = %s", (student_id,)
    )
    return True
