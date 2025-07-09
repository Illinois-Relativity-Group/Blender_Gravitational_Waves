import bpy
import mathutils

def shader_gridwb_node_group():
    # Create a new material and enable nodes
    mat = bpy.data.materials.new(name="shader_gridwb")
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    # Remove any existing nodes
    for node in nodes:
        nodes.remove(node)
    node_tree.color_tag = 'NONE'
    node_tree.description = ""

    # ---------------------------------------
    # Principled BSDF Node
    # ---------------------------------------
    principled_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'MULTI_GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK'

    # Set inputs by name
    principled_bsdf.inputs["Base Color"].default_value =  (0.05, 0.55, 1.0, 1.0) # (0.125, 0.60, 1.0, 1.0) (0.125, 0.50, 0.85, 1.0) (0.125, 0.395, 0.775, 1.0) (0.125, 0.392, 0.722, 1.0) (0.23, 0.55, 0.712, 1.0) (0.212, 0.512, 1.0, 1.0)
    principled_bsdf.inputs["Metallic"].default_value = 0.0
    principled_bsdf.inputs["Roughness"].default_value = 1.0
    principled_bsdf.inputs["IOR"].default_value = 1.5
    principled_bsdf.inputs["Alpha"].default_value = 0.6 #1
    principled_bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.2, 0.1)
    principled_bsdf.inputs["Subsurface Scale"].default_value = 0.05

    # Try to set the clearcoat/coat roughness
    try:
        principled_bsdf.inputs["Clearcoat Roughness"].default_value = 0.03
    except KeyError:
        # Fallback: try using "Coat Roughness" instead
        try:
            principled_bsdf.inputs["Coat Roughness"].default_value = 0.03
        except KeyError:
            print("Neither 'Clearcoat Roughness' nor 'Coat Roughness' socket found in Principled BSDF node.")

    # ---------------------------------------
    # Material Output Node
    # ---------------------------------------
    material_output = nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Set displacement and thickness (these inputs are still by index)
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)  # Displacement
    material_output.inputs[3].default_value = 0.0              # Thickness

    # ---------------------------------------
    # Brick Texture Node
    # ---------------------------------------
    brick_texture = nodes.new("ShaderNodeTexBrick")
    brick_texture.name = "Brick Texture"
    brick_texture.offset = 0.0
    brick_texture.offset_frequency = 2
    brick_texture.squash = 1.0
    brick_texture.squash_frequency = 2
    brick_texture.inputs["Color1"].default_value = (1.0, 1.0, 1.0, 1.0)
    brick_texture.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
    brick_texture.inputs["Mortar"].default_value = (0.0, 0.0, 0.0, 1.0)
    brick_texture.inputs["Scale"].default_value = 0.02
    brick_texture.inputs["Mortar Size"].default_value = 0.02
    brick_texture.inputs["Mortar Smooth"].default_value = 1.0
    brick_texture.inputs["Bias"].default_value = 0.0
    brick_texture.inputs["Brick Width"].default_value = 0.5
    brick_texture.inputs["Row Height"].default_value = 0.5

    # ---------------------------------------
    # Mix Shader Node
    # ---------------------------------------
    mix_shader = nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # ---------------------------------------
    # Mapping Node
    # ---------------------------------------
    mapping_002 = nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    mapping_002.inputs["Location"].default_value = (0.0, 0.0, 0.0)
    mapping_002.inputs["Rotation"].default_value = (0.0, 0.0, 0.0)
    mapping_002.inputs["Scale"].default_value = (1.0, 1.0, 1.0)

    # ---------------------------------------
    # Texture Coordinate Node
    # ---------------------------------------
    texture_coordinate_002 = nodes.new("ShaderNodeTexCoord")
    texture_coordinate_002.name = "Texture Coordinate.002"
    texture_coordinate_002.from_instancer = False

    # ---------------------------------------
    # Set Node Locations and Dimensions
    # ---------------------------------------
    principled_bsdf.location = (578.84, 456.77)
    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0

    material_output.location = (1770.98, 307.56)
    material_output.width, material_output.height = 140.0, 100.0

    brick_texture.location = (859.08, -139.32)
    brick_texture.width, brick_texture.height = 150.0, 100.0

    mix_shader.location = (1427.77, 370.98)
    mix_shader.width, mix_shader.height = 140.0, 100.0

    mapping_002.location = (704.40, -249.57)
    mapping_002.width, mapping_002.height = 140.0, 100.0

    texture_coordinate_002.location = (480.25, -298.47)
    texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0

    # ---------------------------------------
    # Create Links Between Nodes
    # ---------------------------------------
    # Mapping Vector -> Brick Texture Vector
    links.new(mapping_002.outputs["Vector"], brick_texture.inputs["Vector"])
    # Brick Texture Color -> Mix Shader Fac (mix factor)
    links.new(brick_texture.outputs["Color"], mix_shader.inputs["Fac"])
    # Principled BSDF -> Mix Shader (for the "true" shader)
    links.new(principled_bsdf.outputs["BSDF"], mix_shader.inputs[2])
    # Mix Shader -> Material Output Surface
    links.new(mix_shader.outputs["Shader"], material_output.inputs["Surface"])
    # Texture Coordinate Object -> Mapping Vector
    links.new(texture_coordinate_002.outputs["Object"], mapping_002.inputs["Vector"])

    return mat

