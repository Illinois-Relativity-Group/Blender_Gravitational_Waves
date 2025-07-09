import os
import re

# Set the directory containing the files
directory = '/data/yliang3/memory/blender_wave/nsns_movie/nsns_hydro_part'  # Change this to your folder path

# Pattern to match the original files
pattern = re.compile(r'memory_2_(\d{3})_(\d{3})_(\d{4})\.png')

# Get and sort all matching files
files = sorted([f for f in os.listdir(directory) if pattern.match(f)])

# Rename the files in sequential order
for i, filename in enumerate(files, start=1):
    old_path = os.path.join(directory, filename)
    new_filename = f'memory_{i}.png'
    new_path = os.path.join(directory, new_filename)
    
    os.rename(old_path, new_path)
    print(f'Renamed: {filename} → {new_filename}')
