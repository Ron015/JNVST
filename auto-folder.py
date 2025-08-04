import os
import time
import shutil

# 📂 Watch this folder for new images
WATCH_FOLDER = "INCOMING"  # Change this to your actual path

# 📁 Check for latest numbered folder
def get_next_folder_number():
    subfolders = [f for f in os.listdir(WATCH_FOLDER) if os.path.isdir(os.path.join(WATCH_FOLDER, f))]
    numbered = [int(f) for f in subfolders if f.isdigit()]
    return str(max(numbered) + 1 if numbered else 1)

# 🧠 Move image to new numbered folder
def move_to_new_folder(image_path):
    new_folder_name = get_next_folder_number()
    new_folder_path = os.path.join(WATCH_FOLDER, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    dest_path = os.path.join(new_folder_path, os.path.basename(image_path))
    shutil.move(image_path, dest_path)
    print(f"✅ Moved {image_path} to {dest_path}")

# 🔁 Watch loop
def watch_folder():
    print("👀 Watching folder for new images...")
    already_seen = set(os.listdir(WATCH_FOLDER))

    while True:
        current_files = set(os.listdir(WATCH_FOLDER))
        new_files = current_files - already_seen

        for file in new_files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(WATCH_FOLDER, file)
                time.sleep(1)  # Wait a bit in case it's still being copied
                move_to_new_folder(image_path)

        already_seen = current_files
        time.sleep(2)

# 🚀 Run it
watch_folder()
