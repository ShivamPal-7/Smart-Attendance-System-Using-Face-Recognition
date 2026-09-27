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
    Register student and capture face samples.
    """

    # ---------------------------------------------------------
    # 1. Check duplicate roll number
    # ---------------------------------------------------------
    existing = execute_query(
        "SELECT student_id FROM students WHERE roll_no = %s",
        (roll_no,),
        fetch=True
    )

    if existing:
        return False, f"Roll No {roll_no} is already registered!"

    # ---------------------------------------------------------
    # 2. Insert student into database
    # ---------------------------------------------------------
    student_id = execute_query(
        "INSERT INTO students "
        "(name, roll_no, class, email, phone, image_path) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (name, roll_no, class_name, email, phone, "")
    )

    if not student_id:
        return False, "Failed to save student to database."

    # ---------------------------------------------------------
    # 3. Create image folder
    # ---------------------------------------------------------
    folder = os.path.join(IMAGES_PATH, str(student_id))
    os.makedirs(folder, exist_ok=True)

    print("=" * 60)
    print("[INFO] Student ID:", student_id)
    print("[INFO] Image folder:", folder)

    # ---------------------------------------------------------
    # 4. Update image_path in database
    # ---------------------------------------------------------
    execute_query(
        "UPDATE students SET image_path = %s WHERE student_id = %s",
        (folder, student_id)
    )

    # ---------------------------------------------------------
    # 5. Load Haar Cascade
    # ---------------------------------------------------------
    cascade_path = os.path.join(
        cv2.data.haarcascades,
        "haarcascade_frontalface_default.xml"
    )

    print("[INFO] Cascade path:", cascade_path)

    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        print("[ERROR] Face detection model could not be loaded.")
        return False, "Face detection model could not be loaded."

    print("[OK] Face detection model loaded.")
   
    # ---------------------------------------------------------
    # 6. Open webcam
    # ---------------------------------------------------------
    print("[INFO] Opening webcam...")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERROR] Webcam could not be opened.")
        return False, "Cannot access webcam."

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[OK] Webcam opened successfully.")

    # ---------------------------------------------------------
    # 7. Capture face samples
    # ---------------------------------------------------------
    count = 0

    print(
        f"[INFO] Capturing {SAMPLES_PER_STUDENT} "
        f"face samples for {name}"
    )

    while count < SAMPLES_PER_STUDENT:

        print("[INFO] Reading camera frame...")

        ret, frame = cap.read()

        print("[INFO] Frame received:", ret)

        if not ret:
            print("[ERROR] Could not read frame.")
            continue

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        print("[INFO] Faces detected:", len(faces))

        # Display number of detected faces
        cv2.putText(
            frame,
            f"Faces detected: {len(faces)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        for (x, y, w, h) in faces:

            # Extract face
            face_img = gray[y:y + h, x:x + w]

            # Resize for LBPH training
            face_img = cv2.resize(face_img, (200, 200))

            count += 1

            # Image filename
            img_path = os.path.join(
                folder,
                f"{count}.jpg"
            )

            # Save image
            print("[INFO] Saving to:", img_path)

            saved = cv2.imwrite(
                img_path,
                face_img
            )

            if saved:
                print("[OK] Saved image:", img_path)
            else:
                print("[ERROR] Failed to save:", img_path)
                count -= 1
                continue

            # Draw rectangle
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            # Capture counter
            cv2.putText(
                frame,
                f"Captured: {count}/{SAMPLES_PER_STUDENT}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            if progress_callback:
                progress_callback(count)

            if count >= SAMPLES_PER_STUDENT:
                break

        # Instructions
        cv2.putText(
            frame,
            "Look at camera - move slowly",
            (10, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Press Q to cancel",
            (10, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

        # Show camera
        cv2.imshow(
            "Face Registration",
            frame
        )

        # Q or ESC = cancel
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            print("[INFO] Registration cancelled.")
            break

    # ---------------------------------------------------------
    # 8. Close webcam
    # ---------------------------------------------------------
    cap.release()
    cv2.destroyAllWindows()

    # ---------------------------------------------------------
    # 9. Check result
    # ---------------------------------------------------------
    if count < SAMPLES_PER_STUDENT:

        print(
            f"[ERROR] Only {count} samples captured."
        )

        return False, (
            f"Only {count} face samples captured. "
            f"Registration incomplete."
        )

    print("=" * 60)
    print(
        f"[OK] {count} face samples saved "
        f"for {name}"
    )
    print("[INFO] Folder:", folder)
    print("=" * 60)

    return True, (
        f"Student '{name}' registered successfully "
        f"with ID {student_id}!"
    )
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
        (student_id,),
        fetch=True
    )

    if student and student[0]["image_path"]:
        folder = student[0]["image_path"]

        if os.path.exists(folder):
            shutil.rmtree(folder)

    execute_query(
        "DELETE FROM students WHERE student_id = %s",
        (student_id,)
    )

    return True