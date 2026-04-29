"""Câmera em primeira pessoa com clamping dentro de um AABB (req. 9)."""
import glm


class Camera:
    """Câmera estilo FPS — WASD + mouse.

    Os limites (bounds_min/bounds_max) são definidos a partir do tamanho do
    skybox para impedir que o jogador "saia" do mundo (req. 9).
    """

    def __init__(self, position, front=(0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0)):
        self.position = glm.vec3(*position)
        self.front = glm.vec3(*front)
        self.up = glm.vec3(*up)

        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 45.0

        self.speed = 50.0
        self.sensitivity = 0.1

        self.bounds_min = None
        self.bounds_max = None

        # Estado para calcular deltas de mouse — o primeiro evento define o "zero"
        self._first_mouse = True
        self._last_x = 0.0
        self._last_y = 0.0

    def set_bounds(self, vmin, vmax):
        self.bounds_min = glm.vec3(*vmin)
        self.bounds_max = glm.vec3(*vmax)

    def _clamp(self):
        if self.bounds_min is None or self.bounds_max is None:
            return
        self.position.x = max(self.bounds_min.x, min(self.bounds_max.x, self.position.x))
        self.position.y = max(self.bounds_min.y, min(self.bounds_max.y, self.position.y))
        self.position.z = max(self.bounds_min.z, min(self.bounds_max.z, self.position.z))

    def move_forward(self, dt):
        self.position += self.speed * dt * self.front
        self._clamp()

    def move_backward(self, dt):
        self.position -= self.speed * dt * self.front
        self._clamp()

    def move_left(self, dt):
        self.position -= glm.normalize(glm.cross(self.front, self.up)) * self.speed * dt
        self._clamp()

    def move_right(self, dt):
        self.position += glm.normalize(glm.cross(self.front, self.up)) * self.speed * dt
        self._clamp()

    def process_mouse(self, xpos, ypos):
        if self._first_mouse:
            self._last_x = xpos
            self._last_y = ypos
            self._first_mouse = False
        xoffset = xpos - self._last_x
        yoffset = self._last_y - ypos  # Y invertido: tela cresce p/ baixo
        self._last_x = xpos
        self._last_y = ypos

        self.yaw += xoffset * self.sensitivity
        self.pitch += yoffset * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
