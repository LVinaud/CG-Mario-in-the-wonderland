"""Entry point. Rodar a partir da raiz do projeto:  python -m src.main"""
import functools
import os

# Workaround WSL2/WSLg: pyOpenGL tenta buscar o handle do contexto via GLX,
# mas no WSL o GLFW costuma criar o contexto via EGL e o glXGetCurrentContext
# devolve 0, fazendo glVertexAttribPointer falhar com "no valid context".
# Como usamos apenas UM contexto, basta devolver um handle estável quando
# o real falhar.
import OpenGL.contextdata as _gl_ctxdata
_orig_get_context = _gl_ctxdata.getContext
def _safe_get_context(context=None):
    try:
        return _orig_get_context(context)
    except Exception:
        return 1
_gl_ctxdata.getContext = _safe_get_context

import glfw
from OpenGL.GL import *

from src.camera import Camera
from src.gl_setup import init_window, setup_gl_state
from src.input_manager import InputManager
from src.mesh_registry import MeshRegistry
from src.scene import Scene
from src.shader import Shader
from src.transforms import make_projection, make_view


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHADER_DIR = os.path.join(PROJECT_ROOT, "shaders")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

WIDTH, HEIGHT = 1280, 720
TITLE = "Mario in the Wonderland"


def key_callback(camera, input_mgr, state, window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        return
    if key == glfw.KEY_P and action == glfw.PRESS:
        state["polygonal_mode"] = not state["polygonal_mode"]
        return

    if action in (glfw.PRESS, glfw.REPEAT):
        dt = state["delta_time"]
        if key == glfw.KEY_W:
            camera.move_forward(dt)
            return
        if key == glfw.KEY_S:
            camera.move_backward(dt)
            return
        if key == glfw.KEY_A:
            camera.move_left(dt)
            return
        if key == glfw.KEY_D:
            camera.move_right(dt)
            return

    input_mgr.dispatch(key, action)


def mouse_callback(camera, window, xpos, ypos):
    camera.process_mouse(xpos, ypos)


def framebuffer_size_callback(window, w, h):
    glViewport(0, 0, w, h)


def main():
    window = init_window(WIDTH, HEIGHT, TITLE)
    setup_gl_state()

    shader = Shader(
        os.path.join(SHADER_DIR, "vertex_shader.vs"),
        os.path.join(SHADER_DIR, "fragment_shader.fs"),
    )
    shader.use()
    program = shader.get_program()

    # Instanciando todos os singletons
    registry = MeshRegistry()
    camera = Camera(position=(0, 0, 0))
    scene = Scene(camera=camera)
    input_mgr = InputManager()

    # ---- registro de modelos vai aqui (registry.register(...) -> ObjetoGrafico/Skybox) ----

    # CRÍTICO: chamar upload_to_gpu DEPOIS de todos os register(). Caso contrário
    # os VBOs sobem vazios e nada renderiza (o parse/append acontece em CPU).
    registry.upload_to_gpu(program)

    # Estado mutável compartilhado entre as callbacks e o loop principal.
    state = {
        "polygonal_mode": False,
        "delta_time": 0.0,
        "last_frame": 0.0,
    }

    glfw.set_key_callback(window, functools.partial(key_callback, camera, input_mgr, state))
    glfw.set_cursor_pos_callback(window, functools.partial(mouse_callback, camera))
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    glfw.show_window(window)

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        state["delta_time"] = current_frame - state["last_frame"]
        state["last_frame"] = current_frame

        glfw.poll_events()

        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if state["polygonal_mode"] else GL_FILL)

        view_mat = make_view(camera.position, camera.front, camera.up)
        proj_mat = make_projection(camera.fov, WIDTH / HEIGHT)

        glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_TRUE, view_mat)
        glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_TRUE, proj_mat)

        scene.draw(program)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
