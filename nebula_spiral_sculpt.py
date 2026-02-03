import bpy
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection
collection = bpy.data.collections.new("NebulaSpiral")
bpy.context.scene.collection.children.link(collection)

# Parameters
spiral_turns = 6
points_per_turn = 80
radius_growth = 0.08
height_growth = 0.05
wave_amplitude = 0.15
wave_frequency = 3.0

# Create a curve for the spiral
curve_data = bpy.data.curves.new("SpiralCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12

polyline = curve_data.splines.new('POLY')
polyline.points.add(spiral_turns * points_per_turn - 1)

for i in range(spiral_turns * points_per_turn):
    t = i / points_per_turn
    angle = t * 2.0 * math.pi
    radius = 0.3 + t * radius_growth
    height = t * height_growth
    wave = math.sin(t * wave_frequency) * wave_amplitude

    x = math.cos(angle) * (radius + wave)
    y = math.sin(angle) * (radius + wave)
    z = height + math.cos(t * wave_frequency) * wave_amplitude * 0.5
    polyline.points[i].co = (x, y, z, 1)

curve_obj = bpy.data.objects.new("SpiralCurve", curve_data)
collection.objects.link(curve_obj)

# Add a bevel for thickness
curve_data.bevel_depth = 0.02
curve_data.bevel_resolution = 6

# Create glowing spheres along the spiral
for i in range(0, spiral_turns * points_per_turn, 25):
    point = polyline.points[i].co
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(point.x, point.y, point.z))
    sphere = bpy.context.active_object
    sphere.name = f"NebulaSphere_{i}"
    collection.objects.link(sphere)
    bpy.context.scene.collection.objects.unlink(sphere)

    mat = bpy.data.materials.new(name=f"Glow_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 6.0
    emission.inputs['Color'].default_value = (0.7, 0.2 + (i % 100) / 100.0, 1.0, 1)
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

    sphere.data.materials.append(mat)

# Add a central crystal (icosphere with subdivision)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.35, location=(0, 0, 0.1))
crystal = bpy.context.active_object
crystal.name = "NebulaCrystal"
collection.objects.link(crystal)
bpy.context.scene.collection.objects.unlink(crystal)

crystal_mat = bpy.data.materials.new(name="CrystalMaterial")
crystal_mat.use_nodes = True
nodes = crystal_mat.node_tree.nodes
nodes.clear()

output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Transmission'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.05
bsdf.inputs['IOR'].default_value = 1.45
bsdf.inputs['Base Color'].default_value = (0.3, 0.6, 1.0, 1)

crystal_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
crystal.data.materials.append(crystal_mat)

# Set camera
bpy.ops.object.camera_add(location=(3.5, -3.5, 2.5), rotation=(math.radians(60), 0, math.radians(45)))

# Add a light
bpy.ops.object.light_add(type='AREA', location=(4, -2, 4))
light = bpy.context.active_object
light.data.energy = 800

# Set render settings for a vibrant look
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.world.color = (0.02, 0.02, 0.05)