def shader_twoblue():
    # Create a new material and enable nodes
    mat = bpy.data.materials.new(name="shader_gridwb")
    mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Clear any existing nodes in the node tree
    for node in nodes:
        nodes.remove(node)
    nt.color_tag = 'NONE'
    nt.description = ""
    #nt.default_group_node_width = 140

    # ---------------------------------------
    # Create Nodes
    # ---------------------------------------
    # Principled BSDF Node
    principled_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'MULTI_GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK'
    # Set inputs (by index):
    #  0: Base Color, 1: Metallic, 2: Roughness, 3: IOR, 4: Alpha, 5: Normal, etc.
    principled_bsdf.inputs[1].default_value = 0  # Metallic
    principled_bsdf.inputs[2].default_value = 1.0  # Roughness
    principled_bsdf.inputs[3].default_value = 1.5  # IOR
    principled_bsdf.inputs[4].default_value = 0.6000000238418579  # Alpha
    principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)  # Normal
    principled_bsdf.inputs[7].default_value = 0.0  # Diffuse Roughness
    principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)  # Sheen Tint
    #principled_bsdf.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)  # Emission Color
    principled_bsdf.inputs[28].default_value = 0  # Emission Strength


    # Material Output Node
    material_output = nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement & Thickness (set by index)
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)  # Displacement
    material_output.inputs[3].default_value = 0.0              # Thickness

    # Brick Texture Node
    brick_texture = nodes.new("ShaderNodeTexBrick")
    brick_texture.name = "Brick Texture"
    brick_texture.offset = 0.0
    brick_texture.offset_frequency = 2
    brick_texture.squash = 1.0
    brick_texture.squash_frequency = 2
    brick_texture.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)  # Color1
    brick_texture.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)  # Color2
    brick_texture.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)  # Mortar
    brick_texture.inputs[4].default_value = 0.019999999552965164   # Scale
    brick_texture.inputs[5].default_value = 0.019999999552965164   # Mortar Size
    brick_texture.inputs[6].default_value = 1.0                    # Mortar Smooth
    brick_texture.inputs[7].default_value = 0.0                    # Bias
    brick_texture.inputs[8].default_value = 0.5                    # Brick Width
    brick_texture.inputs[9].default_value = 0.5                    # Row Height

    # Mix Shader Node
    mix_shader = nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # Mapping.002 Node
    mapping_002 = nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    mapping_002.inputs[1].default_value = (0.0, 0.0, 0.0)  # Location
    mapping_002.inputs[2].default_value = (0.0, 0.0, 0.0)  # Rotation
    mapping_002.inputs[3].default_value = (1.0, 1.0, 1.0)  # Scale

    # Texture Coordinate.002 Node
    texture_coordinate_002 = nodes.new("ShaderNodeTexCoord")
    texture_coordinate_002.name = "Texture Coordinate.002"
    texture_coordinate_002.from_instancer = False

    # Mapping Node ("Mapping")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    mapping.inputs[1].default_value = (0.7999999523162842, 0.0, 0.0)      # Location
    mapping.inputs[2].default_value = (0.0, 1.5707963705062866, 0.0)      # Rotation
    mapping.inputs[3].default_value = (1.0, 1.0, 0.10000000149011612)      # Scale

    # Texture Coordinate Node ("Texture Coordinate")
    texture_coordinate = nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # Gradient Texture Node
    gradient_texture = nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    # Color Ramp Node
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'
    # Remove the default element and adjust the remaining one
    if len(color_ramp.color_ramp.elements) > 0:
        color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_elem0 = color_ramp.color_ramp.elements[0]
    color_ramp_elem0.position = 0.0
    color_ramp_elem0.alpha = 1.0
    color_ramp_elem0.color = (0.02, 0.02, 0.084, 1.0) #(0.00575070409104228, 0.008538820780813694, 0.08383253961801529, 1.0)
    # Add a new element
    color_ramp_elem1 = color_ramp.color_ramp.elements.new(0.9954545497894287)
    color_ramp_elem1.alpha = 1.0
    color_ramp_elem1.color = (0.2624173164367676, 0.7011075019836426, 1.0, 1.0) #(0.02, 0.02, 0.084, 1.0)

    # ---------------------------------------
    # Set Node Locations and Dimensions
    # ---------------------------------------
    principled_bsdf.location = (578.8400268554688, 456.7699890136719)
    material_output.location = (1770.97998046875, 307.55999755859375)
    brick_texture.location = (935.1474609375, -135.85948181152344)
    mix_shader.location = (1427.77001953125, 370.9800109863281)
    mapping_002.location = (704.4000244140625, -249.57000732421875)
    texture_coordinate_002.location = (480.25, -298.4700012207031)
    mapping.location = (-257.5921630859375, 588.22216796875)
    texture_coordinate.location = (-437.5921630859375, 588.22216796875)
    gradient_texture.location = (-65.7235107421875, 496.15118408203125)
    color_ramp.location = (158.10513305664062, 461.08148193359375)

    # Dimensions
    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
    material_output.width, material_output.height = 140.0, 100.0
    brick_texture.width, brick_texture.height = 150.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    mapping_002.width, mapping_002.height = 140.0, 100.0
    texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0

    # ---------------------------------------
    # Create Links Between Nodes
    # ---------------------------------------
    links.new(mapping_002.outputs[0], brick_texture.inputs[0])         # Mapping.002.Vector -> Brick Texture.Vector
    links.new(brick_texture.outputs[0], mix_shader.inputs[0])            # Brick Texture.Color -> Mix Shader.Fac
    links.new(principled_bsdf.outputs[0], mix_shader.inputs[2])           # Principled BSDF.BSDF -> Mix Shader.Shader
    links.new(mix_shader.outputs[0], material_output.inputs[0])           # Mix Shader.Shader -> Material Output.Surface
    links.new(texture_coordinate_002.outputs[3], mapping_002.inputs[0])   # Texture Coordinate.002.Object -> Mapping.002.Vector
    links.new(texture_coordinate.outputs[3], mapping.inputs[0])           # Texture Coordinate.Object -> Mapping.Vector
    links.new(mapping.outputs[0], gradient_texture.inputs[0])             # Mapping.Vector -> Gradient Texture.Vector
    links.new(gradient_texture.outputs[0], color_ramp.inputs[0])            # Gradient Texture.Color -> Color Ramp.Fac
    links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])             # Color Ramp.Color -> Principled BSDF.Base Color

    return mat

