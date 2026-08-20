# ============================================================
#  modules/train_model.py
#  Trains the LBPH face recognition model
# ============================================================

import cv2
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IMAGES_PATH, MODEL_PATH


def train_model(progress_callback=None):
    """
    Reads all face images from data/student_images/
    Trains LBPH recognizer
    Saves model to data/trained_model.yml
    Returns: (success: bool, message: str)
    """

    faces  = []
    labels = []

    if not os.path.exists(IMAGES_PATH):
        return False, "No student images folder found. Register students first."

    student_folders = [
        f for f in os.listdir(IMAGES_PATH)
        if os.path.isdir(os.path.join(IMAGES_PATH, f))
    ]

    if not student_folders:
        return False, "No student data found. Please register students first."

    total = len(student_folders)
    print(f"[INFO] Training on {total} student(s)...")

    for idx, folder_name in enumerate(student_folders):
        try:
            student_id = int(folder_name)
        except ValueError:
            continue

        folder_path = os.path.join(IMAGES_PATH, folder_name)
        img_files   = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]

        for img_file in img_files:
            img_path = os.path.join(folder_path, img_file)
            img      = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (200, 200))
                faces.append(img)
                labels.append(student_id)

        if progress_callback:
            progress_callback(idx + 1, total)

    if not faces:
        return False, "No face images found. Register students and try again."

    # ── Train LBPH recognizer ─────────────────────────────────
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1, neighbors=8, grid_x=8, grid_y=8
    )
    recognizer.train(faces, np.array(labels))

    # ── Save model ────────────────────────────────────────────
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    recognizer.save(MODEL_PATH)

    msg = f"Model trained on {len(set(labels))} student(s), {len(faces)} images. Saved!"
    print(f"[OK] {msg}")
    return True, msg
