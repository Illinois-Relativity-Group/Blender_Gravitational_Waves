import bpy
import sys
import math
import bmesh
import mathutils
import numpy as np
import os

argv = sys.argv
filename = argv[argv.index("--") + 1]
frame_number = int(argv[argv.index("--") + 2])
output_dir = argv[argv.index("--") + 3]
blend_file_path = argv[argv.index("--") + 4]
frame_dir = argv[argv.index("--") + 5]
shader_dir = argv[argv.index("--") + 6]
image_folder = argv[argv.index("--") + 7]
density_folder = argv[argv.index("--") + 8]
bh_file = argv[argv.index("--") + 9]
plot_mem = argv[argv.index("--") + 10]
with_blend_file = argv[argv.index("--") + 11]
with_density = argv[argv.index("--") + 12]
with_bh = argv[argv.index("--") + 13]
save_blender_file = argv[argv.index("--") + 14]
zero_plane = argv[argv.index("--") + 14]
sys.path.append(shader_dir)

from shader_grid_solidlightblue import shader_gridwb_node_group
from shader_grid_solidlightblue import blue
from shader_grid_solidlightblue import shader_twoblue_3
from time_bar import time_node_group
import shader_grid_solidlightblue
from change_color import changecolor_node_group
#from change_color import nsns_node_group
from nsns_density import nsns_node_group

# Delete all objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#-----------------------Setting for Faster Rendering---------------------------#
bpy.context.scene.render.use_simplify = True
bpy.context.scene.cycles.samples = 128 # above 128 doesnt really matter
# Set scene camera and rendering engine
bpy.context.scene.camera = camera_used
bpy.context.scene.render.engine = 'CYCLES'
#bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
#bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'

bpy.context.scene.cycles.tile_x = 16
bpy.context.scene.cycles.tile_y = 16

# Set world background color (Gray background)
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.006, 0.051, 1)
#dark dark blue(0.006, 0.006, 0.051, 1)
#dark blue(0.129, 0.2, 0.271, 1)
#kind of dark blue(0.188, 0.306, 0.42, 1) 
#first blue (0.2, 0.6, 1, 1)

#-----------------------Setting for Faster Rendering---------------------------#


#-----------------------Append blender file---------------------------#


if with_blend_file == "1":
    print("Using blender file")
    # Check if the file exists
    if not os.path.exists(blend_file_path):
        raise FileNotFoundError(f"Blend file not found: {blend_file_path}")

    # Append all objects from the source blend file.
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    # Link each appended object to the active collection in the current scene.
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
    
#-----------------------Append blender file---------------------------#


#-----------------------Imporint the wave plane---------------------------#

# Import the .obj file (The wave plane)
bpy.ops.wm.obj_import(filepath=frame_dir + filename, 
                        forward_axis='NEGATIVE_Z', up_axis='Y')
for obj in bpy.context.selected_objects:
    obj.name = "wave"
    obj.scale.z *= 2 #3
    obj.rotation_euler = (90*np.pi/180, -120*np.pi/180, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()

# Choose the wave object (we assume only one object named "wave" exists)
obj = bpy.data.objects["wave"]

#Add solidify (so it can do boolean)
#solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
#solidify.thickness = 0.01  # You can adjust thickness


#------Boolean------#
bpy.ops.mesh.primitive_cylinder_add(radius=32, depth=300, location=(0, 0, 0))
cylinder = bpy.context.active_object
cylinder.name = "Boolean_Cylinder"
cylinder.rotation_euler[0] = math.radians(90)
cylinder.hide_render = True

# Add a Boolean modifier to 'wave' using the cylinder
boolean = obj.modifiers.new(name="Boolean_Diff", type='BOOLEAN')
boolean.object = cylinder
boolean.operation = 'DIFFERENCE'
boolean.solver = 'FAST'
#------Boolean------#


# Add a Subdivision Surface modifier
subdivide_modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
subdivide_modifier.levels = 1  # Viewport levels
subdivide_modifier.render_levels = 1  # Render levels


# Append the material from your shader grid node group
if plot_mem == "0":
    #The shader for no memory
    shader_wb_material = shader_twoblue_3()
    #shader_wb_material = two_color_blue_red_node_group()
    obj.data.materials.append(shader_wb_material)
elif plot_mem == "1":
    #The shader for memory
    shader_mat = changecolor_node_group(frame_number, image_folder)
    obj.data.materials.append(shader_mat)
else:
    print(f"Warning: Unexpected value for plot_mem: {plot_mem}")

#shader_mat = changecolor_node_group(frame_number, image_folder)
#obj.data.materials.append(shader_mat)

#-----------------------Imporint the wave plane---------------------------#



#-----------------------Add sunlight and camera---------------------------#

# Add light (Sun)
sun_light_data = bpy.data.lights.new(name="SunLight", type='SUN')
sun_light_object = bpy.data.objects.new(name="SunLight", object_data=sun_light_data)
bpy.context.collection.objects.link(sun_light_object)
sun_light_object.location = (96, -106, -16)
sun_light_object.rotation_euler = (27* np.pi/180, 47.6*np.pi/180, 12*np.pi/180)
sun_light_data.energy = 2.5


# Add camera
camera_data = bpy.data.cameras.new(name="Camera")
camera_used = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_used)

