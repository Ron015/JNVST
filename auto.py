import os
import time
import shutil
from PIL import Image
from io import BytesIO

WATCH_FOLDER = "INCOMING"  # Folder Name

TARGET_WIDTH = 2480
TARGET_HEIGHT = 3508

CROPS = {
    "PH": (100, 100, 500, 600),
    "PS": (1800, 2800, 2300, 2900),
    "SS": (1800, 2950, 2300, 3050),
    "FORM": (0, 0, 2480, 3508),
}

SIZE_LIMITS = {
    "PH": (10, 50),
    "PS": (10, 50),
    "SS": (10, 50),
    "FORM": (100, 300),
}

def get_next_folder_number():
    subfolders = [f for f in os.listdir(WATCH_FOLDER) if os.path.isdir(os.path.join(WATCH_FOLDER, f))]
    numbers = [int(f) for f in subfolders if f.isdigit()]
    return str(max(numbers) + 1 if numbers else 1)

def save_with_size_limit(img, save_path, min_kb, max_kb):
    quality = 95
    while quality > 10:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = len(buffer.getvalue()) / 1024
        if min_kb <= size_kb <= max_kb:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
            print(f"✅ Saved {os.path.basename(save_path)} ({int(size_kb)} KB)")
            return
        quality -= 5
    img.save(save_path, format='JPEG', quality=85, optimize=True)
    print(f"⚠️ Saved {os.path.basename(save_path)} (size off-limit)")

def process_image(image_path, save_folder):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))

    for label, coords in CROPS.items():
        cropped = img.crop(coords)
        save_path = os.path.join(save_folder, f"{label}.jpg")  # 🚫 No original name
        min_kb, max_kb = SIZE_LIMITS[label]
        save_with_size_limit(cropped, save_path, min_kb, max_kb)

def move_and_process(image_path):
    new_folder = get_next_folder_number()
    new_folder_path = os.path.join(WATCH_FOLDER, new_folder)
    os.makedirs(new_folder_path, exist_ok=True)

    dest_image_path = os.path.join(new_folder_path, "original.jpg")  # Temporary rename
    shutil.move(image_path, dest_image_path)
    print(f"📦 Moved image to: {dest_image_path}")

    process_image(dest_image_path, new_folder_path)
    os.remove(dest_image_path)  # 🧹 Clean original after processing

def watch_folder():
    print("👁️ Watching for new images in:", WATCH_FOLDER)
    already_seen = set(os.listdir(WATCH_FOLDER))

    while True:
        current_files = set(os.listdir(WATCH_FOLDER))
        new_files = current_files - already_seen

        for file in new_files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(WATCH_FOLDER, file)
                time.sleep(1)
                move_and_process(image_path)

        already_seen = set(os.listdir(WATCH_FOLDER))
        time.sleep(2)

if __name__ == "__main__":
    watch_folder()
