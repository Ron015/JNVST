import os
from PIL import Image
from io import BytesIO

# 📏 Resize size
TARGET_WIDTH = 2480
TARGET_HEIGHT = 3508

# ✂️ Crop coordinates (tune these as per your form layout)
CROPS = {
    "PH": (100, 100, 500, 600),       # Student Photo
    "PS": (1800, 2800, 2300, 2900),   # Parent Signature
    "SS": (1800, 2950, 2300, 3050),   # Student Signature
    "FORM": (0, 0, 2480, 3508),       # Full Form Image
}

# 🎯 Size limits in KB
SIZE_LIMITS = {
    "PH": (10, 50),
    "PS": (10, 50),
    "SS": (10, 50),
    "FORM": (100, 300),
}

# 📉 Auto quality reducer to fit image in size range
def save_with_size_limit(img, save_path, min_kb, max_kb):
    quality = 95
    while quality > 10:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = len(buffer.getvalue()) / 1024
        if min_kb <= size_kb <= max_kb:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
            print(f"✅ Saved within limit ({int(size_kb)} KB): {save_path}")
            return
        quality -= 5
    print(f"⚠️ Couldn't meet size range for {save_path}, saved at {int(size_kb)} KB anyway.")
    img.save(save_path, format='JPEG', quality=85, optimize=True)

def process_image(image_path, save_folder):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))  # A4 resize

    for label, coords in CROPS.items():
        cropped = img.crop(coords)
        save_path = os.path.join(save_folder, f"{label}.jpg")  # ✅ Fixed name
        min_kb, max_kb = SIZE_LIMITS[label]
        save_with_size_limit(cropped, save_path, min_kb, max_kb)

def process_all_images_in_folder(root_folder):
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(subdir, file)
                process_image(image_path, subdir)

# 🔍 Path to your folder
main_folder = "your_folder_path_here"  # 👈 Update this
process_all_images_in_folder(main_folder)
