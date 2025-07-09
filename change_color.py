import bpy, mathutils
import os
mat = bpy.data.materials.new(name = "ChangeColor")
mat.use_nodes = True
#initialize ChangeColor node group
def changecolor_node_group(frame_number, image_folder):

    image_name = f"hplus_{frame_number:06d}_GW-MEM.png"
    image_path = os.path.join(image_folder, image_name)
    image = bpy.data.images.get(image_name)


    # Load or get the image
    if "output.png" in bpy.data.images:
        image = bpy.data.images["output.png"]
    elif os.path.exists(image_path):
        image = bpy.data.images.load(image_path)
    else:
        print("Image file not found:", image_path)
        image = None

    changecolor = mat.node_tree
    #start with a clean node tree
    for node in changecolor.nodes:
        changecolor.nodes.remove(node)
    changecolor.color_tag = 'NONE'
    changecolor.description = ""
    changecolor.default_group_node_width = 140
    

    #changecolor interface

    #initialize changecolor nodes
    #node Principled BSDF.001
    principled_bsdf_001 = changecolor.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf_001.name = "Principled BSDF.001"
    principled_bsdf_001.distribution = 'MULTI_GGX'
    principled_bsdf_001.subsurface_method = 'RANDOM_WALK'
    #Metallic
    principled_bsdf_001.inputs[1].default_value = 0.0
    #Roughness
    principled_bsdf_001.inputs[2].default_value = 1.0
    #IOR
    principled_bsdf_001.inputs[3].default_value = 1.5
    #Alpha
    principled_bsdf_001.inputs[4].default_value = 0.949999988079071
    #Normal
    principled_bsdf_001.inputs[5].default_value = (0.0, 0.0, 0.0)
    #Diffuse Roughness
    principled_bsdf_001.inputs[7].default_value = 0.0
    #Subsurface Weight
    principled_bsdf_001.inputs[8].default_value = 0.0
    #Subsurface Radius
    principled_bsdf_001.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    #Subsurface Scale
    principled_bsdf_001.inputs[10].default_value = 0.05000000074505806
    #Subsurface Anisotropy
    principled_bsdf_001.inputs[12].default_value = 0.0
    #Specular IOR Level
    principled_bsdf_001.inputs[13].default_value = 0.5
    #Specular Tint
    principled_bsdf_001.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    #Anisotropic
    principled_bsdf_001.inputs[15].default_value = 0.0
    #Anisotropic Rotation
    principled_bsdf_001.inputs[16].default_value = 0.0
    #Tangent
    principled_bsdf_001.inputs[17].default_value = (0.0, 0.0, 0.0)
    #Transmission Weight
    principled_bsdf_001.inputs[18].default_value = 0.0
    #Coat Weight
    principled_bsdf_001.inputs[19].default_value = 0.0
    #Coat Roughness
    principled_bsdf_001.inputs[20].default_value = 0.029999999329447746
    #Coat IOR
    principled_bsdf_001.inputs[21].default_value = 1.5
    #Coat Tint
    principled_bsdf_001.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    #Coat Normal
    principled_bsdf_001.inputs[23].default_value = (0.0, 0.0, 0.0)
    #Sheen Weight
    principled_bsdf_001.inputs[24].default_value = 0.0
    #Sheen Roughness
    principled_bsdf_001.inputs[25].default_value = 0.5
    #Sheen Tint
    principled_bsdf_001.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    #Emission Color
    principled_bsdf_001.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
    #Emission Strength
    principled_bsdf_001.inputs[28].default_value = 0.0
    #Thin Film Thickness
    principled_bsdf_001.inputs[29].default_value = 0.0
    #Thin Film IOR
    principled_bsdf_001.inputs[30].default_value = 1.3300000429153442

    #node Material Output.001
    material_output_001 = changecolor.nodes.new("ShaderNodeOutputMaterial")
    material_output_001.name = "Material Output.001"
    material_output_001.is_active_output = True
    material_output_001.target = 'ALL'
    #Displacement
    material_output_001.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Thickness
    material_output_001.inputs[3].default_value = 0.0

    #node Brick Texture
    brick_texture = changecolor.nodes.new("ShaderNodeTexBrick")
    brick_texture.name = "Brick Texture"
    brick_texture.offset = 0.0
    brick_texture.offset_frequency = 2
    brick_texture.squash = 1.0
    brick_texture.squash_frequency = 2
    #Color1
    brick_texture.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
    #Color2
    brick_texture.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
    #Mortar
    brick_texture.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
    #Scale
    brick_texture.inputs[4].default_value = 0.03999999910593033
    #Mortar Size
    brick_texture.inputs[5].default_value = 0.014999999664723873
    #Mortar Smooth
    brick_texture.inputs[6].default_value = 1.0
    #Bias
    brick_texture.inputs[7].default_value = 0.0
    #Brick Width
    brick_texture.inputs[8].default_value = 0.5
    #Row Height
    brick_texture.inputs[9].default_value = 0.5

    #node Mix Shader
    mix_shader = changecolor.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    #node Mapping.002
    mapping_002 = changecolor.nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    #Location
    mapping_002.inputs[1].default_value = (0.0, 0.0, 0.0)
    #Rotation
    mapping_002.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Scale
    mapping_002.inputs[3].default_value = (1.0, 1.0, 1.0)

    #node Texture Coordinate.002
    texture_coordinate_002 = changecolor.nodes.new("ShaderNodeTexCoord")
    texture_coordinate_002.name = "Texture Coordinate.002"
    texture_coordinate_002.from_instancer = False

    #node Mapping
    mapping = changecolor.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    #Location
    mapping.inputs[1].default_value = (0.699999988079071, 0.0, 0.0)
    #Rotation
    mapping.inputs[2].default_value = (0.0, 1.5707999467849731, 0.0)
    #Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 0.019999999552965164)

    #node Texture Coordinate
    texture_coordinate = changecolor.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    #node Gradient Texture
    gradient_texture = changecolor.nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    #node Color Ramp
    color_ramp = changecolor.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.0
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (0.019999999552965164, 0.019999999552965164, 0.08399999886751175, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.9950000047683716)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (0.2619999945163727, 0.7009999752044678, 1.0, 1.0)


    #node Image Texture
    image_texture = changecolor.nodes.new("ShaderNodeTexImage")
    image_texture.name = "Image Texture"
    image_texture.extension = 'REPEAT'
    image_texture.image = image
    image_texture.image_user.frame_current = 1
    image_texture.image_user.frame_duration = 1
    image_texture.image_user.frame_offset = -1
    image_texture.image_user.frame_start = 1
    image_texture.image_user.tile = 0
    image_texture.image_user.use_auto_refresh = False
    image_texture.image_user.use_cyclic = False
    image_texture.interpolation = 'Linear'
    image_texture.projection = 'FLAT'
    image_texture.projection_blend = 0.0

    #node Mapping.001
    mapping_001 = changecolor.nodes.new("ShaderNodeMapping")
    mapping_001.name = "Mapping.001"
    mapping_001.vector_type = 'POINT'
    #Location
    mapping_001.inputs[1].default_value = (0.0, 0.0, 0.0)
    #Rotation
    mapping_001.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Scale
    mapping_001.inputs[3].default_value = (1.0, 1.0, 1.0)

    #node Texture Coordinate.001
    texture_coordinate_001 = changecolor.nodes.new("ShaderNodeTexCoord")
    texture_coordinate_001.name = "Texture Coordinate.001"
    texture_coordinate_001.from_instancer = False

    #node Mix
    mix = changecolor.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'
    #A_Color
    #mix.inputs[6].default_value = (0.5, 0.06, 0.22, 1.0) #Read
    mix.inputs[6].default_value = (0, 1, 0.17, 1.0) #Green

    #Set locations
    principled_bsdf_001.location = (904.1597290039062, 235.47091674804688)
    material_output_001.location = (2317.1142578125, 228.12698364257812)
    brick_texture.location = (1010.0, -220.0)
    mix_shader.location = (1610.0, 90.0)
    mapping_002.location = (770.0, -330.0)
    texture_coordinate_002.location = (550.0, -380.0)
    mapping.location = (-185.0, 505.0)
    texture_coordinate.location = (-365.0, 505.0)
    gradient_texture.location = (10.0, 415.0)
    color_ramp.location = (294.4573974609375, 427.4915771484375)
    image_texture.location = (399.491455078125, 154.01968383789062)
    mapping_001.location = (219.491455078125, 114.01968383789062)
    texture_coordinate_001.location = (39.491455078125, 114.01968383789062)
    mix.location = (691.68896484375, 166.12548828125)

    #Set dimensions
    principled_bsdf_001.width, principled_bsdf_001.height = 240.0, 100.0
    material_output_001.width, material_output_001.height = 140.0, 100.0
    brick_texture.width, brick_texture.height = 150.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    mapping_002.width, mapping_002.height = 140.0, 100.0
    texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    image_texture.width, image_texture.height = 240.0, 100.0
    mapping_001.width, mapping_001.height = 140.0, 100.0
    texture_coordinate_001.width, texture_coordinate_001.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0

    #initialize changecolor links
    #mapping_002.Vector -> brick_texture.Vector
    changecolor.links.new(mapping_002.outputs[0], brick_texture.inputs[0])
    #brick_texture.Color -> mix_shader.Fac
    changecolor.links.new(brick_texture.outputs[0], mix_shader.inputs[0])
    #principled_bsdf_001.BSDF -> mix_shader.Shader
    changecolor.links.new(principled_bsdf_001.outputs[0], mix_shader.inputs[2])
    #texture_coordinate_002.Object -> mapping_002.Vector
    changecolor.links.new(texture_coordinate_002.outputs[3], mapping_002.inputs[0])
    #texture_coordinate.Object -> mapping.Vector
    changecolor.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    #mapping.Vector -> gradient_texture.Vector
    changecolor.links.new(mapping.outputs[0], gradient_texture.inputs[0])
    #gradient_texture.Color -> color_ramp.Fac
    changecolor.links.new(gradient_texture.outputs[0], color_ramp.inputs[0])
    #mapping_001.Vector -> image_texture.Vector
    changecolor.links.new(mapping_001.outputs[0], image_texture.inputs[0])
    #texture_coordinate_001.Generated -> mapping_001.Vector
    changecolor.links.new(texture_coordinate_001.outputs[0], mapping_001.inputs[0])
    #image_texture.Color -> mix.Factor
    changecolor.links.new(image_texture.outputs[0], mix.inputs[0])
    #mix.Result -> principled_bsdf_001.Base Color
    changecolor.links.new(mix.outputs[2], principled_bsdf_001.inputs[0])
    #mix_shader.Shader -> material_output_001.Surface
    changecolor.links.new(mix_shader.outputs[0], material_output_001.inputs[0])
    #color_ramp.Color -> mix.B
    changecolor.links.new(color_ramp.outputs[0], mix.inputs[7])
    return mat

