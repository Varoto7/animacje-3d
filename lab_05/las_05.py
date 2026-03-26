import bpy
import math
import random
import os

TYPY_ROSLIN = {
    "drzewo": {
        "wysokosc": (3.0, 5.0),
        "liczba_lisci": (4, 6),
        "promien_lisci": (0.4, 0.7),
        "liczba_korzeni": (4, 6),
        "kolor_lodygi": (0.15, 0.08, 0.02, 1), 
        "kolor_lisci": (0.05, 0.35, 0.1, 1), 
    },
    "krzew": {
        "wysokosc": (0.8, 1.8),
        "liczba_lisci": (5, 8),
        "promien_lisci": (0.5, 0.9),
        "liczba_korzeni": (2, 4),
        "kolor_lodygi": (0.25, 0.15, 0.05, 1),
        "kolor_lisci": (0.1, 0.5, 0.05, 1), 
    },
    "paproc": {
        "wysokosc": (0.5, 1.2),
        "liczba_lisci": (6, 10),
        "promien_lisci": (0.6, 1.0),
        "liczba_korzeni": (2, 3),
        "kolor_lodygi": (0.2, 0.3, 0.1, 1), 
        "kolor_lisci": (0.0, 0.6, 0.15, 1), 
    },
}

NAZWY_MNOGIE = {
    "drzewo": "Drzewa",
    "krzew": "Krzewy",
    "paproc": "Paprocie"
}

def stworz_material(nazwa, kolor):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = kolor
    return mat

def stworz_rosline(wysokosc, liczba_lisci, promien_lisci, liczba_korzeni, pozycja, mat_lodyga, mat_lisc):
    obiekty = []
    px, pz, py = pozycja 
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=wysokosc, location=(px, py, pz + wysokosc / 2))
    lodyga = bpy.context.active_object
    lodyga.data.materials.append(mat_lodyga)
    obiekty.append(lodyga)
    
    for i in range(liczba_lisci):
        kat = (2 * math.pi / liczba_lisci) * i
        lx, ly, lz = px + math.cos(kat) * 0.2, py + math.sin(kat) * 0.2, pz + wysokosc * 0.9
        bpy.ops.mesh.primitive_cube_add(size=promien_lisci, location=(lx, ly, lz))
        lisc = bpy.context.active_object
        lisc.rotation_euler = (math.radians(45), 0, kat)
        lisc.data.materials.append(mat_lisc)
        obiekty.append(lisc)
        
    for i in range(liczba_korzeni):
        kat = (2 * math.pi / liczba_korzeni) * i
        kx, ky, kz = px + math.cos(kat) * 0.15, py + math.sin(kat) * 0.15, pz + 0.1
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(kx, ky, kz))
        korzen = bpy.context.active_object
        korzen.data.materials.append(mat_lodyga)
        obiekty.append(korzen)
        
    return obiekty

def stworz_rosline_typ(x, z, typ):
    p = TYPY_ROSLIN[typ]
    h = random.uniform(*p["wysokosc"])
    n_l = random.randint(*p["liczba_lisci"])
    r_l = random.uniform(*p["promien_lisci"])
    n_k = random.randint(*p["liczba_korzeni"])
    
    m_lodyga = stworz_material(f"Mat_Lodyga_{typ}", p["kolor_lodygi"])
    m_lisc = stworz_material(f"Mat_Lisc_{typ}", p["kolor_lisci"])
    
    return stworz_rosline(h, n_l, r_l, n_k, (x, 0, z), m_lodyga, m_lisc)

def wybierz_typ_biomu(x, z, rozmiar_pola):
    prog_centrum = 0.3 * (rozmiar_pola / 2)
    prog_peryferia = 0.7 * (rozmiar_pola / 2)
    
    if abs(x) < prog_centrum and abs(z) < prog_centrum:
        return "drzewo"
    elif abs(x) < prog_peryferia and abs(z) < prog_peryferia:
        return "krzew" if random.random() < 0.7 else "drzewo"
    else:
        return "paproc" if random.random() < 0.7 else "krzew"

def generuj_las(liczba_roslin=30, rozmiar_pola=15.0, seed=42):
    random.seed(seed)
    
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

    kolekcja_glowna = bpy.data.collections.new("Las")
    bpy.context.scene.collection.children.link(kolekcja_glowna)
    
    podkolekcje = {t: bpy.data.collections.new(f"Las/{NAZWY_MNOGIE[t]}") for t in TYPY_ROSLIN}
    for pk in podkolekcje.values():
        kolekcja_glowna.children.link(pk)

    for _ in range(liczba_roslin):
        rx = random.uniform(-rozmiar_pola/2, rozmiar_pola/2)
        rz = random.uniform(-rozmiar_pola/2, rozmiar_pola/2)
        typ = wybierz_typ_biomu(rx, rz, rozmiar_pola)
        
        for obj in stworz_rosline_typ(rx, rz, typ):
            for col in list(obj.users_collection):
                col.objects.unlink(obj)
            podkolekcje[typ].objects.link(obj)

    bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
    bpy.context.active_object.data.energy = 4.0
    
    bpy.ops.object.camera_add(location=(15, -15, 12))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(60), 0, math.radians(45))
    cam.data.lens = 30
    bpy.context.scene.camera = cam

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.filepath = os.path.abspath("las_05.png")
    scene.render.resolution_x, scene.render.resolution_y = 1200, 800
    bpy.ops.render.render(write_still=True)

generuj_las(liczba_roslin=40, rozmiar_pola=20, seed=123)