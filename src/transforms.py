"""Funções puras para gerar matrizes Model, View e Projection.

Este é outro módulo composto apenas de funções auxiliares
"""
import math

import glm
import numpy as np


def make_model(angle_deg, axis, translation, scale):
    """Compõe a matriz model como T * R * S aplicada à identidade.

    A ordem (escala primeiro, depois rotação, depois translação) garante
    que objetos sejam dimensionados em torno do próprio centro antes de
    serem posicionados no mundo.
    """
    angle = math.radians(angle_deg)
    m = glm.mat4(1.0)
    m = glm.translate(m, glm.vec3(*translation))
    if angle != 0:
        m = glm.rotate(m, angle, glm.vec3(*axis))
    m = glm.scale(m, glm.vec3(*scale))
    return np.array(m)


def make_view(camera_pos, camera_front, camera_up):
    return np.array(glm.lookAt(camera_pos, camera_pos + camera_front, camera_up))


def make_projection(fov_deg, aspect, near=0.1, far=1000.0):
    return np.array(glm.perspective(glm.radians(fov_deg), aspect, near, far))
