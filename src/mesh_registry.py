"""MeshRegistry: Gera e gerencia os VBOs e do contador de texturas.

Todos os modelos compartilham UM único par de VBOs (positions + uvs).
Cada modelo é identificado por um (offset, count) no buffer global
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
    """Acumula vértices/UVs e gerencia texturas."""

    # Constante para crop de texturas estremamente grandes
    # (observação: No fim do projeto, elas foram trocadas para versões menores)
    MAX_TEXTURE_DIM = 2048

    def __init__(self):
        self._vertices = []
        self._tex_coords = []
        self._normals = []
        self._num_textures = 0
        self.buffers = []

        self.stride_vertices = 0
        self.stride_normals = 0
        self.stride_uvs = 0

    def register(self, obj_path, texture_paths):
        """Registra um modelo. Retorna um MeshHandle que o ObjetoGrafico vai guardar."""
        model = parse_obj(obj_path)
        has_normals = len(model["normais"]) > 0

        # Salva objetos de acordo com a triangulação
        offset = len(self._vertices)
        for face in model["faces"]:
            v_indices = triangulate_face(face[0])
            t_indices = triangulate_face(face[1])
            n_indices = triangulate_face(face[2])

            # Registra vértice por vértice de forma estritamente sincronizada
            for i in range(len(v_indices)):
                # Posição do Vértice
                vid = v_indices[i]
                self._vertices.append(model["vertices"][vid - 1])

                # Coordenada de Textura
                tid = t_indices[i]
                self._tex_coords.append(model["texture"][tid - 1])

                # Vetor Normal (quando especificado pelo modelo)
                if has_normals and i < len(n_indices) and n_indices[i] > 0:
                    nid = n_indices[i]
                    self._normals.append(model["normais"][nid - 1])
                else:
                    self._normals.append([0.0, 1.0, 0.0])

        # Calculando e retornando o MeshHandle final
        count = len(self._vertices) - offset
        texture_ids = [self._load_texture(p) for p in texture_paths]
        return MeshHandle(vertex_offset=offset, vertex_count=count, texture_ids=texture_ids)

    def _load_texture(self, path):
        """Carrega imagem para a GPU."""
        tid = self._num_textures

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


    def upload_to_gpu(self):
            """Envia os dados para a GPU e armazena os IDs dos VBO."""
            if not self._vertices:
                return

            # criando os ids dos buffers na instância
            self.buffers = glGenBuffers(3)

            # BUFFER DE VÉRTICES
            verts = np.zeros(len(self._vertices), [("position", np.float32, 3)])
            verts["position"] = self._vertices
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[0])
            glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
            self.stride_vertices = verts.strides[0]

            # UFFER DE TEXTURAS (UVs)
            uvs = np.zeros(len(self._tex_coords), [("position", np.float32, 2)])
            uvs["position"] = self._tex_coords
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[1])
            glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)
            self.stride_uvs = uvs.strides[0]

            # BUFFER DE NORMAIS
            norms = np.zeros(len(self._normals), [("position", np.float32, 3)])
            norms["position"] = self._normals
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[2])
            glBufferData(GL_ARRAY_BUFFER, norms.nbytes, norms, GL_STATIC_DRAW)
            self.stride_normals = norms.strides[0]

            # Limpa o bind global para segurança
            glBindBuffer(GL_ARRAY_BUFFER, 0)


    def bind_buffers_to_shader(self, shader_program):
        """Função que reconfigura os binds dos buffers para quando o shader é trocado"""

        # Ativa e aponta as Posições
        loc_pos = glGetAttribLocation(shader_program, "position")
        if loc_pos != -1:
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[0])
            glEnableVertexAttribArray(loc_pos)
            glVertexAttribPointer(loc_pos, 3, GL_FLOAT, False, self.stride_vertices, ctypes.c_void_p(0))

        # Ativa e aponta as Texturas
        loc_uv = glGetAttribLocation(shader_program, "texture_coord")
        if loc_uv != -1:
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[1])
            glEnableVertexAttribArray(loc_uv)
            glVertexAttribPointer(loc_uv, 2, GL_FLOAT, False, self.stride_uvs, ctypes.c_void_p(0))

        # Ativa e aponta as Normais
        loc_norm = glGetAttribLocation(shader_program, "normal")
        if loc_norm != -1:
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[2])
            glEnableVertexAttribArray(loc_norm)
            glVertexAttribPointer(loc_norm, 3, GL_FLOAT, False, self.stride_normals, ctypes.c_void_p(0))
