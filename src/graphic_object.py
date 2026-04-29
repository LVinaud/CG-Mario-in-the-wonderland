"""ObjetoGrafico: representa cada modelo desenhável da cena.

`static=True` desliga as transformações vindas do teclado — útil para móveis,
paredes, quadro, velas, etc. (e também é o que a Skybox usa por baixo).
"""
from OpenGL.GL import *

from src.transforms import make_model


class ObjetoGrafico:
    def __init__(self, mesh_handle, position=(0.0, 0.0, 0.0),
                 rotation_axis=(0.0, 1.0, 0.0), rotation_angle=0.0,
                 scale=(1.0, 1.0, 1.0), texture_index=0, static=False):
        self.mesh = mesh_handle
        self.position = list(position)
        self.rotation_axis = list(rotation_axis)
        self.rotation_angle = rotation_angle
        self.scale = list(scale)
        self.texture_index = texture_index
        self.static = static

    def translate(self, dx, dy, dz):
        if self.static:
            return
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz

    def rotate(self, delta_deg):
        if self.static:
            return
        self.rotation_angle = (self.rotation_angle + delta_deg) % 360.0

    def scale_by(self, factor):
        if self.static:
            return
        self.scale = [s * factor for s in self.scale]

    def set_texture(self, index):
        self.texture_index = index

    def draw(self, shader_program):
        mat = make_model(self.rotation_angle, self.rotation_axis, self.position, self.scale)
        loc_model = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat)

        glBindTexture(GL_TEXTURE_2D, self.mesh.texture_ids[self.texture_index])
        glDrawArrays(GL_TRIANGLES, self.mesh.vertex_offset, self.mesh.vertex_count)
