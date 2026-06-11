"""Scene: agrupa câmera, skybox e a lista de objetos. Quem chama draw é ela."""

from OpenGL.GL import *
from src.light import Light
from src.transforms import make_view, make_projection
from src.scene_editor import SceneEditor
from src.input_manager import InputManager

_CHANGE_GLOBAL_DIFFUSE = 0.1
_CHANGE_GLOBAL_SPECULAR = 0.1
_CHANGE_GLOBAL_AMBIENT =0.1

class Scene:
    def __init__(self, camera, mode="viz", skybox=None):
        self.camera = camera
        self.skybox = skybox
        self.objects = []
        self.light_objects = []
        self.lights = []


        # Atributos para a gerência do estado da cena
        self.is_at_polygonal_mode = False
        self._mode = mode

        # Handlers para inputs e alteração permantente da cena
        self.scene_editor = SceneEditor()
        self.input_mngr = InputManager(self._mode)

        # Incremento e decremento dos fatores de reflexão pelo teclado
        self.diffuse_factor = 1.0
        self.specular_factor = 1.0

        # Atributos para calculos com framerate
        self.delta_time = 0.0
        self.last_frame = 0.0

    def get_mode(self):
        return self._mode

    def set_mode(self, new_mode):
        """Configura o estado interno de qual modo de uso a cena está e propaga para o InputManager"""

        self._mode = new_mode
        self.input_mngr.curr_mode = new_mode


    def add_object(self, obj, is_light_src=False):
        if not is_light_src:
            self.objects.append(obj)
        else:
            self.light_objects.append(obj)


    def add_light(self, light):
        self.lights.append(light)


    def decrease_diffuse_factor(self):
        self.diffuse_factor -= _CHANGE_GLOBAL_DIFFUSE

    def increase_diffuse_factor(self):
        self.diffuse_factor += _CHANGE_GLOBAL_DIFFUSE

    def decrease_specular_factor(self):
        self.specular_factor -= _CHANGE_GLOBAL_SPECULAR

    def increase_specular_factor(self):
        self.specular_factor += _CHANGE_GLOBAL_SPECULAR

    def decrease_ambient_light(self):
        self.diffuse_factor -= _CHANGE_GLOBAL_AMBIENT

    def increase_ambient_light(self):
        self.diffuse_factor += _CHANGE_GLOBAL_AMBIENT

    def draw(self, light_src_shader, lightable_shader, aspect_ratio, registry):
        """
        Gerencia o fluxo de renderização da cena
        """

        # Obtendo os programas
        light_src_program = light_src_shader.get_program()
        lightable_program = lightable_shader.get_program()

        # Gerar matrizes de View e Projection globais da cena
        view_mat = make_view(self.camera.position, self.camera.front, self.camera.up)
        proj_mat = make_projection(self.camera.fov, aspect_ratio)

        # Reativação da lógica de detecção de ambiente para alimentar a classe Light
        # (Ajuste os valores -15.0 e 15.0 se a sua castleroom for maior/menor)
        is_camera_inside = (-15.0 < self.camera.position[0] < 15.0) and (-15.0 < self.camera.position[2] < 15.0)

        # Renderizando os objetos que emitem luz
        light_src_shader.use()
        registry.bind_buffers_to_shader(light_src_program)
        glUniformMatrix4fv(glGetUniformLocation(light_src_program, "view"), 1, GL_TRUE, view_mat)
        glUniformMatrix4fv(glGetUniformLocation(light_src_program, "projection"), 1, GL_TRUE, proj_mat)


        # Objetos fontes de luz que brilham puramente
        for obj in self.light_objects:
            obj.draw(light_src_program)

        # Renderizando objetos afetados pela luz
        lightable_shader.use()
        registry.bind_buffers_to_shader(lightable_program)
        glUniformMatrix4fv(glGetUniformLocation(lightable_program, "view"), 1, GL_TRUE, view_mat)
        glUniformMatrix4fv(glGetUniformLocation(lightable_program, "projection"), 1, GL_TRUE, proj_mat)

        # Envia a posição da câmera (necessária para o cálculo da reflexão especular)
        glUniform3f(
            glGetUniformLocation(lightable_program, "view_pos"),
            self.camera.position[0],
            self.camera.position[1],
            self.camera.position[2]
        )

        # Envia os fatores de incremento/decremento controlados via teclado
        glUniform1f(glGetUniformLocation(lightable_program, "global_diffuse_factor"), self.diffuse_factor)
        glUniform1f(glGetUniformLocation(lightable_program, "global_specular_factor"), self.specular_factor)

        # Injeta as luzes no shader
        for i, light in enumerate(self.lights):
            light.send_to_shader(lightable_program, i, is_camera_inside)

        # Desenha todos os objetos opacos normais da cena usando o shader com Phong
        for obj in self.objects:
            obj.draw(lightable_program)

        if self.skybox is not None:
            self.skybox.draw(lightable_program)
