#!/usr/bin/env python
import os
import sys
import argparse
import numpy as np
import meshio

# --- Global Options ---
DEFAULT_RADIUS = 27
VTK_INPUT_DIR = "/data/yliang3/memory/blender_wave/2D_with_both_var"
FINAL_OUTPUT_DIR = "/data/yliang3/memory/blender_wave/obj_data_mem"

def process_mesh(vertices, faces, radius):
    r2 = radius * radius
    keep = (vertices[:, 0]**2 + vertices[:, 1]**2) >= r2

    new_index = -np.ones(len(vertices), dtype=int)
    count = 0
    for i in range(len(vertices)):
        if keep[i]:
            new_index[i] = count
            count += 1

    new_faces = []
    for face in faces:
        if all(keep[face]):
            new_face = [new_index[i] for i in face]
            new_faces.append(new_face)
    new_faces = np.array(new_faces)

    new_vertices = vertices[keep, :]
    return new_vertices, new_faces

def convert_and_process_vtk(vtk_input_dir, final_output_dir, radius, variable, start=None, end=None):
    os.makedirs(final_output_dir, exist_ok=True)
    vtk_files = sorted([f for f in os.listdir(vtk_input_dir) if f.endswith(".vtk")])

    if start is not None or end is not None:
        if start is None:
            start = 0
        if end is None:
            end = len(vtk_files)
        vtk_files = vtk_files[start:end]

    for vtk_file in vtk_files:
        input_file = os.path.join(vtk_input_dir, vtk_file)
        mesh = meshio.read(input_file)

        if variable not in mesh.point_data:
            print(f"Variable '{variable}' not found in {vtk_file}. Skipping.")
            continue

        scalar_field = mesh.point_data[variable]
        dimensions = [500, 500]
        x_dim, y_dim = dimensions

        x = np.linspace(-1000.0, 1000.0, x_dim)
        y = np.linspace(-1000.0, 1000.0, y_dim)
        X, Y = np.meshgrid(x, y)
        Z = scalar_field.reshape(y_dim, x_dim)
        vertices = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))

        faces = []
        for i in range(y_dim - 1):
            for j in range(x_dim - 1):
                bottom_left = i * x_dim + j
                bottom_right = i * x_dim + (j + 1)
                top_left = (i + 1) * x_dim + j
                top_right = (i + 1) * x_dim + (j + 1)
                faces.append([bottom_left, bottom_right, top_right, top_left])
        faces = np.array(faces)

        new_vertices, new_faces = process_mesh(vertices, faces, radius)

        output_file = os.path.join(final_output_dir, f"{os.path.splitext(vtk_file)[0]}_{variable}.obj")
        meshio.write_points_cells(output_file, new_vertices, [("quad", new_faces)])
        print(f"Processed mesh for '{variable}' saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert VTK files to processed OBJ cutout files for a specific scalar variable."
    )
    parser.add_argument("--vtk_input_dir", default=VTK_INPUT_DIR,
                        help="Directory containing input VTK files.")
    parser.add_argument("--final_output_dir", default=FINAL_OUTPUT_DIR,
                        help="Directory to store the final processed OBJ files.")
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS,
                        help="Radius for removing vertices (set to 0 to keep all vertices).")
    parser.add_argument("--variable", type=str, required=True,
                        help="Scalar variable name to convert (e.g., 'GW-MEM').")
    parser.add_argument("--start", type=int, default=None,
                        help="Start index for processing VTK files (inclusive).")
    parser.add_argument("--end", type=int, default=None,
                        help="End index for processing VTK files (exclusive).")
    args = parser.parse_args()

    convert_and_process_vtk(args.vtk_input_dir, args.final_output_dir, args.radius,
                            args.variable, args.start, args.end)

if __name__ == "__main__":
    main()