def shader_twoblue_2():
    # Create a new material and enable nodes
    mat = bpy.data.materials.new(name="two_blue_2")
    mat.use_nodes = True
    nt = mat.node_tree

    # Start with a clean node tree
    for node in nt.nodes:
        nt.nodes.remove(node)
    nt.color_tag = 'NONE'
    nt.description = ""
    #nt.default_group_node_width = 140

    # ------------------------------
    # Create Nodes
    # ------------------------------
    # Principled BSDF Node
    principled_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'MULTI_GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK'
    principled_bsdf.inputs[1].default_value = 0.0   # Metallic
    principled_bsdf.inputs[2].default_value = 1.0   # Roughness
    principled_bsdf.inputs[3].default_value = 1.5   # IOR
    principled_bsdf.inputs[4].default_value = 0.6000000238418579   # Alpha
    principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)       # Normal
    principled_bsdf.inputs[7].default_value = 0.0   # Diffuse Roughness
    principled_bsdf.inputs[28].default_value = 0     # Emission Strength


    # Material Output Node
    material_output = nt.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)  # Displacement
    material_output.inputs[3].default_value = 0.0              # Thickness

    # Brick Texture Node
    brick_texture = nt.nodes.new("ShaderNodeTexBrick")
    brick_texture.name = "Brick Texture"
    brick_texture.offset = 0.0
    brick_texture.offset_frequency = 2
    brick_texture.squash = 1.0
    brick_texture.squash_frequency = 2
    brick_texture.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)  # Color1
    brick_texture.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)  # Color2
    brick_texture.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)  # Mortar
    brick_texture.inputs[4].default_value = 0.02    # Scale
    brick_texture.inputs[5].default_value = 0.02    # Mortar Size
    brick_texture.inputs[6].default_value = 1.0     # Mortar Smooth
    brick_texture.inputs[7].default_value = 0.0     # Bias
    brick_texture.inputs[8].default_value = 0.5     # Brick Width
    brick_texture.inputs[9].default_value = 0.5     # Row Height

    # Mix Shader Node
    mix_shader = nt.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # Mapping.002 Node
    mapping_002 = nt.nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    mapping_002.inputs[1].default_value = (0.0, 0.0, 0.0)  # Location
    mapping_002.inputs[2].default_value = (0.0, 0.0, 0.0)  # Rotation
    mapping_002.inputs[3].default_value = (1.0, 1.0, 1.0)  # Scale

    # Texture Coordinate.002 Node
    texture_coordinate_002 = nt.nodes.new("ShaderNodeTexCoord")
    texture_coordinate_002.name = "Texture Coordinate.002"
    texture_coordinate_002.from_instancer = False

    # Mapping Node
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    mapping.inputs[1].default_value = (0.8, 0.0, 0.0)          # Location
    mapping.inputs[2].default_value = (0.0, 1.5708, 0.0)         # Rotation
    mapping.inputs[3].default_value = (1.0, 1.0, 0.05)            # Scale

    # Texture Coordinate Node
    texture_coordinate = nt.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # Gradient Texture Node
    gradient_texture = nt.nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    # Color Ramp Node
    color_ramp = nt.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    # Initialize Color Ramp Elements
    if color_ramp.color_ramp.elements:
        #Remove the default element
        color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_elem0 = color_ramp.color_ramp.elements[0]
    color_ramp_elem0.position = 0.0
    color_ramp_elem0.alpha = 1.0
    color_ramp_elem0.color = (0.02, 0.02, 0.084, 1.0)
    color_ramp_elem1 = color_ramp.color_ramp.elements.new(1)
    color_ramp_elem1.alpha = 1.0
    color_ramp_elem1.color = (0.094, 0.639, 1, 1.0)

    # ------------------------------
    # Set Node Locations & Dimensions
    # ------------------------------
    principled_bsdf.location = (578.84, 456.77)
    material_output.location = (1770.98, 307.56)
    brick_texture.location = (935.15, -135.86)
    mix_shader.location = (1427.77, 370.98)
    mapping_002.location = (704.40, -249.57)
    texture_coordinate_002.location = (480.25, -298.47)
    mapping.location = (-257.59, 588.22)
    texture_coordinate.location = (-437.59, 588.22)
    gradient_texture.location = (-65.72, 496.15)
    color_ramp.location = (158.11, 461.08)

    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
    material_output.width, material_output.height = 140.0, 100.0
    brick_texture.width, brick_texture.height = 150.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    mapping_002.width, mapping_002.height = 140.0, 100.0
    texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0

    # ------------------------------
    # Create Links Between Nodes
    # ------------------------------
    nt.links.new(mapping_002.outputs[0], brick_texture.inputs[0])
    nt.links.new(brick_texture.outputs[0], mix_shader.inputs[0])
    nt.links.new(principled_bsdf.outputs[0], mix_shader.inputs[2])
    nt.links.new(texture_coordinate_002.outputs[3], mapping_002.inputs[0])
    nt.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    nt.links.new(mapping.outputs[0], gradient_texture.inputs[0])
    nt.links.new(gradient_texture.outputs[0], color_ramp.inputs[0])
    nt.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
    nt.links.new(color_ramp.outputs[0], principled_bsdf.inputs[27])
    nt.links.new(mix_shader.outputs[0], material_output.inputs[0])

    return mat



