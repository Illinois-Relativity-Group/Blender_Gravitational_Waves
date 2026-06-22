import os
import numpy as np
import matplotlib.pyplot as plt

def load_obj_z_grid(filename):
    vertices = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):  # Vertex line
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))

    vertices = np.array(vertices)

    x_unique = np.unique(vertices[:, 0])
    y_unique = np.unique(vertices[:, 1])
    x_unique.sort()
    y_unique.sort()

    z_grid = np.full((len(y_unique), len(x_unique)), np.nan)

    for x, y, z in vertices:
        ix = np.where(x_unique == x)[0][0]
        iy = np.where(y_unique == y)[0][0]
        z_grid[iy, ix] = z

    return z_grid

def load_obj_rz_grid(filename):
    vertices = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):  # Vertex line
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                r = np.sqrt(x**2 + y**2)
                rz = r * z
                vertices.append((x, y, rz))

    vertices = np.array(vertices)

    x_unique = np.unique(vertices[:, 0])
    y_unique = np.unique(vertices[:, 1])
    x_unique.sort()
    y_unique.sort()

    rz_grid = np.full((len(y_unique), len(x_unique)), np.nan)

    for x, y, rz in vertices:
        ix = np.where(x_unique == x)[0][0]
        iy = np.where(y_unique == y)[0][0]
        rz_grid[iy, ix] = rz

    return rz_grid


def create_grayscale_image(z_grid, zmin=250, zmax=750):
    z_normalized = np.clip(z_grid, zmin, zmax)
    z_scaled = 255 * (1 - (z_normalized - zmin) / (zmax - zmin))
    z_scaled = np.nan_to_num(z_scaled, nan=255)
    return z_scaled

def process_obj_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.obj'):
            input_path = os.path.join(input_dir, filename)
            output_name = os.path.splitext(filename)[0] + '.png'
            output_path = os.path.join(output_dir, output_name)

            try:
                #z_grid = load_obj_z_grid(input_path)
                rz_grid = load_obj_rz_grid(input_path)
                img_array = create_grayscale_image(rz_grid)
                plt.imsave(output_path, img_array, cmap='gray', vmin=0, vmax=255)
                print(f"Saved: {output_path}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

# Example usage:
input_directory = '/data/yliang3/memory/blender_wave/obj_data_mem/'
output_directory = '/data/yliang3/memory/blender_wave/texturemap_rz/'
process_obj_directory(input_directory, output_directory)
