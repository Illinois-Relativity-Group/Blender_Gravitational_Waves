import bpy, mathutils, math
bpy.ops.wm.open_mainfile(filepath="/anvil/scratch/x-yguo11/blender_gw_dev/render_fix/final.blend")
cam  = bpy.data.objects["Camera"]
wave = bpy.data.objects["wave"]

Mw   = wave.matrix_world            # wave-local -> world (local x,y = equatorial/sim coords; local z = orbital axis)
Rinv = Mw.to_3x3().inverted()

cam_loc_local = Mw.inverted() @ cam.matrix_world.translation
fwd_w = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))
up_w  = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 1,  0))
fwd_l = (Rinv @ fwd_w).normalized()
up_l  = (Rinv @ up_w).normalized()

elev = math.degrees(math.asin(max(-1, min(1, -fwd_l.z))))   # + = camera above the equatorial plane
azim = math.degrees(math.atan2(fwd_l.y, fwd_l.x))           # around the orbital axis, 0 = +x
zhat = mathutils.Vector((0, 0, 1))
u0 = (zhat - zhat.dot(fwd_l) * fwd_l).normalized()
roll = math.degrees(math.atan2(u0.cross(up_l).dot(fwd_l), u0.dot(up_l)))
look_at = cam_loc_local + fwd_l * cam_loc_local.length

print("=== camera in DISK frame (equatorial/sim coords, M_sun) ===")
print("camera_position :", [round(x, 1) for x in cam_loc_local])
print("look_direction  :", [round(x, 4) for x in fwd_l])
print("up_vector       :", [round(x, 4) for x in up_l])
print("look_at (approx):", [round(x, 1) for x in look_at])
print("elevation_deg   :", round(elev, 2), "(above equatorial plane)")
print("azimuth_deg     :", round(azim, 2), "(around orbital axis, 0=+x)")
print("roll_deg        :", round(roll, 2))
print("distance_Msun   :", round(cam_loc_local.length, 1))
print("FOV_deg         :", round(math.degrees(cam.data.angle), 2))