def shader_twoblue_3():

    two_blue_3 = mat.node_tree
    #start with a clean node tree
    for node in two_blue_3.nodes:
        two_blue_3.nodes.remove(node)
    two_blue_3.color_tag = 'NONE'
    two_blue_3.description = ""
    #two_blue_3.default_group_node_width = 140
    

    #two_blue_3 interface

    #initialize two_blue_3 nodes
    #node Principled BSDF
    principled_bsdf = two_blue_3.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'MULTI_GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK'
    #Metallic
    principled_bsdf.inputs[1].default_value = 0.0
    #Roughness
    principled_bsdf.inputs[2].default_value = 1.0
    #IOR
    principled_bsdf.inputs[3].default_value = 1.5
    #Alpha
    principled_bsdf.inputs[4].default_value = 0.95
    #Normal
    principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
    #Diffuse Roughness
    principled_bsdf.inputs[7].default_value = 0.0



    #node Material Output
    material_output = two_blue_3.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    #Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Thickness
    material_output.inputs[3].default_value = 0.0

    #node Brick Texture
    brick_texture = two_blue_3.nodes.new("ShaderNodeTexBrick")
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
    brick_texture.inputs[4].default_value = 0.019999999552965164
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
    mix_shader = two_blue_3.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    #node Mapping.002
    mapping_002 = two_blue_3.nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    #Location
    mapping_002.inputs[1].default_value = (0.0, 0.0, 0.0)
    #Rotation
    mapping_002.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Scale
    mapping_002.inputs[3].default_value = (1.0, 1.0, 1.0)

    #node Texture Coordinate.002
    texture_coordinate_002 = two_blue_3.nodes.new("ShaderNodeTexCoord")
    texture_coordinate_002.name = "Texture Coordinate.002"
    texture_coordinate_002.from_instancer = False

    #node Mapping
    mapping = two_blue_3.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    #Location
    mapping.inputs[1].default_value = (0.6999999284744263, 0.0, 0.0)
    #Rotation
    mapping.inputs[2].default_value = (0.0, 1.5707999467849731, 0.0)
    #Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 0.019999999552965164)

    #node Texture Coordinate
    texture_coordinate = two_blue_3.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    #node Gradient Texture
    gradient_texture = two_blue_3.nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    #node Color Ramp
    color_ramp = two_blue_3.nodes.new("ShaderNodeValToRGB")
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

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.9954545497894287)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (0.2624173164367676, 0.7011075019836426, 1.0, 1.0)



    #Set locations
    principled_bsdf.location = (663.3345947265625, 166.83021545410156)
    material_output.location = (1843.4039306640625, 226.01443481445312)
    brick_texture.location = (1007.573974609375, -217.40557861328125)
    mix_shader.location = (1614.865234375, 93.1209716796875)
    mapping_002.location = (776.823974609375, -331.1155700683594)
    texture_coordinate_002.location = (552.6739501953125, -380.01556396484375)
    mapping.location = (-185.16607666015625, 506.6744079589844)
    texture_coordinate.location = (-365.16607666015625, 506.6744079589844)
    gradient_texture.location = (6.70391845703125, 414.60443115234375)
    color_ramp.location = (230.53392028808594, 379.534423828125)

    #Set dimensions
    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
    material_output.width, material_output.height = 140.0, 100.0
    brick_texture.width, brick_texture.height = 150.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    mapping_002.width, mapping_002.height = 140.0, 100.0
    texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0

    #initialize two_blue_3 links
    #mapping_002.Vector -> brick_texture.Vector
    two_blue_3.links.new(mapping_002.outputs[0], brick_texture.inputs[0])
    #brick_texture.Color -> mix_shader.Fac
    two_blue_3.links.new(brick_texture.outputs[0], mix_shader.inputs[0])
    #principled_bsdf.BSDF -> mix_shader.Shader
    two_blue_3.links.new(principled_bsdf.outputs[0], mix_shader.inputs[2])
    #texture_coordinate_002.Object -> mapping_002.Vector
    two_blue_3.links.new(texture_coordinate_002.outputs[3], mapping_002.inputs[0])
    #texture_coordinate.Object -> mapping.Vector
    two_blue_3.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    #mapping.Vector -> gradient_texture.Vector
    two_blue_3.links.new(mapping.outputs[0], gradient_texture.inputs[0])
    #gradient_texture.Color -> color_ramp.Fac
    two_blue_3.links.new(gradient_texture.outputs[0], color_ramp.inputs[0])
    #color_ramp.Color -> principled_bsdf.Base Color
    two_blue_3.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
    #color_ramp.Color -> principled_bsdf.Emission Color
    two_blue_3.links.new(color_ramp.outputs[0], principled_bsdf.inputs[26])
    #mix_shader.Shader -> material_output.Surface
    two_blue_3.links.new(mix_shader.outputs[0], material_output.inputs[0])
    return mat




