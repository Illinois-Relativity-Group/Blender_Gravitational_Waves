import bpy, mathutils
import os
mat = bpy.data.materials.new(name = "nsns")
mat.use_nodes = True
#initialize nsns node group
def nsns_node_group(image_path):
    image_name = os.path.basename(image_path)

    # Load image if not already in bpy.data.images
    if image_name not in bpy.data.images:
        try:
            bpy.data.images.load(image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {image_path}\n{e}")

    image = bpy.data.images[image_name]

    # Create a new material
    mat = bpy.data.materials.new(name="NSNS_Image_Material")
    mat.use_nodes = True
    nsns = mat.node_tree

    # Clear existing nodes
    for node in nsns.nodes:
        nsns.nodes.remove(node)

    # Image Texture node
    image_texture = nsns.nodes.new("ShaderNodeTexImage")
    image_texture.image = image
    image_texture.interpolation = 'Linear'
    image_texture.projection = 'FLAT'
    image_texture.extension = 'REPEAT'
    image_texture.location = (-400, 300)

    # Principled BSDF node
    principled_bsdf = nsns.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.location = (0, 300)
    principled_bsdf.inputs["Metallic"].default_value = 1.0
    principled_bsdf.inputs["Roughness"].default_value = 1.0
    principled_bsdf.inputs["Emission Strength"].default_value = 1.0

    # Material Output node
    material_output = nsns.nodes.new("ShaderNodeOutputMaterial")
    material_output.location = (300, 300)

    # Connect image color to base color and emission
    nsns.links.new(image_texture.outputs["Color"], principled_bsdf.inputs["Base Color"])
    nsns.links.new(image_texture.outputs["Color"], principled_bsdf.inputs[27])

    # Connect alpha to alpha input
    nsns.links.new(image_texture.outputs["Alpha"], principled_bsdf.inputs["Alpha"])

    # Connect BSDF to output
    nsns.links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

    # Enable transparency in material settings
    #mat.blend_method = 'BLEND'
    #mat.shadow_method = 'NONE'  # Optional: prevents shadow artifacts from alpha

    return mat
