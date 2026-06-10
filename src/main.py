import functools
import os

import glfw
from OpenGL.GL import *

from src.camera import Camera
from src.gl_setup import init_window, setup_gl_state
from src.graphic_object import ObjetoGrafico
from src.input_manager import InputManager
from src.scene_editor import SceneEditor
from src.mesh_registry import MeshRegistry
from src.scene import Scene
from src.shader import Shader
from src.skybox import Skybox
from src.transforms import make_projection, make_view

# Constantes do código
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHADER_DIR = os.path.join(PROJECT_ROOT, "shaders")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

WIDTH, HEIGHT = 1280, 720
TITLE = "Mario in the Wonderland"

# Passo de edição por quadro (enquanto a tecla está pressionada).
_T = 0.25   # translação (unidades)
_R = 1.0    # rotação (graus)
_S = 1.02   # escala (fator multiplicativo)


def _sel(state):
    """Retorna o objeto atualmente selecionado no editor."""
    return state["editor_objects"][state["editor_idx"]][1]


def _scale_y(obj, factor):
    """Escala apenas o eixo Y. Função usada para escalar um dos canos externos da cena"""
    obj.scale[1] *= factor


def key_callback(camera, input_mgr, scene_editor, state, window, key, scancode, action, mods):
    """Callback dos inputs da Window GFLW para a lógica interna do código"""

    # Configurando as ações na edição ao fechar a cena com ESC
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        # Só persiste se estiver em modo edit
        # Alterações em viz não sobrescrevem o .json da configuração inicial da cena.
        if state["mode"] == "edit":
            scene_editor.save_layout(camera)
        else:
            print("[modo viz] alterações não salvas (use modo edit para salvar)")
        glfw.set_window_should_close(window, True)
        return

    # P - Ativa o modo poligonal
    if key == glfw.KEY_P and action == glfw.PRESS:
        state["polygonal_mode"] = not state["polygonal_mode"]
        return

    # T - alterna entre modo viz e modo edit
    if key == glfw.KEY_T and action == glfw.PRESS:
        state["mode"] = "edit" if state["mode"] == "viz" else "viz"
        print(f"[modo] {state['mode']}")
        return

    # TAB / SHIFT+TAB. Só funciona no modo edit
    if key == glfw.KEY_TAB and action == glfw.PRESS and state["mode"] == "edit":
        objs = state["editor_objects"]
        delta = -1 if (mods & glfw.MOD_SHIFT) else 1
        state["editor_idx"] = (state["editor_idx"] + delta) % len(objs)
        name, _ = objs[state["editor_idx"]]
        print(f"[editor] Selecionado: {name}  (TAB = próximo, SHIFT+TAB = anterior)")
        return

    # WASD - Movimento de câmera
    if action in (glfw.PRESS, glfw.RELEASE):
        is_pressed = action == glfw.PRESS

        # Configura a camera para mexer no frame caso is_pressed seja verdadeiro
        if key == glfw.KEY_W:
            camera.is_moving_forward = is_pressed
            return
        if key == glfw.KEY_S:
            camera.is_moving_backward = is_pressed
            return
        if key == glfw.KEY_A:
            camera.is_moving_left = is_pressed
            return
        if key == glfw.KEY_D:
            camera.is_moving_right = is_pressed
            return

    input_mgr.dispatch(key, action)


def mouse_callback(camera, window, xpos, ypos):
    camera.process_mouse(xpos, ypos)


def framebuffer_size_callback(window, w, h):
    glViewport(0, 0, w, h)

def _generate_obj_paths(obj_name):
    """
    Auxiliar que gera o caminho o para um objeto dado a string do seu nome de registro.
    Retorna o caminho para o .obj e para o arquivo de textura respectivamente
    """

    folder_name = obj_name + "64/"
    obj_file_name = folder_name + obj_name +"64.obj"
    tex_file_name = folder_name + obj_name + "64_tex.png"

    return obj_file_name, tex_file_name

def _add_model(registry, scene, scene_editor, obj_name, instance_idx=0):
    """Auxiliar para registrar mesh, criar ObjetoGrafico e adicionar à cena. Retornando o objeto."""

    # Criando os caminhos para os arquivos
    obj_path, tex_path = _generate_obj_paths(obj_name)

    # Carregando em Registry
    handle = registry.register(
        os.path.join(ASSETS_DIR, obj_path),
        [os.path.join(ASSETS_DIR, tex_path)],
    )

    # Adcionando referencia as estruturas de controle do código
    obj = ObjetoGrafico(mesh_handle=handle)
    scene.add(obj)

    # Adcionando no editor com o nome correto
    if instance_idx > 0:
        scene_editor.add_object(obj_name+str(instance_idx), obj)
    else:
        scene_editor.add_object(obj_name, obj)
    return obj


