import bpy
import os
# blender -b finalrotate.blend -P render_all.py
def render_all_frames():
    scene = bpy.context.scene

    # Customize this path – make sure the directory exists
    output_dir = "/data/yliang3/memory/just_for_rendering/rotate/zoomin"  # <-- Change this to your preferred output folder
    filename_prefix = "frame_"            # Optional: change the file name prefix

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save original path to restore later
    original_filepath = scene.render.filepath

    start_frame = scene.frame_start
    end_frame = scene.frame_end

    print(f"Rendering frames {start_frame} to {end_frame} into {output_dir}")

    for frame in range(start_frame, end_frame + 1):
        scene.frame_set(frame)

        # Format: /path/to/output/frame_0001.png
        frame_filename = f"{filename_prefix}{frame:04d}"
        full_path = os.path.join(output_dir, frame_filename)
        scene.render.filepath = full_path

        bpy.ops.render.render(write_still=True)
        print(f"Rendered frame {frame} -> {full_path}")

    # Restore original render path
    scene.render.filepath = original_filepath
    print("Rendering completed.")

if __name__ == "__main__":
    render_all_frames()
