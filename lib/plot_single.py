# ============================================================================
#  LOCKED LOOK -- the dialed-in mesh view. The camera (AZIMUTH/ELEVATION, DOLLY_DIST, lens) stays LOCKED
#  here so the reproduction is fixed; the rest (samples/ZSCALE/hole/margin) are exposed as config.sh knobs.
#    samples            = SAMPLES env, default 128   (line ~52; config.sh)
#    ZSCALE             = obj.scale.z *= ZSCALE (default 0.7)  (line ~106; wave height; config.sh)
#    central hole       = cylinder radius HOLE_RADIUS (default 7.5, physical M_sun)  (line ~120; config.sh)
#    camera DOLLY_DIST  = 125 (dollied IN for 2x magnification)  ELEV_DEG = 37.4  lens = 50mm*ZOOM (ZOOM=1)
#    why dolly not zoom = 2x via dollying-in keeps the WIDE 50mm converging perspective; a telephoto (ZOOM>1)
#                         would give the same magnification but FLATTEN the perspective. DOLLY_DIST & ZOOM are
#                         env-overridable but locked by default. The disk billboard (_hw), time label, and grid
#                         brick Scale (=0.02*781.8/DOLLY_DIST*ZOOM) ALL auto-track them -> one consistent ruler.
#  Paths/frames come from config.sh via the CLI args this script is called with.
# ============================================================================
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
zero_plane = argv[argv.index("--") + 15]
sys.path.append(shader_dir)

from shader_grid_solidlightblue import shader_gridwb_node_group
from shader_grid_solidlightblue import blue
from shader_grid_solidlightblue import shader_twoblue_3
from time_bar import time_node_group
import shader_grid_solidlightblue
# from change_color import changecolor_node_group   # only needed for plot_mem=1; module-level demo crashes on Blender 5.0
#from change_color import nsns_node_group
from nsns_density import nsns_node_group           # with_density=1: disk card laid in the orbital plane

# Delete all objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#-----------------------Setting for Faster Rendering---------------------------#
bpy.context.scene.render.use_simplify = True
bpy.context.scene.cycles.samples = int(os.environ.get("SAMPLES", "128")) # env knob SAMPLES (config.sh); default 128
ZOOM = float(os.environ.get("ZOOM", "1.0"))  # LOCKED look: lens = 50mm*ZOOM, default ZOOM=1 -> wide 50mm (converging perspective). env-overridable. ZOOM>1 = telephoto (flattens perspective) -- not used; the 2x magnification is done by dollying instead (DOLLY_DIST). Read EARLY (grid shader/lens/billboard/label all use it).
_DOLLY_DIST = float(os.environ.get("DOLLY_DIST", "125"))  # LOCKED look: camera distance, default 125 = dollied in for 2x magnification while the wide 50mm lens KEEPS the converging perspective (vs telephoto, which flattens). env-overridable. Read EARLY for the grid shader.
# Set scene camera and rendering engine

bpy.context.scene.render.engine = 'CYCLES'
#bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
#bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'

# bpy.context.scene.cycles.tile_x = 16   # Blender 5.0: tile_x/tile_y removed (automatic tiling)
# bpy.context.scene.cycles.tile_y = 16

# Set world background color (Gray background)
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.006, 0.051, 1)

