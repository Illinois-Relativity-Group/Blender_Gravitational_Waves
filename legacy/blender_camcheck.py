import mathutils, math
e = mathutils.Euler((math.radians(296), math.radians(-108.19), math.radians(-153.6)), 'XYZ')
R = e.to_matrix()
f = R @ mathutils.Vector((0, 0, -1))
u = R @ mathutils.Vector((0, 1, 0))
print("BLENDER_FORWARD", round(f.x, 4), round(f.y, 4), round(f.z, 4))
print("BLENDER_UP", round(u.x, 4), round(u.y, 4), round(u.z, 4))
