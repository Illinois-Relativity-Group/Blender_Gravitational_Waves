import meshio
import numpy as np
import os
    

# Directory containing VTK files
input_directory = "/data/codyolson/blender_waves/gw_2d_xyPlane_1500RES_1omega" 

# Output directory for the OBJ files
output_directory = "/data/codyolson/blender_waves/blender_waves_xyPlane_1500RES_1omega" 

os.makedirs(output_directory, exist_ok=True)
vtk_files = sorted([f for f in os.listdir(input_directory) if f.endswith(".vtk")])


for vtk_file in vtk_files:
    input_file = os.path.join(input_directory, vtk_file)
    mesh = meshio.read(input_file)

    dimensions = [1500, 1500]  
    x_dim, y_dim = dimensions
    scalar_field = mesh.point_data["GW-FIELD"]  

    x = np.linspace(-3000.0, 3000.0, x_dim)  
    y = np.linspace(-3000.0, 3000.0, y_dim)  
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

    output_file = os.path.join(output_directory, f"{os.path.splitext(vtk_file)[0]}.obj")
    meshio.write_points_cells(
        output_file,
        vertices,
        [("quad", faces)]
    )

    print(f"Quad mesh saved to {output_file}")
