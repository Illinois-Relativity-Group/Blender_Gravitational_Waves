import bpy, mathutils, math
bpy.ops.wm.open_mainfile(filepath="/anvil/scratch/x-yguo11/blender_gw_dev/render_fix/final.blend")
cam = bpy.data.objects.get("Camera")
wave = bpy.data.objects.get("wave")

mw = cam.matrix_world
loc = mw.translation
fwd = (mw.to_3x3() @ mathutils.Vector((0,0,-1))).normalized()
up  = (mw.to_3x3() @ mathutils.Vector((0,1,0))).normalized()
print("CAM_LOC", [round(x,2) for x in loc])
print("CAM_FWD", [round(x,4) for x in fwd])
print("CAM_UP", [round(x,4) for x in up])
print("CAM_EULER_deg", [round(math.degrees(a),2) for a in cam.rotation_euler])
print("CAM_FOV_deg", round(math.degrees(cam.data.angle),2), "LENS", cam.data.lens)

to_hole = (mathutils.Vector((0,0,0)) - loc).normalized()
print("HOLE_OFF_AXIS_deg", round(math.degrees(fwd.angle(to_hole)),2))
print("CAM_DIST_TO_HOLE", round(loc.length,1))

if wave:
    n = (wave.matrix_world.to_3x3() @ mathutils.Vector((0,0,1))).normalized()
    print("DISK_PLANE_NORMAL", [round(x,4) for x in n])
    graze = abs(90 - math.degrees(fwd.angle(n)))
    print("VIEW_ELEVATION_ABOVE_DISK_deg", round(graze,2))
else:
    print("(no 'wave' object in file)")
