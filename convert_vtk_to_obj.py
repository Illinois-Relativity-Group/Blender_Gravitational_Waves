#!/usr/bin/env python
import os
import sys
import argparse
import numpy as np
import meshio

# --- Global Options ---
DEFAULT_RADIUS = 27
VTK_INPUT_DIR = "/data/yliang3/memory/blender_wave/2D_10000"
FINAL_OUTPUT_DIR = "/data/yliang3/memory/blender_wave/obj_data"

def process_mesh(vertices, faces, radius):
    """
    Remove vertices inside the circle of the given radius and update face connectivity.
    Vertices are removed if (x^2 + y^2) < (radius^2). Faces containing any removed vertices are discarded.
    The remaining vertices are renumbered (0-indexed) for writing with meshio.
    """
    r2 = radius * radius
    keep = (vertices[:, 0]**2 + vertices[:, 1]**2) >= r2

    # Build a mapping from old vertex indices to new ones.
    new_index = -np.ones(len(vertices), dtype=int)
    count = 0
    for i in range(len(vertices)):
        if keep[i]:
            new_index[i] = count
            count += 1

    # Process faces: only keep faces if all vertices are kept.
    new_faces = []
    for face in faces:
        if all(keep[face]):
            new_face = [new_index[i] for i in face]
            new_faces.append(new_face)
    new_faces = np.array(new_faces)

    new_vertices = vertices[keep, :]
    return new_vertices, new_faces

def convert_and_process_vtk(vtk_input_dir, final_output_dir, radius, start=None, end=None):
    """
    Process VTK files from vtk_input_dir by:
      - Reading the VTK file,
      - Building a quad mesh,
      - Removing vertices inside a circle of the given radius,
      - And saving the processed mesh as an OBJ file in final_output_dir.
    
    If start and end are provided, only the files in that index range (from the sorted list) are processed.
    """
    os.makedirs(final_output_dir, exist_ok=True)
    vtk_files = sorted([f for f in os.listdir(vtk_input_dir) if f.endswith(".vtk")])
    
    # If start and/or end indices are provided, slice the list.
    if start is not None or end is not None:
        if start is None:
            start = 0
        if end is None:
            end = len(vtk_files)
        vtk_files = vtk_files[start:end]
    
    for vtk_file in vtk_files:
        input_file = os.path.join(vtk_input_dir, vtk_file)
        mesh = meshio.read(input_file)

        # --- Build the quad mesh ---
        dimensions = [500, 500]
        x_dim, y_dim = dimensions
        scalar_field = mesh.point_data["GW-FIELD"]

        # Create grid coordinates.
        x = np.linspace(-1000.0, 1000.0, x_dim)
        y = np.linspace(-1000.0, 1000.0, y_dim)
        X, Y = np.meshgrid(x, y)
        Z = scalar_field.reshape(y_dim, x_dim)
        vertices = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))

        # Build faces for a quad mesh.
        faces = []
        for i in range(y_dim - 1):
            for j in range(x_dim - 1):
                bottom_left = i * x_dim + j
                bottom_right = i * x_dim + (j + 1)
                top_left = (i + 1) * x_dim + j
                top_right = (i + 1) * x_dim + (j + 1)
                faces.append([bottom_left, bottom_right, top_right, top_left])
        faces = np.array(faces)

        # --- Process the mesh ---
        new_vertices, new_faces = process_mesh(vertices, faces, radius)

        # --- Save the processed OBJ file ---
        output_file = os.path.join(final_output_dir, f"{os.path.splitext(vtk_file)[0]}.obj")
        meshio.write_points_cells(output_file, new_vertices, [("quad", new_faces)])
        print(f"Processed cutout mesh saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
         description="Convert VTK files to processed OBJ cutout files by removing vertices inside a circle."
    )
    parser.add_argument("--vtk_input_dir", default=VTK_INPUT_DIR,
                        help="Directory containing input VTK files.")
    parser.add_argument("--final_output_dir", default=FINAL_OUTPUT_DIR,
                        help="Directory to store the final processed OBJ files.")
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS,
                        help="Radius for removing vertices (set to 0 to keep all vertices).")
    parser.add_argument("--start", type=int, default=None,
                        help="Start index for processing VTK files (inclusive).")
    parser.add_argument("--end", type=int, default=None,
                        help="End index for processing VTK files (exclusive).")
    args = parser.parse_args()

    convert_and_process_vtk(args.vtk_input_dir, args.final_output_dir, args.radius, args.start, args.end)

if __name__ == "__main__":
    main()
