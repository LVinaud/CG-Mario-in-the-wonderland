from OpenGL.GL import *


class Shader:
    """Wrapper enxuto de programa de shader: lê vs/fs de arquivo, compila, linka.

    Observação, mesmo código adaptado da classe usada nas aulas (créditos: https://learnopengl.com).
    """

    def __init__(self, vertex_path: str, fragment_path: str):
        try:
            with open(vertex_path) as f:
                vertex_code = f.read()
            with open(fragment_path) as f:
                fragment_code = f.read()

            vertex = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex, vertex_code)
            glCompileShader(vertex)
            self._check_errors(vertex, "VERTEX")

            fragment = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment, fragment_code)
            glCompileShader(fragment)
            self._check_errors(fragment, "FRAGMENT")

            self.ID = glCreateProgram()
            glAttachShader(self.ID, vertex)
            glAttachShader(self.ID, fragment)
            glLinkProgram(self.ID)
            self._check_errors(self.ID, "PROGRAM")

            glDeleteShader(vertex)
            glDeleteShader(fragment)

        except IOError:
            print("ERROR::SHADER::FILE_NOT_SUCCESFULLY_READ")

    def get_program(self) -> int:
        return self.ID

    def use(self) -> None:
        glUseProgram(self.ID)

    def set_bool(self, name: str, value: bool) -> None:
        glUniform1i(glGetUniformLocation(self.ID, name), int(value))

    def set_int(self, name: str, value: int) -> None:
        glUniform1i(glGetUniformLocation(self.ID, name), value)

    def set_float(self, name: str, value: float) -> None:
        glUniform1f(glGetUniformLocation(self.ID, name), value)

    @staticmethod
    def _check_errors(shader: int, kind: str) -> None:
        if kind != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if not success:
                info = glGetShaderInfoLog(shader)
                print(f"ERROR::SHADER_COMPILATION_ERROR of type: {kind}\n{info.decode()}")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if not success:
                info = glGetProgramInfoLog(shader)
                print(f"ERROR::PROGRAM_LINKING_ERROR of type: {kind}\n{info.decode()}")