#changecolor = changecolor_node_group(frame_number, image_folder)


def nsns_node_group(image_path):
    import os

    # Ensure image is loaded into Blender
    image_name = os.path.basename(image_path)
    if image_name not in bpy.data.images:
        try:
            bpy.data.images.load(image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load image '{image_path}': {e}")
    image = bpy.data.images[image_name]

    # Create a new material
    mat = bpy.data.materials.new(name="NSNS_Material")
    mat.use_nodes = True

    # Access node tree and clear default nodes
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Create nodes
    image_node = nodes.new(type='ShaderNodeTexImage')
    image_node.image = image

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')

    # Position nodes
    image_node.location = (-400, 0)
    bsdf.location = (0, 0)
    output.location = (200, 0)

    # Link nodes
    links.new(image_node.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    

    return mat


'''
import bpy, mathutils

mat = bpy.data.materials.new(name = "nsns")
mat.use_nodes = True
#initialize nsns node group
def nsns_node_group(image_path):
    image_name = os.path.basename(image_path)
    if image_name not in bpy.data.images:
        try:
            bpy.data.images.load(image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {image_path}\n{e}")

    image = bpy.data.images[image_name]
    
    nsns = mat.node_tree
    #start with a clean node tree
    for node in nsns.nodes:
        nsns.nodes.remove(node)
    nsns.color_tag = 'NONE'
    nsns.description = ""
    nsns.default_group_node_width = 140
    

    #nsns interface

    #initialize nsns nodes
    #node Principled BSDF
    principled_bsdf = nsns.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'MULTI_GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK'
    #Metallic
    principled_bsdf.inputs[1].default_value = 1.0
    #Roughness
    principled_bsdf.inputs[2].default_value = 1.0
    #IOR
    principled_bsdf.inputs[3].default_value = 1.5
    #Normal
    principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
    #Diffuse Roughness
    principled_bsdf.inputs[7].default_value = 0.0
    #Subsurface Weight
    principled_bsdf.inputs[8].default_value = 0.0
    #Subsurface Radius
    principled_bsdf.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    #Subsurface Scale
    principled_bsdf.inputs[10].default_value = 0.05000000074505806
    #Subsurface Anisotropy
    principled_bsdf.inputs[12].default_value = 0.0
    #Specular IOR Level
    principled_bsdf.inputs[13].default_value = 0.5
    #Specular Tint
    principled_bsdf.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
    #Anisotropic
    principled_bsdf.inputs[15].default_value = 0.0
    #Anisotropic Rotation
    principled_bsdf.inputs[16].default_value = 0.0
    #Tangent
    principled_bsdf.inputs[17].default_value = (0.0, 0.0, 0.0)
    #Transmission Weight
    principled_bsdf.inputs[18].default_value = 0.0
    #Coat Weight
    principled_bsdf.inputs[19].default_value = 0.0
    #Coat Roughness
    principled_bsdf.inputs[20].default_value = 0.029999999329447746
    #Coat IOR
    principled_bsdf.inputs[21].default_value = 1.5
    #Coat Tint
    principled_bsdf.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
    #Coat Normal
    principled_bsdf.inputs[23].default_value = (0.0, 0.0, 0.0)
    #Sheen Weight
    principled_bsdf.inputs[24].default_value = 0.0
    #Sheen Roughness
    principled_bsdf.inputs[25].default_value = 0.5
    #Sheen Tint
    principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
    #Emission Strength
    principled_bsdf.inputs[28].default_value = 0.800000011920929
    #Thin Film Thickness
    principled_bsdf.inputs[29].default_value = 0.0
    #Thin Film IOR
    principled_bsdf.inputs[30].default_value = 1.3300000429153442

    #node Material Output
    material_output = nsns.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    #Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Thickness
    material_output.inputs[3].default_value = 0.0

    #node Image Texture
    image_texture = nsns.nodes.new("ShaderNodeTexImage")
    image_texture.name = "Image Texture"
    image_texture.extension = 'REPEAT'
    if "memory_001_000_0000.png" in bpy.data.images:
        image_texture.image = bpy.data.images[image]
    image_texture.image_user.frame_current = 0
    image_texture.image_user.frame_duration = 1
    image_texture.image_user.frame_offset = -1
    image_texture.image_user.frame_start = 1
    image_texture.image_user.tile = 0
    image_texture.image_user.use_auto_refresh = False
    image_texture.image_user.use_cyclic = False
    image_texture.interpolation = 'Linear'
    image_texture.projection = 'FLAT'
    image_texture.projection_blend = 0.0
    #Vector
    image_texture.inputs[0].default_value = (0.0, 0.0, 0.0)


    #Set locations
    principled_bsdf.location = (10.0, 300.0)
    material_output.location = (300.0, 300.0)
    image_texture.location = (-379.52569580078125, 264.8343200683594)

    #Set dimensions
    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
    material_output.width, material_output.height = 140.0, 100.0
    image_texture.width, image_texture.height = 240.0, 100.0

    #initialize nsns links
    #image_texture.Color -> principled_bsdf.Base Color
    nsns.links.new(image_texture.outputs[0], principled_bsdf.inputs[0])
    #principled_bsdf.BSDF -> material_output.Surface
    nsns.links.new(principled_bsdf.outputs[0], material_output.inputs[0])
    #image_texture.Alpha -> principled_bsdf.Alpha
    nsns.links.new(image_texture.outputs[1], principled_bsdf.inputs[4])
    #image_texture.Color -> principled_bsdf.Emission Color
    nsns.links.new(image_texture.outputs[0], principled_bsdf.inputs[27])
    return mat


'''