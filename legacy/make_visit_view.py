"""make_visit_view.py  --  derive a VisIt View3D from the LOCKED plot_single.py mesh camera.

Run headless:
    blender --background --python make_visit_view.py

It rebuilds the camera EXACTLY as plot_single.py does (same _DOLLY_DIST / ELEV_DEG / lens +
the realign-to-origin quaternion) and the wave mesh's rotation (90,-120,0) that maps the
sim/equatorial frame into Blender world. Using Blender's own mathutils removes all Euler/quat
convention risk. It then expresses the camera in the DISK (sim, M_sun) frame and prints a ready
VisIt View3D so the 7 M_sun disk can be rendered from the identical grazing viewpoint and overlaid
into the 10 M_sun hole.

The disk lives at z_sim = 0 (equatorial plane); the hole/focus is the sim origin.
"""
import bpy, mathutils, math

# ---------- keep these in lockstep with plot_single.py ----------
WAVE_EULER_DEG = (90.0, -120.0, 0.0)      # plot_single.py:97  wave-local(sim) -> Blender world
_az_xz_raw     = (600.0, -160.0)          # plot_single.py:169  artist azimuth direction (x,z)
_DOLLY_DIST    = 250.0                     # plot_single.py:170
ELEV_DEG       = 37.4                      # plot_single.py:171
BASE_CAM_EULER_DEG = (296.0, -108.19, -153.6)  # plot_single.py:175
LENS_MM        = 50.0                      # plot_single.py:190 (ZOOM=1)
RES_X, RES_Y   = 1920, 1080               # render resolution (test images)
# ----------------------------------------------------------------

# --- wave object: a proxy at origin carrying the exact sim->world rotation ---
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
wave = bpy.context.active_object
wave.name = "wave"
wave.rotation_euler = tuple(math.radians(a) for a in WAVE_EULER_DEG)
bpy.context.view_layer.update()

# --- camera built VERBATIM as plot_single.py lines 161-192 ---
cam_data = bpy.data.cameras.new(name="Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)

import numpy as np
_az_xz = mathutils.Vector(_az_xz_raw); _az_xz.normalize()
_el    = ELEV_DEG * np.pi/180.0
_horiz = _DOLLY_DIST * np.cos(_el); _height = _DOLLY_DIST * np.sin(_el)
cam.location = (_horiz*_az_xz.x, -_height, _horiz*_az_xz.y)
cam.rotation_euler = tuple(a*np.pi/180 for a in BASE_CAM_EULER_DEG)
cam_data.clip_end = 10000.0
# realign optical axis exactly at origin (minimal rotation, roll preserved)
_base_rot  = cam.rotation_euler.to_matrix()
_fwd       = _base_rot @ mathutils.Vector((0.0, 0.0, -1.0))
_to_origin = (mathutils.Vector((0.0, 0.0, 0.0)) - cam.location).normalized()
_realign   = _fwd.rotation_difference(_to_origin)
cam.rotation_euler = (_realign.to_matrix() @ _base_rot).to_euler()
cam_data.lens = LENS_MM
cam_data.sensor_fit = 'AUTO'
bpy.context.view_layer.update()

# --- express the camera in the DISK (sim) frame ---
Mw   = wave.matrix_world
Rinv = Mw.to_3x3().inverted()
cam_loc_local = Mw.inverted() @ cam.matrix_world.translation
fwd_w = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))
up_w  = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 1,  0))
fwd_l = (Rinv @ fwd_w).normalized()
up_l  = (Rinv @ up_w).normalized()

elev = math.degrees(math.asin(max(-1, min(1, -fwd_l.z))))   # + = above equatorial plane
azim = math.degrees(math.atan2(fwd_l.y, fwd_l.x))           # around orbital axis, 0=+x
zhat = mathutils.Vector((0, 0, 1))
u0   = (zhat - zhat.dot(fwd_l) * fwd_l).normalized()
roll = math.degrees(math.atan2(u0.cross(up_l).dot(fwd_l), u0.dot(up_l)))
dist = cam_loc_local.length

# Blender FOVs.  sensor_fit='AUTO' + landscape -> sensor_width(36) drives the HORIZONTAL angle
# (angle_x is correct/effective). angle_y is NOT the rendered vertical FOV (it uses sensor_height=24);
# the true rendered vertical FOV comes from hfov and the pixel aspect:
hfov = math.degrees(cam_data.angle_x)
vfov = math.degrees(2.0*math.atan(math.tan(math.radians(hfov)/2.0) * RES_Y/RES_X))
vfov_raw = math.degrees(cam_data.angle_y)   # (Blender's misleading sensor_height-based value, for ref)

# --- VisIt View3D (perspective). eye distance in VisIt = parallelScale / tan(viewAngle/2).
#     Match Blender eye distance (=dist) -> parallelScale = dist * tan(vfov/2).
view_normal = (cam_loc_local.normalized())          # focus->camera
view_up     = up_l
view_angle  = vfov                                   # VisIt viewAngle = vertical full FOV
parallel_scale = dist * math.tan(math.radians(vfov)/2.0)

print("\n================= CAMERA IN DISK FRAME (sim coords, M_sun) =================")
print("camera_position :", [round(x, 2) for x in cam_loc_local])
print("look_direction  :", [round(x, 4) for x in fwd_l])
print("up_vector       :", [round(x, 4) for x in up_l])
print("distance_Msun   :", round(dist, 2))
print("elevation_deg   :", round(elev, 2), "(above equatorial/disk plane)")
print("azimuth_deg     :", round(azim, 2), "(around orbital axis, 0=+x)")
print("roll_deg        :", round(roll, 2))
print("HFOV_deg        :", round(hfov, 2), " VFOV_deg(eff):", round(vfov, 2),
      f"  (lens {LENS_MM}mm, {RES_X}x{RES_Y}; Blender angle_y={vfov_raw:.2f} is NOT the render VFOV)")

print("\n================= VisIt View3D (paste into VisIt CLI) =================")
print("# render the disk at %dx%d, perspective, to match the locked mesh camera" % (RES_X, RES_Y))
print("v = GetView3D()")
print("v.viewNormal   = (%.6f, %.6f, %.6f)" % tuple(view_normal))
print("v.focus        = (0.0, 0.0, 0.0)")
print("v.viewUp       = (%.6f, %.6f, %.6f)" % tuple(view_up))
print("v.viewAngle    = %.4f          # vertical full FOV (deg)" % view_angle)
print("v.parallelScale= %.4f          # = dist*tan(vfov/2); sets perspective eye distance" % parallel_scale)
print("v.perspective  = 1")
print("v.nearPlane    = %.2f" % (-2.0*dist))
print("v.farPlane     = %.2f" % ( 2.0*dist))
print("v.imageZoom    = 1")
print("v.imagePan     = (0.0, 0.0)")
print("SetView3D(v)")
print("# also: SaveWindowAtts width=%d height=%d, transparent/no-bg for overlay" % (RES_X, RES_Y))
print("======================================================================\n")