def blue():
    mat_name = "Blue"
    
    # If the material already exists, return it
    if mat_name in bpy.data.materials:
        return bpy.data.materials[mat_name]
    
    # Create a new material and enable nodes
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Clear all default nodes
    nodes.clear()
    
    # Create a Principled BSDF node
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (0, 0)
    # Set the base color to light blue (e.g., RGB 173,216,230 normalized to 0-1)
    #bsdf_node.inputs["Base Color"].default_value = (0.678, 0.847, 0.902, 1)
    bsdf_node.inputs["Base Color"].default_value = (0.11, 0.25, 0.9, 1)
    #bsdf_node.inputs["Base Color"].default_value = (0.05, 0.55, 1.0, 1.0)
    bsdf_node.inputs["Roughness"].default_value = 1.0
    bsdf_node.inputs["Metallic"].default_value = 0.0
    bsdf_node.inputs["Alpha"].default_value = 0.6
    # Create a Material Output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (300, 0)
    
    # Link the BSDF shader output to the material output's surface input
    links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])
    
    return mat





import bpy, mathutils

mat = bpy.data.materials.new(name = "two_color_blue_red")
mat.use_nodes = True
#initialize two_color_blue_red node group
def two_color_blue_red_node_group():
    mat = bpy.data.materials.new(name="two_color_blue_red_node_group")
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    two_color_blue_red = mat.node_tree
    #start with a clean node tree
    for node in two_color_blue_red.nodes:
        two_color_blue_red.nodes.remove(node)
    two_color_blue_red.color_tag = 'NONE'
    two_color_blue_red.description = ""
    #two_color_blue_red.default_group_node_width = 140
    

    #two_color_blue_red interface

    #initialize two_color_blue_red nodes
    #node Principled BSDF.001
    principled_bsdf_001 = two_color_blue_red.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf_001.name = "Principled BSDF.001"
    principled_bsdf_001.distribution = 'MULTI_GGX'
    principled_bsdf_001.subsurface_method = 'RANDOM_WALK'
    #Metallic
    principled_bsdf_001.inputs[1].default_value = 0.0
    #Roughness
    principled_bsdf_001.inputs[2].default_value = 0.5
    #IOR
    principled_bsdf_001.inputs[3].default_value = 1.5
    #Alpha
    principled_bsdf_001.inputs[4].default_value = 1.0
    #Normal
    principled_bsdf_001.inputs[5].default_value = (0.0, 0.0, 0.0)

    #Emission Strength
    principled_bsdf_001.inputs[28].default_value = 0.5
    #Thin Film Thickness
    principled_bsdf_001.inputs[29].default_value = 0.0


    #node Material Output.001
    material_output_001 = two_color_blue_red.nodes.new("ShaderNodeOutputMaterial")
    material_output_001.name = "Material Output.001"
    material_output_001.is_active_output = True
    material_output_001.target = 'ALL'
    #Displacement
    material_output_001.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Thickness
    material_output_001.inputs[3].default_value = 0.0

    #node Mapping
    mapping = two_color_blue_red.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    #Location
    mapping.inputs[1].default_value = (0.7999999523162842, 0.0, 0.0)
    #Rotation
    mapping.inputs[2].default_value = (0.0, 1.5707963705062866, 0.0)
    #Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 0.10000000149011612)

    #node Texture Coordinate
    texture_coordinate = two_color_blue_red.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    #node Gradient Texture
    gradient_texture = two_color_blue_red.nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    #node Color Ramp
    color_ramp = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.0
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (0.7460798025131226, 0.017206234857439995, 0.031243890523910522, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.9909090995788574)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (0.014988411217927933, 0.06866735219955444, 1.0, 1.0)


    #node Color Ramp.001
    color_ramp_001 = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp_001.name = "Color Ramp.001"
    color_ramp_001.color_ramp.color_mode = 'RGB'
    color_ramp_001.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_001.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp_001.color_ramp.elements.remove(color_ramp_001.color_ramp.elements[0])
    color_ramp_001_cre_0 = color_ramp_001.color_ramp.elements[0]
    color_ramp_001_cre_0.position = 0.0
    color_ramp_001_cre_0.alpha = 1.0
    color_ramp_001_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    color_ramp_001_cre_1 = color_ramp_001.color_ramp.elements.new(0.49545466899871826)
    color_ramp_001_cre_1.alpha = 1.0
    color_ramp_001_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    color_ramp_001_cre_2 = color_ramp_001.color_ramp.elements.new(1.0)
    color_ramp_001_cre_2.alpha = 1.0
    color_ramp_001_cre_2.color = (0.0, 0.0, 0.0, 1.0)


    #node Mix Shader
    mix_shader = two_color_blue_red.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    #node Transparent BSDF
    transparent_bsdf = two_color_blue_red.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    #Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    #node Color Ramp.002
    color_ramp_002 = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp_002.name = "Color Ramp.002"
    color_ramp_002.color_ramp.color_mode = 'RGB'
    color_ramp_002.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_002.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp_002.color_ramp.elements.remove(color_ramp_002.color_ramp.elements[0])
    color_ramp_002_cre_0 = color_ramp_002.color_ramp.elements[0]
    color_ramp_002_cre_0.position = 0.0
    color_ramp_002_cre_0.alpha = 1.0
    color_ramp_002_cre_0.color = (0.11136271059513092, 0.31832197308540344, 1.0, 1.0)

    color_ramp_002_cre_1 = color_ramp_002.color_ramp.elements.new(1.0)
    color_ramp_002_cre_1.alpha = 1.0
    color_ramp_002_cre_1.color = (0.44737708568573, 0.7460546493530273, 0.513788104057312, 1.0)

    #Fac
    color_ramp_002.inputs[0].default_value = 0.5


    #Set locations
    principled_bsdf_001.location = (-97.71873474121094, 146.1671142578125)
    material_output_001.location = (797.6838989257812, 359.5358581542969)
    mapping.location = (-887.208984375, 295.3012390136719)
    texture_coordinate.location = (-1067.208984375, 295.3012390136719)
    gradient_texture.location = (-695.34033203125, 203.23025512695312)
    color_ramp.location = (-471.5116882324219, 168.1605224609375)
    color_ramp_001.location = (-404.4095764160156, 448.23516845703125)
    mix_shader.location = (373.4551696777344, 434.6831359863281)
    transparent_bsdf.location = (156.40982055664062, 293.4704284667969)
    color_ramp_002.location = (-522.1466064453125, -144.16119384765625)

    #Set dimensions
    principled_bsdf_001.width, principled_bsdf_001.height = 240.0, 100.0
    material_output_001.width, material_output_001.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    color_ramp_001.width, color_ramp_001.height = 240.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    transparent_bsdf.width, transparent_bsdf.height = 140.0, 100.0
    color_ramp_002.width, color_ramp_002.height = 240.0, 100.0

    #initialize two_color_blue_red links
    #texture_coordinate.Object -> mapping.Vector
    two_color_blue_red.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    #mapping.Vector -> gradient_texture.Vector
    two_color_blue_red.links.new(mapping.outputs[0], gradient_texture.inputs[0])
    #color_ramp.Color -> principled_bsdf_001.Base Color
    two_color_blue_red.links.new(color_ramp.outputs[0], principled_bsdf_001.inputs[0])
    #gradient_texture.Color -> color_ramp.Fac
    two_color_blue_red.links.new(gradient_texture.outputs[0], color_ramp.inputs[0])
    #gradient_texture.Color -> color_ramp_001.Fac
    two_color_blue_red.links.new(gradient_texture.outputs[0], color_ramp_001.inputs[0])
    #color_ramp_001.Color -> mix_shader.Fac
    two_color_blue_red.links.new(color_ramp_001.outputs[0], mix_shader.inputs[0])
    #transparent_bsdf.BSDF -> mix_shader.Shader
    two_color_blue_red.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[2])
    #principled_bsdf_001.BSDF -> material_output_001.Surface
    two_color_blue_red.links.new(principled_bsdf_001.outputs[0], material_output_001.inputs[0])
    #color_ramp.Color -> principled_bsdf_001.Emission Color
    two_color_blue_red.links.new(color_ramp.outputs[0], principled_bsdf_001.inputs[27])
    return mat



