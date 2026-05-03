"""Entry point. Rodar a partir da raiz do projeto:  python -m src.main"""
import functools
import os

import glfw
from OpenGL.GL import *

from src.camera import Camera
from src.gl_setup import init_window, setup_gl_state
from src.graphic_object import ObjetoGrafico
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


def _add_model(registry, scene, obj_path, tex_path, **kwargs):
    """Atalho: registra mesh, cria ObjetoGrafico e adiciona à scene. Retorna o objeto."""
    handle = registry.register(
        os.path.join(ASSETS_DIR, obj_path),
        [os.path.join(ASSETS_DIR, tex_path)],
    )
    obj = ObjetoGrafico(mesh_handle=handle, **kwargs)
    scene.add(obj)
    return obj


def main():
    window = init_window(WIDTH, HEIGHT, TITLE)
    setup_gl_state()

    shader = Shader(
        os.path.join(SHADER_DIR, "vertex_shader.vs"),
        os.path.join(SHADER_DIR, "fragment_shader.fs"),
    )
    shader.use()
    program = shader.get_program()

    registry = MeshRegistry()
    camera = Camera(position=(0.0, 2.0, 3.0))  # dentro da sala, olhando -Z
    scene = Scene(camera=camera)
    input_mgr = InputManager()

    # ===================================================================
    # AMBIENTE INTERNO — sala do castelo, em torno da origem.
    # castleroom64 delimita o ambiente (não conta nos 6 da req. 2).
    # ===================================================================
    _add_model(registry, scene, "castleroom64/castleroom64.obj",
               "castleroom64/castleroom64_tex.png",
               position=(0.0, 0.0, 0.0))

    _add_model(registry, scene, "quadro64/quadro64.obj",
               "quadro64/quadro64_tex.png",
               position=(0.0, 2.0, -4.0))  # parede norte

    # Duas tochas (mesmo modelo repetido — vale como 1 modelo, req. 2)
    _add_model(registry, scene, "torch64/torch64.obj",
               "torch64/torch64_tex.png",
               position=(-3.0, 1.5, -4.0))
    _add_model(registry, scene, "torch64/torch64.obj",
               "torch64/torch64_tex.png",
               position=(3.0, 1.5, -4.0))

    _add_model(registry, scene, "toad64/toad64.obj",
               "toad64/toad64_tex.png",
               position=(-3.0, 0.0, 0.5))

    # ===================================================================
    # AMBIENTE EXTERNO — z bem negativo, "do outro lado do quadro".
    # chao64 delimita o piso externo (não conta nos 6 da req. 2).
    # ===================================================================
    _add_model(registry, scene, "chao64/chao64.obj",
               "chao64/char64_tex.png",  # nome real do arquivo de textura
               position=(0.0, 0.0, -20.0))

    _add_model(registry, scene, "boo64/boo64.obj",
               "boo64/boo64_tex.png",
               position=(-3.0, 2.0, -18.0))

    _add_model(registry, scene, "pipe64/pipe64.obj",
               "pipe64/pipe64_tex.png",
               position=(5.0, 0.0, -22.0))

    # ===================================================================
    # Modelos com transformação por teclado (req. 7) — um para cada.
    # ===================================================================
    mario = _add_model(registry, scene, "mario64/mario64.obj",
                       "mario64/mario64_textura.png",
                       position=(0.0, 0.0, -15.0))

    estrela = _add_model(registry, scene, "estrela/estrela.obj",
                         "estrela/estrela.png",
                         position=(3.0, 2.0, -15.0),
                         rotation_axis=(0, 1, 0))

    arvore = _add_model(registry, scene, "arvore64/arvore64.obj",
                        "arvore64/arvore64_tex.png",
                        position=(-5.0, 0.0, -22.0))

    # Bindings da req. 7 (translação, rotação, escala — uma cada):
    input_mgr.on_hold(glfw.KEY_UP,    lambda: mario.translate(0, 0, -0.2))
    input_mgr.on_hold(glfw.KEY_DOWN,  lambda: mario.translate(0, 0,  0.2))
    input_mgr.on_hold(glfw.KEY_LEFT,  lambda: mario.translate(-0.2, 0, 0))
    input_mgr.on_hold(glfw.KEY_RIGHT, lambda: mario.translate( 0.2, 0, 0))

    input_mgr.on_hold(glfw.KEY_R,     lambda: estrela.rotate(2.0))         # rotação Y

    input_mgr.on_hold(glfw.KEY_EQUAL, lambda: arvore.scale_by(1.05))       # tecla "="
    input_mgr.on_hold(glfw.KEY_MINUS, lambda: arvore.scale_by(0.95))       # tecla "-"

    # CRÍTICO: chamar upload_to_gpu DEPOIS de todos os register(). Caso contrário
    # os VBOs sobem vazios e nada renderiza (o parse/append acontece em CPU).
    registry.upload_to_gpu(program)

    # Bounds da câmera — perimetra a sala + área externa, com folga.
    camera.set_bounds((-15.0, 0.5, -30.0), (15.0, 10.0, 10.0))

    state = {
        "polygonal_mode": False,
        "delta_time": 0.0,
        "last_frame": 0.0,
    }

    glfw.set_key_callback(window, functools.partial(key_callback, camera, input_mgr, state))
    glfw.set_cursor_pos_callback(window, functools.partial(mouse_callback, camera))
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # Captura o cursor — mesmo padrão FPS do notebook do professor (Aula 13).
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
