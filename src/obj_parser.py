"""Parser de arquivos Wavefront (.obj). Função pura: arquivo -> dicionário.

Quem decide o que fazer com os vértices depois (acumular num VBO global,
mandar para GPU etc.) é o MeshRegistry.
"""


def parse_obj(filepath):
    """Lê um .obj e devolve {'vertices', 'texture', 'faces'}.

    Ignora normais (vn) e linhas de comentário. Cada face vira uma tupla
    (indices_de_vertice, indices_de_textura, material).
    """
    vertices = []
    texture_coords = []
    faces = []
    material = None

    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == "v":
                vertices.append(values[1:4])
            elif values[0] == "vt":
                texture_coords.append(values[1:3])
            elif values[0] in ("usemtl", "usemat"):
                material = values[1]
            elif values[0] == "f":
                face = []
                face_texture = []
                for v in values[1:]:
                    w = v.split("/")
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)
                faces.append((face, face_texture, material))

    return {"vertices": vertices, "texture": texture_coords, "faces": faces}


def triangulate_face(indices):
    """Transforma uma face poligonal numa lista de índices em formato fan-triangulation.

    Necessário porque alguns .obj trazem quads ou n-gons. Para faces que já
    são triângulos, devolve tal qual.
    """
    if len(indices) == 3:
        return indices
    circular = list(indices) + [indices[0]]
    result = []
    for i in range(len(circular) - 2):
        result.extend(circular[i:i + 3])
    return result
