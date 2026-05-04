"""Skybox: caixa grande estática usando o mesmo shader dos demais objetos.

É uma subclasse do ObjetoGrafico estático com escala enorme. Essa classe
existe para facilitar a legibilidade e diferenciação ao sinalizar intenção e expor "bounds".
"""
from src.graphic_object import ObjetoGrafico


class Skybox(ObjetoGrafico):
    def __init__(self, mesh_handle, scale=50.0, position=(0.0, 0.0, 0.0), texture_index=0):

        super().__init__(
            mesh_handle=mesh_handle,
            position=position,
            scale=(scale, scale, scale),
            texture_index=texture_index,
            static=True,
        )
        self.bounds = scale
