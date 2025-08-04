import os
import cv2
import numpy as np

# 📁 Base folder with numbered subfolders
BASE_FOLDER = "FORMS"  # e.g. FORMS/1/, FORMS/2/, etc.

# ✂️ Fixed crop zones (x1, y1, x2, y2)
PHOTO_ZONE = (100, 100, 500, 600)
PARENT_SIGN_ZONE = (1800, 2800, 2300, 2900)
STUDENT_SIGN_ZONE = (1800, 2950, 2300, 3050)

# 🎯 Size limits (KB)
SIZE_LIMITS = {
    "PH": (10, 50),
    "PS": (10, 50),
    "SS": (10, 50),
    "FORM": (100, 300),
}

# 💾 Compress + Save within size range
def save_with_compression(img, path, min_kb, max_kb):
    for q in range(95, 10, -5):
        _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        size_kb = len(buffer) / 1024
        if min_kb <= size_kb <= max_kb:
            with open(path, 'wb') as f:
                f.write(buffer)
            print(f"✅ Saved {path} ({int(size_kb)} KB)")
            return
    with open(path, 'wb') as f:
        f.write(buffer)
    print(f"⚠️ Saved {path} (out of size range)")

# 🔍 Detect inside zone & crop
def detect_signature(image, zone, label, save_dir):
    x1, y1, x2, y2 = zone
    roi = image[y1:y2, x1:x2]
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500:  # avoid small dots
            cropped = roi[y:y+h, x:x+w]
            save_path = os.path.join(save_dir, f"{label}.jpg")
            min_kb, max_kb = SIZE_LIMITS[label]
            save_with_compression(cropped, save_path, min_kb, max_kb)
            return
    print(f"❌ No valid {label} found.")

# 🔁 Process all subfolders
def process_all_existing_subfolders(base_path):
    for folder in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(folder_path) or not folder.isdigit():
            continue
        
        print(f"\n📂 Processing folder: {folder_path}")
        # Find the image file in that folder
        image_file = None
        for file in os.listdir(folder_path):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_file = file
                break
        if not image_file:
            print("⚠️ No image found in", folder_path)
            continue

        image_path = os.path.join(folder_path, image_file)
        image = cv2.imread(image_path)
        image = cv2.resize(image, (2480, 3508))  # Resize to A4

        # Save full FORM image
        form_path = os.path.join(folder_path, "FORM.jpg")
        min_kb, max_kb = SIZE_LIMITS["FORM"]
        save_with_compression(image, form_path, min_kb, max_kb)

        # Auto-detect from zones
        detect_signature(image, PHOTO_ZONE, "PH", folder_path)
        detect_signature(image, PARENT_SIGN_ZONE, "PS", folder_path)
        detect_signature(image, STUDENT_SIGN_ZONE, "SS", folder_path)

# 🚀 Start processing
process_all_existing_subfolders(BASE_FOLDER)