camera_used.location = (600, -475, -160) #for bh cluster(2270, -1753, -537)
camera_used.rotation_euler = (296*np.pi/180, -108.19*np.pi/180, -153.6*np.pi/180) #(295.2*np.pi/180, -107.94*np.pi/180, -152.05*np.pi/180)
camera_data.clip_end = 10000.0
#-----------------------Add sunlight and camera---------------------------#




#------Add density------#

if with_density == "1"
    print("Adding density...")
    # Add a plane and assign new material with image
    bpy.ops.mesh.primitive_plane_add(size=50, enter_editmode=False, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.location.y -= 20

    print("temp_frame_number:" + str(frame_number))
    print("density_number:" + str(round(frame_number/3)+1))

    image_filename = f"memory_{round(frame_number/3)+1}.png"
    image_path = os.path.join(density_folder, image_filename)


    plane_mat = nsns_node_group(image_path)
    plane.data.materials.append(plane_mat)

    copy_rot = plane.constraints.new(type='COPY_ROTATION')
    copy_rot.target = camera_used  # camera_used is your camera object
    copy_rot.use_x = True
    copy_rot.use_y = True
    copy_rot.use_z = True
    copy_rot.target_space = 'WORLD'
    copy_rot.owner_space = 'WORLD'
else:
    print("Not adding density")
#------Add density------#




#-----------------Add bh----------------#

if with_bh == "1":
    print("Adding bh as solid sphere")
    with open(bh_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) != 2:
            continue  # Skip malformed lines

        try:
            line_frame = int(parts[0])
            radius = float(parts[1])
        except ValueError:
            continue  # Skip lines with invalid values

        if line_frame == frame_number:
            bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            location=(0, -20, 0)
            )
            sphere = bpy.context.object
            sphere.name = "AutoSphere"

            mat = bpy.data.materials.new(name="BlackMaterial")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)  # Black RGBA
            bsdf.inputs["Roughness"].default_value = 1  # Optional: make it non-reflective
            sphere.data.materials.clear()  # Remove existing materials
            sphere.data.materials.append(mat)
            break  # Only plot the first match
#-----------------Add bh----------------#




# --------------------- Add Time bar--------------------- #
# Create the time node group instance and update its "Value to String" node with the frame number
# Assuming the time_node_group and text_node_group functions are defined elsewhere
time_group = time_node_group()
for node in time_group.nodes:
    if node.name == "Value to String":
        node.inputs[0].default_value = frame_number * 3.52 / 2.7
        break

# Create a new empty mesh object to host the time text geometry
time_mesh = bpy.data.meshes.new("TimeMesh")
time_obj = bpy.data.objects.new("TimeText", time_mesh)
bpy.context.collection.objects.link(time_obj)

# Add a Geometry Nodes modifier to this object using the time node group
time_mod = time_obj.modifiers.new("TimePlot", 'NODES')
time_mod.node_group = time_group

# Create a black material
black_material = bpy.data.materials.new(name="BlackMaterial")
black_material.use_nodes = True
nodes = black_material.node_tree.nodes
nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 1, 1)  # (0, 0, 0, 1) RGBA for black color
nodes["Principled BSDF"].inputs[28].default_value = 1.0 #Emission

# Ensure the geometry nodes group applies the material
if "Material" not in [n.name for n in time_group.nodes]:
    material_node = time_group.nodes.new(type="GeometryNodeSetMaterial")
    material_node.inputs["Material"].default_value = black_material
    # Link the material node to the output of the existing node group
    time_output = next(n for n in time_group.nodes if n.type == "GROUP_OUTPUT")
    links = time_group.links
    # Connect the material node
    last_socket = time_output.inputs["Geometry"].links[0].from_socket
    links.new(last_socket, material_node.inputs["Geometry"])
    links.new(material_node.outputs["Geometry"], time_output.inputs["Geometry"])

time_obj.location = mathutils.Vector((-12.65,  -55, 177.76)) #mathutils.Vector((-236, 1358, -1867))
time_obj.rotation_euler = (294*np.pi/180, -108*np.pi/180, -152*np.pi/180) #(np.deg2rad(153.74), np.deg2rad(1.9617), np.deg2rad(182.64))
time_obj.scale *= 0.8  #0.086
time_obj.visible_shadow = False
# --------------------- Add Time bar--------------------- #



# -----------------ADD 0 plane--------#

if zero_plane == "1":
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.scale = (1000, 2, 1000) 

# -----------------ADD 0 plane--------#


# ----------------------------Save Blender File------------------------------------------- #

if save_blender_file == "1":
    print("Save blender files...")
    final_filename = "final.blend"
    ## Construct the full path to save the file.
    final_filepath = os.path.join(output_dir, final_filename)

    ## Save the Blender file to the specified path.
    bpy.ops.wm.save_as_mainfile(filepath=final_filepath)
else:
    print("No blender file saved")
# ----------------------------Save Image File------------------------------------------- #

# Set render filepath (you can include frame number or filename as desired)
bpy.context.scene.render.filepath = f"{output_dir}/{filename}.jpeg"
#bpy.context.scene.render.filepath = f"/data/yliang3/BH_N25/blender_code/wave_movie_2_20/yinuan_plotting/test_image/6.png"

# Set the scene frame (using the passed frame number)
bpy.context.scene.frame_set(frame_number)

# Render the scene
bpy.ops.render.render(write_still=True)