# Set thread mode to 'FIXED'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.threads_mode = 'FIXED'
bpy.context.scene.render.threads = int(os.environ.get("BLENDER_THREADS", "12"))  # env knob BLENDER_THREADS, default 12 = matches config.sh (the array job packs 2 procs x 12 threads/24-core task)

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
    obj.scale.z *= float(os.environ.get("ZSCALE", "0.35")) # blender z-scale (ZSCALE); LOCKED default 0.35. Total z-amp = scale_factor(5000)*ZSCALE (=1750 at 0.35). Halved from the old 0.7 to cancel the DOLLY_DIST=125 2x magnification (=0.7*125/250) so the wave shares the same on-screen ruler as the grid/disk/hole. Cheap knob via env; no mesh regen.
    obj.rotation_euler = (90*np.pi/180, -120*np.pi/180, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()

# Choose the wave object (we assume only one object named "wave" exists)
obj = bpy.data.objects["wave"]

#Add solidify (so it can do boolean)
#solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
#solidify.thickness = 0.01  # You can adjust thickness


#------Boolean------#
bpy.ops.mesh.primitive_cylinder_add(radius=float(os.environ.get("HOLE_RADIUS", "7.5")), depth=1000, location=(0, 0, 0))  # central cutout (PHYSICAL M_sun, independent of ZOOM); env knob HOLE_RADIUS, default 7.5 = matches config.sh. The ~7 M_sun disk seats inside with margin.
cylinder = bpy.context.active_object
cylinder.name = "Boolean_Cylinder"
cylinder.rotation_euler[0] = math.radians(90)
cylinder.hide_render = True

# Add a Boolean modifier to 'wave' using the cylinder
boolean = obj.modifiers.new(name="Boolean_Diff", type='BOOLEAN')
boolean.object = cylinder
boolean.operation = 'DIFFERENCE'
boolean.solver = 'FLOAT'   # Blender 5.0: 'FAST' renamed to 'FLOAT' (enum FLOAT/EXACT/MANIFOLD)
#------Boolean------#


# Add a Subdivision Surface modifier
subdivide_modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
subdivide_modifier.levels = 1  # Viewport levels
subdivide_modifier.render_levels = 1  # Render levels


# Append the material from your shader grid node group
if plot_mem == "0":
    #The shader for no memory
    shader_wb_material = shader_twoblue_3(grid_scale=0.02*781.8/_DOLLY_DIST*ZOOM)   # cell scale ~ magnification = (250/_DOLLY_DIST)*ZOOM. Physical cell halves as the mesh is magnified 2x (8.7->4.6 M_sun), so on-screen grid density stays the same AND the cell M_sun stays consistent with the faithfully-placed disk -> one uniform ruler. Tracks BOTH dolly and lens zoom; =0.125 at the default dist250/ZOOM2 and at dist125/ZOOM1.
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

# --- Camera elevation control (raise = more top-down: covers more ground-plane, hole sits centered not "on the ceiling", disk more face-on) ---
# Disk/orbital plane normal in Blender world = (0,-1,0). Keep the artist camera's azimuth + distance
# (orig pos (600,-475,-160), dist 781.79, elev 37.4 deg); change ONLY the elevation angle above the plane.
_az_xz   = mathutils.Vector((600.0, -160.0)); _az_xz.normalize()   # in-plane (x,z) direction
# _DOLLY_DIST is read once near the top (env knob DOLLY_DIST, default 250). Dollying CLOSER magnifies the mesh while the wide 50mm lens KEEPS the converging perspective (unlike telephoto/ZOOM, which flattens it). Needs the wider ±200 M_sun mesh (obj_data, XY_MAX=200) so far corners stay covered.
ELEV_DEG = 37.4                                                   # artist/reference grazing angle. LOWER = more grazing/receding plane; HIGHER = more top-down.
_el      = ELEV_DEG * np.pi/180.0
_horiz   = _DOLLY_DIST * np.cos(_el); _height = _DOLLY_DIST * np.sin(_el)
camera_used.location = (_horiz*_az_xz.x, -_height, _horiz*_az_xz.y)  # y<0 = above plane (normal is -y). orig (600,-475,-160) #for bh cluster(2270, -1753, -537)
camera_used.rotation_euler = (296*np.pi/180, -108.19*np.pi/180, -153.6*np.pi/180) #(295.2*np.pi/180, -107.94*np.pi/180, -152.05*np.pi/180)
camera_data.clip_end = 10000.0

# --- lens = 50mm*ZOOM (ZOOM env knob, config.sh, default 2.0 -> 100mm). ZOOM is a PURE optical
# magnification at the FIXED camera position (_DOLLY_DIST=250), i.e. a telephoto -- this is the exact
# analog of the VisIt disk view's imageZoom (also a pure magnification at fixed eye), so disk and mesh
# share one scale. A MILD 2x (100mm) keeps usable converging perspective; do NOT push to a strong
# telephoto (e.g. 15x/750mm, ~1.5deg FOV) which goes near-orthographic and KILLS the convergence.
# (Magnify here, NOT by dollying closer: dollying changes the viewpoint and would break the match
# with the disk, which was rendered from distance 250.) First re-aim the optical axis exactly at the
# origin (minimal rotation -> roll preserved). The disk billboard (_hw), time label, and grid-shader
# brick Scale all auto-track ZOOM below.
# (ZOOM is read once near the top, with SAMPLES, so it's available to the grid shader earlier in the file.)
_base_rot   = camera_used.rotation_euler.to_matrix()
_fwd        = _base_rot @ mathutils.Vector((0.0, 0.0, -1.0))
_to_origin  = (mathutils.Vector((0.0, 0.0, 0.0)) - camera_used.location).normalized()
_realign    = _fwd.rotation_difference(_to_origin)          # minimal rotation, keeps roll
camera_used.rotation_euler = (_realign.to_matrix() @ _base_rot).to_euler()
camera_data.lens = 50.0 * ZOOM                              # 50mm base * ZOOM (default 2.0 -> 100mm). Pure magnification at fixed _DOLLY_DIST, matching the disk's VisIt imageZoom.

bpy.context.scene.camera = camera_used
#-----------------------Add sunlight and camera---------------------------#




#------Add density------#

if with_density == "1":
    print("Adding disk as a FLAT top-down card lying in the orbital plane (grazing view)...")
    # NEW (flat top-down disk): the disk PNG is now a face-on / top-down density map (NOT the old
    # pre-foreshortened grazing render). So we lay the card FLAT in the orbital plane and let the
    # grazing camera foreshorten it exactly once -> it reads as a flat disk seated on the fabric.
    # (This is the opposite of the old path, which billboarded a pre-foreshortened frame at the
    # camera.) World size is unchanged from the engineered overlay -- only the orientation flips from
    # camera-facing to in-plane. The card sits EXACTLY in the orbital plane (y=0) and is CLIPPED to
    # the hole (see below), so the disk (~4-5 M_sun) seats inside the HOLE_RADIUS cutout with its
    # transparent margin removed. Transparent (alpha-0) bg shows the backdrop through the hole.
    # Per-frame disk image comes from DISK_IMAGE (the driver sets it); falls back to the test card.
    image_path = os.environ.get("DISK_IMAGE",
        "/anvil/scratch/x-yguo11/blender_gw_dev/density_movies/disk_card_0010.png")
    # Placement: EXACTLY in the orbital plane by default. The coplanar z-fight with the flat mesh
    # (t/M=0 and the flat tail) is avoided by CLIPPING the card to the hole below (INTERSECT with the
    # same HOLE_RADIUS cylinder that cuts the mesh): mesh keeps r>HOLE_RADIUS, card keeps
    # r<HOLE_RADIUS -> complementary, zero overlap, nothing to z-fight. DISK_MARGIN>0 optionally
    # floats the card off the plane toward the camera (orbital normal (0,-1,0), camera at y<0 -> -y).
    _margin  = float(os.environ.get("DISK_MARGIN", "0"))                # optional M_sun lift toward the camera; default 0 = EXACTLY in the orbital plane
    _loc     = mathutils.Vector((0.0, -_margin, 0.0))                   # in-plane by default; the hole-clip (below) prevents any z-fight
    _hw = _DOLLY_DIST * (camera_data.sensor_width / 2.0) / camera_data.lens  # render half-width (M_sun); engineered size unchanged (tiny lift = negligible size change)
    _rh = bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=_loc)
    plane = bpy.context.active_object
    plane.name = "disk_billboard"
    plane.rotation_euler = (math.radians(90), 0.0, 0.0)               # lie FLAT in the orbital plane (normal -> world -Y, matches the fabric). Roll irrelevant for the radial disk.
    _dscale = float(os.environ.get("DISK_SCALE", "1.0"))              # per-frame gauge-shrink size normalization (manifest col 3)
    plane.scale = (_hw * _dscale, _hw * _rh * _dscale, 1.0)           # fill frame 1:1 at depth, x DISK_SCALE -> hold constant apparent size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Clip the card to the hole (same cylinder that cuts the mesh) so its transparent margin never
    # overlaps the coplanar flat mesh -> no z-fight even with the card exactly in-plane. EXACT solver
    # handles the coarse quad-vs-cylinder cut cleanly; the disk (well inside the hole) is untouched.
    _clip = plane.modifiers.new(name="Clip_To_Hole", type='BOOLEAN')
    _clip.object = bpy.data.objects["Boolean_Cylinder"]
    _clip.operation = 'INTERSECT'
    _clip.solver = 'EXACT'
    plane.visible_shadow = False                                      # don't cast the disk card's shadow on the waves
    plane_mat = nsns_node_group(image_path)
    plane.data.materials.append(plane_mat)
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
        node.inputs[0].default_value = frame_number * 0.056325 / 0.0603349020955639  # t/M = frame*dt/M_ADM (physical), was NSNS 3.52/2.7
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

