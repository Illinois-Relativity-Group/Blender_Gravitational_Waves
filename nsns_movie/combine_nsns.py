import os
import shutil
import re

def get_sorted_image_files(folder):
    # Match files like memory_1.png, memory_23.png, etc.
    pattern = re.compile(r"memory_(\d+)\.png")
    files = []
    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))
            files.append((number, filename))
    files.sort()  # Sort by the numeric part
    return [f for _, f in files]

def rename_and_copy_files(src_folder, dst_folder, start_index):
    files = get_sorted_image_files(src_folder)
    for i, filename in enumerate(files):
        new_name = f"memory_{start_index + i}.png"
        shutil.copy(os.path.join(src_folder, filename), os.path.join(dst_folder, new_name))
    return start_index + len(files)  # Return new index to continue from

def merge_image_folders(folder_a, folder_b, folder_c):
    os.makedirs(folder_c, exist_ok=True)
    next_index = rename_and_copy_files(folder_a, folder_c, 1)
    rename_and_copy_files(folder_b, folder_c, next_index)

# Example usage
merge_image_folders("nsns_hydro_part", "nsns_density", "full_movie")
