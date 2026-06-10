"""Parser de arquivos Wavefront (.obj). Função pura que leva um arquivo para um dicionário Python.

É um módulo auxiliar do MeshRegistry.
"""


def parse_obj(filepath):
    """Lê um .obj e devolve {'vertices', 'texture', 'normais', 'faces'}.

    (indices_de_vertice, indices_de_textura, material).
    """
    vertices = []
    texture_coords = []
    normais = []
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
                vertices.append([float(x) for x in values[1:4]])
            elif values[0] == "vt":
                texture_coords.append([float(x) for x in values[1:3]])
            elif values[0] == "vn":
                normais.append([float(x) for x in values[1:4]])
            elif values[0] in ("usemtl", "usemat"):
                material = values[1]
            elif values[0] == "f":
                face = []
                face_texture = []
                face_normal = []
                for v in values[1:]:
                    w = v.split("/")
                    face.append(int(w[0]))

                    # Adcionando o índice da coordenada de textura
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)

                    # Adcionando o índice da normal
                    if len(w) >=3 and len(w[2]) > 0:
                        face_normal.append(int(w[2]))
                    else:
                        face_normal.append(0)
                faces.append((face, face_texture, face_normal, material))

    return {"vertices": vertices, "texture": texture_coords, "normais": normais, "faces": faces}


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