# Pin the label to the TOP-RIGHT corner: parent it to the camera and place it in camera space
# (x=right, y=up, -z=forward) so it stays put at any zoom/aim. At distance _D the visible frame
# half-extents are _D*tan(hfov/2) wide (=_D*18/lens) and *(9/16) tall (16:9). Text is align_x=CENTER,
# align_y=TOP_BASELINE (Size=33.6 native): centered on its origin-x, hangs below origin-y.
_D = 100.0
time_obj.parent = camera_used
time_obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)   # local transform == camera-space
time_obj.location = mathutils.Vector((23.25/ZOOM, 15.75/ZOOM, -_D))   # top-right; coords ~ 1/lens (the old "rescaled x15=750/50" logic), so /ZOOM keeps the SAME corner as the lens magnifies. Base (23.25,15.75) is the 50mm placement (frame half-extents at z=-_D are W=_D*18/50=36, H=20.25 -> 65%/78% toward the corner); at ZOOM=2 -> (11.625,7.875), else it falls off-screen (W shrinks to 18).
time_obj.rotation_euler = (0.0, 0.0, 0.0)                       # face the camera (text in its XY plane)
time_obj.scale = (0.12/ZOOM, 0.12/ZOOM, 0.12/ZOOM)            # scale ~ 1/lens (same law as position), so /ZOOM keeps the on-screen label size constant as the lens magnifies. Base 0.12 = ~10% of frame height at 50mm (33.6*0.12/40.5); at ZOOM=2 -> 0.06.
time_obj.visible_shadow = False
# --------------------- Add Time bar--------------------- #



# -----------------ADD 0 plane--------#

if zero_plane == "1":
    print("Add 0-plane")
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.scale = (1000, 2, 1000) 
else:
    print("Does not add 0-plane")

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

