#!/usr/bin/env python3
"""Convert plot_single.py's Blender camera (location + XYZ Euler) into a physical
view: look direction, azimuth / elevation / roll, FOV, and how far the hole
(world origin) sits off the optical axis. Standalone numpy.

Blender Euler order 'XYZ'  ==>  R = Rz @ Ry @ Rx   (verified vs mathutils)."""
import numpy as np

# --- camera from plot_single.py (lines 166-168) ---
loc = np.array([600.0, -475.0, -160.0])           # camera_used.location
euler_deg = np.array([296.0, -108.19, -153.6])    # camera_used.rotation_euler (XYZ), deg
lens_mm, sensor_mm = 50.0, 36.0                    # Blender defaults

a, b, c = np.radians(euler_deg)
Rx = np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
Ry = np.array([[np.cos(b),0,np.sin(b)],[0,1,0],[-np.sin(b),0,np.cos(b)]])
Rz = np.array([[np.cos(c),-np.sin(c),0],[np.sin(c),np.cos(c),0],[0,0,1]])
R = Rz @ Ry @ Rx                                   # Blender 'XYZ'

fwd   = R @ np.array([0., 0., -1.])                # camera looks down its local -Z
up    = R @ np.array([0., 1.,  0.])
right = R @ np.array([1., 0.,  0.])

az = np.degrees(np.arctan2(fwd[1], fwd[0]))        # 0 = +x, CCW
el = np.degrees(np.arcsin(fwd[2]))                 # + = looking up
wZ = np.array([0., 0., 1.])
u0 = wZ - np.dot(wZ, fwd) * fwd; u0 /= np.linalg.norm(u0)
roll = np.degrees(np.arctan2(np.dot(np.cross(u0, up), fwd), np.dot(u0, up)))
hfov = np.degrees(2*np.arctan(sensor_mm/2/lens_mm))

to_hole = -loc / np.linalg.norm(loc)               # hole sits at world origin
off = np.degrees(np.arccos(np.clip(np.dot(fwd, to_hole), -1, 1)))

print(f"camera position        : {loc}   (|r| = {np.linalg.norm(loc):.1f} M_sun from hole)")
print(f"look direction (fwd)   : {np.round(fwd,4)}")
print(f"up                     : {np.round(up,4)}")
print(f"azimuth   (+x=0, CCW)   : {az:.2f} deg")
print(f"elevation (+=up)        : {el:.2f} deg")
print(f"roll                    : {roll:.2f} deg")
print(f"horizontal FOV          : {hfov:.2f} deg   (lens {lens_mm}mm / sensor {sensor_mm}mm)")
print(f"hole(origin) off-axis   : {off:.2f} deg  ->  {'~centered in frame' if off < hfov/2 else 'OFF-FRAME'}")
