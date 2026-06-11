"""ObjetoGrafico: representa cada modelo desenhável da cena.

`static=True` desliga as transformações vindas do teclado — Utilizada em elementos decorativos
do cenário.
"""
from OpenGL.GL import *

from src.transforms import make_model


class ObjetoGrafico:
    def __init__(self, mesh_handle, position=(0.0, 0.0, 0.0),
                 rotation_axis=(0.0, 1.0, 0.0), rotation_angle=0.0,
                 scale=(1.0, 1.0, 1.0), texture_index=0, static=False,
                 k_diffuse = 0.1, k_specular=0.1, shininess = 10.0):
        self.mesh = mesh_handle
        self.position = list(position)
        self.rotation_axis = list(rotation_axis)
        self.rotation_angle = rotation_angle
        self.scale = list(scale)
        self.texture_index = texture_index
        self.static = static

        # Atributos de iluminação
        self.k_diffuse = k_diffuse
        self.k_specular = k_specular
        self.shininess = shininess

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
        """
        Gera a matriz com o estado do objeto, aplicando sua textura e a matriz model associada ao
        seu estado de transforamções geométricas
        """

        # Configurando a matriz model para posicionais o objeto
        mat = make_model(self.rotation_angle, self.rotation_axis, self.position, self.scale)
        loc_model = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat)

        # Configurando os parametros globais de iluminação do objeto
        glUniform1f(glGetUniformLocation(shader_program, "material.k_diffuse"), self.k_diffuse)
        glUniform1f(glGetUniformLocation(shader_program, "material.k_specular"), self.k_specular)
        glUniform1f(glGetUniformLocation(shader_program, "material.shininess"), self.shininess)


        glBindTexture(GL_TEXTURE_2D, self.mesh.texture_ids[self.texture_index])
        glDrawArrays(GL_TRIANGLES, self.mesh.vertex_offset, self.mesh.vertex_count)
