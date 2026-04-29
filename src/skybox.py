"""Skybox: caixa grande estática usando o mesmo shader dos demais objetos.

É essencialmente um ObjetoGrafico estático com escala enorme. A classe
existe para sinalizar intenção e expor `bounds`, que é o tamanho
usado pela Camera para clamping (req. 9).
"""
from src.graphic_object import ObjetoGrafico


class Skybox(ObjetoGrafico):
    def __init__(self, mesh_handle, scale=50.0, position=(0.0, 0.0, 0.0), texture_index=0):
        # `position` é necessária quando o .obj não está centrado em (0,0,0).
        # Ex.: o skybox.obj atual é um cubo no octante negativo — sem deslocamento,
        # ele fica num canto e a câmera nunca chega a ficar envolvida por ele.
        super().__init__(
            mesh_handle=mesh_handle,
            position=position,
            scale=(scale, scale, scale),
            texture_index=texture_index,
            static=True,
        )
        self.bounds = scale