def main():
    window = init_window(WIDTH, HEIGHT, TITLE)

    # Inicialicando o OpenGl e os Objetos Singletons
    setup_gl_state()

    shader = Shader(
        os.path.join(SHADER_DIR, "vertex_shader.vs"),
        os.path.join(SHADER_DIR, "fragment_shader.fs"),
    )
    shader.use()
    program = shader.get_program()

    registry = MeshRegistry()
    input_mgr = InputManager()
    camera = Camera(position=(0.0, 2.0, 3.0))
    scene = Scene(camera=camera)
    scene_editor = SceneEditor()

    # Configurando o skybox
    skybox_h = registry.register(
        os.path.join(ASSETS_DIR, "skybox/skybox.obj"),
        [os.path.join(ASSETS_DIR, "skybox/skybox.png")],
    )
    scene.skybox = Skybox(skybox_h, scale=1.0)

    # Configurando os limites físicos da câmera (considerando o skybox)
    camera.set_bounds((-65, 0.5, -65), (65, 65, 65))


    # Carregando objetos do ambiente interno (sala do castelo)
    _add_model(registry, scene, scene_editor, "castleroom")
    _add_model(registry, scene, scene_editor, "chao")
    _add_model(registry, scene, scene_editor, "torch", 1)
    _add_model(registry, scene, scene_editor, "torch", 2)
    _add_model(registry, scene, scene_editor, "quadro")

    # Carregando objetos que são personagens no ambiente interno
    _add_model(registry, scene, scene_editor, "toad")
    _add_model(registry, scene, scene_editor, "mario")
    _add_model(registry, scene, scene_editor, "porta")

    # Carregando objetos do ambiente externo
    _add_model(registry, scene, scene_editor, "pipe", 1)
    _add_model(registry, scene, scene_editor, "pipe", 2)
    _add_model(registry, scene, scene_editor, "plataforma", 1)
    _add_model(registry, scene, scene_editor, "plataforma", 2)
    estrela = _add_model(registry, scene, scene_editor, "estrela")

    # Lista de fantasmas :)
    boos = []
    for i in range(4):
        boo = _add_model(registry, scene, scene_editor, "boo", i+1)
        boos.append(boo)

    # Lista de moedas. Todas giram continuamente no loop
    coins = []
    for i in range(16):
        c = _add_model(registry, scene, scene_editor, "coin", i+1)
        coins.append(c)

    # Lista de árvores
    trees = []
    for i in range(16):
        t = _add_model(registry, scene, scene_editor, "arvore", i+1)
        trees.append(t)


    boo_movable = _add_model(registry, scene, scene_editor, "boo") #especial
    pipe3 = _add_model(registry, scene, scene_editor, "pipe", 3) #especial

    # Upload final de todos os objetos carregados na GPU
    registry.upload_to_gpu(program)

    # Aplica layout salvo anteriormente (se existir)
    scene_editor.load_layout(camera)

    state = {
        "polygonal_mode": False,
        "delta_time": 0.0,
        "last_frame": 0.0,
        "editor_objects": scene_editor,
        "editor_idx": 0,
        "mode": "viz",  # Garante que a cena comece no modo de visualização
    }

    # Imprimindo os controles no terminal
    print("[modo viz] (padrão — requisitos do trabalho)")
    print("  Setas        — translada boo")
    print("  Z / X        — rotaciona estrela")
    print("  N / M        — escala pipe3 em Y")
    print("  T            — alterna para modo edit")
    print("[modo edit]")
    print("  TAB / SHIFT+TAB  — próximo/anterior objeto")
    print("  Setas            — translada X/Y do selecionado")
    print("  G / H            — translada Z do selecionado")
    print("  R / F            — rotaciona ±1°")
    print("  = / -            — escala")
    print("[geral] ESC — salva layout e fecha; P — wireframe")

    # Bindings com chaveamento por modo
    def _up():
        if state["mode"] == "edit": _sel(state).translate(0,  _T, 0)
        else:                       boo_movable.translate(0, 0, -_T)
    def _down():
        if state["mode"] == "edit": _sel(state).translate(0, -_T, 0)
        else:                       boo_movable.translate(0, 0,  _T)
    def _left():
        if state["mode"] == "edit": _sel(state).translate(-_T, 0, 0)
        else:                       boo_movable.translate(-_T, 0, 0)
    def _right():
        if state["mode"] == "edit": _sel(state).translate( _T, 0, 0)
        else:                       boo_movable.translate( _T, 0, 0)

    input_mgr.on_hold(glfw.KEY_UP,        _up)
    input_mgr.on_hold(glfw.KEY_DOWN,      _down)
    input_mgr.on_hold(glfw.KEY_LEFT,      _left)
    input_mgr.on_hold(glfw.KEY_RIGHT,     _right)
    input_mgr.on_hold(glfw.KEY_Z,         lambda: state["mode"] == "viz" and estrela.rotate(-_R))
    input_mgr.on_hold(glfw.KEY_X,         lambda: state["mode"] == "viz" and estrela.rotate( _R))
    input_mgr.on_hold(glfw.KEY_N,         lambda: state["mode"] == "viz" and _scale_y(pipe3, 1.0 / _S))
    input_mgr.on_hold(glfw.KEY_M,         lambda: state["mode"] == "viz" and _scale_y(pipe3, _S))

    # Bindings exclusivos do modo edit (teclas sem conflito com a câmera)
    input_mgr.on_hold(glfw.KEY_G,         lambda: state["mode"] == "edit" and _sel(state).translate(0, 0, -_T))
    input_mgr.on_hold(glfw.KEY_H,         lambda: state["mode"] == "edit" and _sel(state).translate(0, 0,  _T))
    input_mgr.on_hold(glfw.KEY_R,         lambda: state["mode"] == "edit" and _sel(state).rotate( _R))
    input_mgr.on_hold(glfw.KEY_F,         lambda: state["mode"] == "edit" and _sel(state).rotate(-_R))
    input_mgr.on_hold(glfw.KEY_EQUAL,     lambda: state["mode"] == "edit" and _sel(state).scale_by(_S))
    input_mgr.on_hold(glfw.KEY_MINUS,     lambda: state["mode"] == "edit" and _sel(state).scale_by(1.0 / _S))



    glfw.set_key_callback(window, functools.partial(key_callback, camera, input_mgr, scene_editor, state))
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

        camera.update(state["delta_time"])

        for coin in coins:
            coin.rotate(90.0 * state["delta_time"])

        glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_TRUE, view_mat)
        glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_TRUE, proj_mat)

        scene.draw(program)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
