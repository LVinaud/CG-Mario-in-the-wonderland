from OpenGL.GL import *

class Light:
    def __init__(self, position=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0), is_internal=True):
        self.position = list(position)
        self.color = list(color)
        self.is_internal = is_internal  # Define se a luz pertence ao ambiente interno ou externo
        self.is_on = 1.0                # Estado padrão: ligada (1.0) ou desligada (0.0)
        self._is_on_input = False

    def set_position(self, position):
        self.position = list(position)

    def toogle_on_of(self):
        self._is_on_input = not self._is_on_input


    def send_to_shader(self, shader_program, index: int, is_camera_inside: bool):
        """
        Injeta os dados desta luz diretamente no elemento correspondente
        do array 'lights[index]' no fragment shader.
        """
        # Define se a luz deve se manifestar baseado no isolamento de ambiente
        if self.is_internal:
            # Luz interna só brilha se a câmera estiver dentro e a luz estiver ligada
            active_status = self.is_on if is_camera_inside and self._is_on_input else 0.0
        else:
            # Luz externa só brilha se a câmera estiver fora e a luz estiver ligada
            active_status = self.is_on if not is_camera_inside and self._is_on_input else 0.0

        # Monta as strings de localização para o array do GLSL
        loc_pos = glGetUniformLocation(shader_program, f"lights[{index}].position")
        loc_col = glGetUniformLocation(shader_program, f"lights[{index}].color")
        loc_on  = glGetUniformLocation(shader_program, f"lights[{index}].is_on")

        # Envia os dados brutos para a GPU
        glUniform3f(loc_pos, self.position[0], self.position[1], self.position[2])
        glUniform3f(loc_col, self.color[0], self.color[1], self.color[2])
        glUniform1f(loc_on, active_status)
