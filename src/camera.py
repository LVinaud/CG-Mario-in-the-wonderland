"""Câmera em primeira pessoa com movimento e rotação livre pela cena.

Nela também se aplica a lógica de colisão com o skybox, gerando uma "parede invisível" na cena.
"""
import glm


class Camera:
    def __init__(self, position, front=(0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0)):
        # Vetores para a geração da matriz projection
        self.position = glm.vec3(*position)
        self.front = glm.vec3(*front)
        self.up = glm.vec3(*up)

        # Atributos para o movimento de câmera
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 45.0
        self.sensitivity = 0.1

        # Atributos para o movimento
        self.speed = 25.0
        self.is_moving_forward = False
        self.is_moving_backward = False
        self.is_moving_left = False
        self.is_moving_right = False

        self.bounds_min = None
        self.bounds_max = None

        self._first_mouse = True
        self._last_x = 0.0
        self._last_y = 0.0

    def set_bounds(self, vmin, vmax):
        self.bounds_min = glm.vec3(*vmin)
        self.bounds_max = glm.vec3(*vmax)

    def _clamp(self):
        """
        Auxiliar que impede a câmera de passar dos limites estabelecidos em bounds_min e boundds_max
        """

        if self.bounds_min is None or self.bounds_max is None:
            return
        self.position.x = max(self.bounds_min.x, min(self.bounds_max.x, self.position.x))
        self.position.y = max(self.bounds_min.y, min(self.bounds_max.y, self.position.y))
        self.position.z = max(self.bounds_min.z, min(self.bounds_max.z, self.position.z))


    def update(self, dt):
        """Calcula melhores movimentos de câmera"""

        # Atualizando de acordo com o estado de cada movimento no frame
        if self.is_moving_forward:
            self.position += self.speed * dt * self.front
        if self.is_moving_backward:
            self.position -= self.speed * dt * self.front
        if self.is_moving_left:
            self.position -= glm.normalize(glm.cross(self.front, self.up)) * self.speed * dt
        if self.is_moving_right:
            self.position += glm.normalize(glm.cross(self.front, self.up)) * self.speed * dt

        # Garantindo que ela não saiu das bordas
        self._clamp()


    def process_mouse(self, xpos, ypos):
        """Processamento da lógica de callbacks de inputs dentro da câmera"""
        if self._first_mouse:
            self._last_x = xpos
            self._last_y = ypos
            self._first_mouse = False

        xoffset = xpos - self._last_x
        yoffset = self._last_y - ypos
        self._last_x = xpos
        self._last_y = ypos

        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
