"""MeshRegistry: dono dos VBOs e do contador de texturas.

Todos os modelos compartilham UM único par de VBOs (positions + uvs).
Cada modelo é identificado por um (offset, count) no buffer global —
mesmo esquema usado na base do professor.
"""
import ctypes
from dataclasses import dataclass, field
from typing import List

import numpy as np
from OpenGL.GL import *
from PIL import Image

from src.obj_parser import parse_obj, triangulate_face


@dataclass
class MeshHandle:
    """Identifica uma malha dentro do VBO global e suas texturas disponíveis."""
    vertex_offset: int
    vertex_count: int
    texture_ids: List[int] = field(default_factory=list)


class MeshRegistry:
    """Acumula vértices/UVs e gerencia texturas. Singleton de fato (1 instância no main)."""

    def __init__(self):
        self._vertices = []
        self._tex_coords = []
        self._num_textures = 0

    def register(self, obj_path, texture_paths):
        """Registra um modelo. Retorna um MeshHandle que o ObjetoGrafico vai guardar."""
        model = parse_obj(obj_path)
        print('Processando modelo {}. Vertice inicial: {}'.format(obj_path, len(self._vertices)))

        offset = len(self._vertices)
        for face in model["faces"]:
            for vid in triangulate_face(face[0]):
                self._vertices.append(model["vertices"][vid - 1])
            for tid in triangulate_face(face[1]):
                self._tex_coords.append(model["texture"][tid - 1])
        count = len(self._vertices) - offset

        print('Processando modelo {}. Vertice final: {}'.format(obj_path, len(self._vertices)))

        texture_ids = [self._load_texture(p) for p in texture_paths]
        return MeshHandle(vertex_offset=offset, vertex_count=count, texture_ids=texture_ids)

    # Texturas maiores que isso são reduzidas antes de subirem para a GPU. Algumas
    # imagens (ex.: a do mario64, 4962×3675) estouram a alocação do driver OpenGL,
    # mesmo em GPUs modernas. 2048px atende com folga ao detalhe que precisamos.
    MAX_TEXTURE_DIM = 2048

    def _load_texture(self, path):
        """Carrega imagem para a GPU — mesmo fluxo de load_texture_from_file da Aula 13."""
        tid = self._num_textures
        print(tid)
        glBindTexture(GL_TEXTURE_2D, tid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        img = Image.open(path).convert("RGB")
        if max(img.size) > self.MAX_TEXTURE_DIM:
            ratio = self.MAX_TEXTURE_DIM / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # stride y negativo inverte a imagem verticalmente (texturas em obj costumam vir invertidas)
        image_data = img.tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

        self._num_textures += 1
        return tid

    def upload_to_gpu(self, shader_program):
        """Sobe vértices e UVs para a GPU. Chamar UMA vez, depois de registrar tudo."""
        if not self._vertices:
            return  # nada registrado ainda — ok para esqueleto inicial

        buffers = glGenBuffers(2)

        verts = np.zeros(len(self._vertices), [("position", np.float32, 3)])
        verts["position"] = self._vertices
        glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        loc = glGetAttribLocation(shader_program, "position")
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, 3, GL_FLOAT, False, verts.strides[0], ctypes.c_void_p(0))

        uvs = np.zeros(len(self._tex_coords), [("position", np.float32, 2)])
        uvs["position"] = self._tex_coords
        glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
        glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)
        loc = glGetAttribLocation(shader_program, "texture_coord")
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, 2, GL_FLOAT, False, uvs.strides[0], ctypes.c_void_p(0))