def dark_and_light_red():
    mat = bpy.data.materials.new(name="two_color_blue_red_node_group")
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    two_color_blue_red = mat.node_tree
    #start with a clean node tree
    for node in two_color_blue_red.nodes:
        two_color_blue_red.nodes.remove(node)
    two_color_blue_red.color_tag = 'NONE'
    two_color_blue_red.description = ""
    #two_color_blue_red.default_group_node_width = 140
    

    #two_color_blue_red interface

    #initialize two_color_blue_red nodes
    #node Principled BSDF.001
    principled_bsdf_001 = two_color_blue_red.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf_001.name = "Principled BSDF.001"
    principled_bsdf_001.distribution = 'MULTI_GGX'
    principled_bsdf_001.subsurface_method = 'RANDOM_WALK'
    #Metallic
    principled_bsdf_001.inputs[1].default_value = 0.0
    #Roughness
    principled_bsdf_001.inputs[2].default_value = 0.5
    #IOR
    principled_bsdf_001.inputs[3].default_value = 1.5
    #Alpha
    principled_bsdf_001.inputs[4].default_value = 1.0
    #Normal
    principled_bsdf_001.inputs[5].default_value = (0.0, 0.0, 0.0)

    #Emission Strength
    principled_bsdf_001.inputs[28].default_value = 0.1
    #Thin Film Thickness
    principled_bsdf_001.inputs[29].default_value = 0.0


    #node Material Output.001
    material_output_001 = two_color_blue_red.nodes.new("ShaderNodeOutputMaterial")
    material_output_001.name = "Material Output.001"
    material_output_001.is_active_output = True
    material_output_001.target = 'ALL'
    #Displacement
    material_output_001.inputs[2].default_value = (0.0, 0.0, 0.0)
    #Thickness
    material_output_001.inputs[3].default_value = 0.0

    #node Mapping
    mapping = two_color_blue_red.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    #Location
    mapping.inputs[1].default_value = (0.7999999523162842, 0.0, 0.0)
    #Rotation
    mapping.inputs[2].default_value = (0.0, 1.5707963705062866, 0.0)
    #Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 0.10000000149011612)

    #node Texture Coordinate
    texture_coordinate = two_color_blue_red.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    #node Gradient Texture
    gradient_texture = two_color_blue_red.nodes.new("ShaderNodeTexGradient")
    gradient_texture.name = "Gradient Texture"
    gradient_texture.gradient_type = 'LINEAR'

    #node Color Ramp
    color_ramp = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.0
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (0.7460798025131226, 0.017206234857439995, 0.031243890523910522, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.9909090995788574)
    color_ramp_cre_1.alpha = 1.0
    #color_ramp_cre_1.color = (0.014988411217927933, 0.06866735219955444, 1.0, 1.0)
    color_ramp_cre_1.color = (0.969, 0.741, 0.749, 1.0)


    #node Color Ramp.001
    color_ramp_001 = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp_001.name = "Color Ramp.001"
    color_ramp_001.color_ramp.color_mode = 'RGB'
    color_ramp_001.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_001.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp_001.color_ramp.elements.remove(color_ramp_001.color_ramp.elements[0])
    color_ramp_001_cre_0 = color_ramp_001.color_ramp.elements[0]
    color_ramp_001_cre_0.position = 0.0
    color_ramp_001_cre_0.alpha = 1.0
    color_ramp_001_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    color_ramp_001_cre_1 = color_ramp_001.color_ramp.elements.new(0.49545466899871826)
    color_ramp_001_cre_1.alpha = 1.0
    color_ramp_001_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    color_ramp_001_cre_2 = color_ramp_001.color_ramp.elements.new(1.0)
    color_ramp_001_cre_2.alpha = 1.0
    color_ramp_001_cre_2.color = (0.0, 0.0, 0.0, 1.0)


    #node Mix Shader
    mix_shader = two_color_blue_red.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    #node Transparent BSDF
    transparent_bsdf = two_color_blue_red.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    #Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    #node Color Ramp.002
    color_ramp_002 = two_color_blue_red.nodes.new("ShaderNodeValToRGB")
    color_ramp_002.name = "Color Ramp.002"
    color_ramp_002.color_ramp.color_mode = 'RGB'
    color_ramp_002.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_002.color_ramp.interpolation = 'LINEAR'

    #initialize color ramp elements
    color_ramp_002.color_ramp.elements.remove(color_ramp_002.color_ramp.elements[0])
    color_ramp_002_cre_0 = color_ramp_002.color_ramp.elements[0]
    color_ramp_002_cre_0.position = 0.0
    color_ramp_002_cre_0.alpha = 1.0
    color_ramp_002_cre_0.color = (0.11136271059513092, 0.31832197308540344, 1.0, 1.0)

    color_ramp_002_cre_1 = color_ramp_002.color_ramp.elements.new(1.0)
    color_ramp_002_cre_1.alpha = 1.0
    color_ramp_002_cre_1.color = (0.44737708568573, 0.7460546493530273, 0.513788104057312, 1.0)

    #Fac
    color_ramp_002.inputs[0].default_value = 0.5


    #Set locations
    principled_bsdf_001.location = (-97.71873474121094, 146.1671142578125)
    material_output_001.location = (797.6838989257812, 359.5358581542969)
    mapping.location = (-887.208984375, 295.3012390136719)
    texture_coordinate.location = (-1067.208984375, 295.3012390136719)
    gradient_texture.location = (-695.34033203125, 203.23025512695312)
    color_ramp.location = (-471.5116882324219, 168.1605224609375)
    color_ramp_001.location = (-404.4095764160156, 448.23516845703125)
    mix_shader.location = (373.4551696777344, 434.6831359863281)
    transparent_bsdf.location = (156.40982055664062, 293.4704284667969)
    color_ramp_002.location = (-522.1466064453125, -144.16119384765625)

    #Set dimensions
    principled_bsdf_001.width, principled_bsdf_001.height = 240.0, 100.0
    material_output_001.width, material_output_001.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    gradient_texture.width, gradient_texture.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    color_ramp_001.width, color_ramp_001.height = 240.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    transparent_bsdf.width, transparent_bsdf.height = 140.0, 100.0
    color_ramp_002.width, color_ramp_002.height = 240.0, 100.0

    #initialize two_color_blue_red links
    #texture_coordinate.Object -> mapping.Vector
    two_color_blue_red.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    #mapping.Vector -> gradient_texture.Vector
    two_color_blue_red.links.new(mapping.outputs[0], gradient_texture.inputs[0])
    #color_ramp.Color -> principled_bsdf_001.Base Color
    two_color_blue_red.links.new(color_ramp.outputs[0], principled_bsdf_001.inputs[0])
    #gradient_texture.Color -> color_ramp.Fac
    two_color_blue_red.links.new(gradient_texture.outputs[0], color_ramp.inputs[0])
    #gradient_texture.Color -> color_ramp_001.Fac
    two_color_blue_red.links.new(gradient_texture.outputs[0], color_ramp_001.inputs[0])
    #color_ramp_001.Color -> mix_shader.Fac
    two_color_blue_red.links.new(color_ramp_001.outputs[0], mix_shader.inputs[0])
    #transparent_bsdf.BSDF -> mix_shader.Shader
    two_color_blue_red.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[2])
    #principled_bsdf_001.BSDF -> material_output_001.Surface
    two_color_blue_red.links.new(principled_bsdf_001.outputs[0], material_output_001.inputs[0])
    #color_ramp.Color -> principled_bsdf_001.Emission Color
    two_color_blue_red.links.new(color_ramp.outputs[0], principled_bsdf_001.inputs[27])
    return mat