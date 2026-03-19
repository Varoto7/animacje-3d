import bpy
import math
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

mat_lodyga = bpy.data.materials.new(name="Mat_Lodyga")
mat_lodyga.use_nodes = True
bsdf_lodyga = mat_lodyga.node_tree.nodes["Principled BSDF"]
bsdf_lodyga.inputs["Base Color"].default_value = (0.2, 0.05, 0.0, 1.0)
bsdf_lodyga.inputs["Metallic"].default_value = 0.8
bsdf_lodyga.inputs["Roughness"].default_value = 0.3

mat_lisc = bpy.data.materials.new(name="Mat_Lisc")
mat_lisc.use_nodes = True
bsdf_lisc = mat_lisc.node_tree.nodes["Principled BSDF"]
bsdf_lisc.inputs["Base Color"].default_value = (0.0, 0.8, 0.6, 1.0)
if "Emission Color" in bsdf_lisc.inputs:
    bsdf_lisc.inputs["Emission Color"].default_value = (0.0, 0.8, 0.6, 1.0)
    bsdf_lisc.inputs["Emission Strength"].default_value = 2.0

def stworz_rosline(wysokosc=2.0, liczba_lisci=3, promien_lisci=0.3, liczba_korzeni=4, x_offset=0.0):
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.1, 
        depth=wysokosc, 
        location=(x_offset, 0, wysokosc / 2)
    )
    lodyga = bpy.context.active_object
    lodyga.name = "Lodyga"
    lodyga.data.materials.append(mat_lodyga)
    
    for i in range(liczba_lisci):
        kat = (2 * math.pi / liczba_lisci) * i
        
        x = x_offset + math.cos(kat) * 0.15
        y = math.sin(kat) * 0.15
        z = wysokosc * 0.9
        
        bpy.ops.mesh.primitive_cube_add(size=promien_lisci, location=(x, y, z))
        lisc = bpy.context.active_object
        lisc.name = "Lisc"
        lisc.rotation_euler = (math.radians(45), 0, kat)
        lisc.data.materials.append(mat_lisc)
        
    for i in range(liczba_korzeni):
        kat = (2 * math.pi / liczba_korzeni) * i
        
        x = x_offset + math.cos(kat) * 0.12
        y = math.sin(kat) * 0.12
        z = 0.1
        
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(x, y, z))
        korzen = bpy.context.active_object
        korzen.name = "Korzen"
        korzen.data.materials.append(mat_lodyga)

stworz_rosline(wysokosc=1.5, liczba_lisci=3, promien_lisci=0.2, liczba_korzeni=4, x_offset=-2.5)
stworz_rosline(wysokosc=3.0, liczba_lisci=3, promien_lisci=0.4, liczba_korzeni=5, x_offset=0.0)
stworz_rosline(wysokosc=4.5, liczba_lisci=3, promien_lisci=0.3, liczba_korzeni=5, x_offset=2.5)

bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
slonce = bpy.context.active_object
slonce.data.energy = 3.0
slonce.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.camera_add(location=(0, -9, 3.5))
kamera = bpy.context.active_object
kamera.rotation_euler = (math.radians(80), 0, 0)
kamera.data.lens = 30
bpy.context.scene.camera = kamera

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.filepath = os.path.abspath("laboratorium_04_render.png")
scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_x = 800
scene.render.resolution_y = 600

bpy.ops.render.render(write_still=True)
print("Gotowe. Render zapisany jako: laboratorium_04_render.png")