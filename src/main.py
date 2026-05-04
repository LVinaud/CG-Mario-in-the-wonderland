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
from src.scene_editor import load_layout, save_layout
from src.shader import Shader
from src.skybox import Skybox
from src.transforms import make_projection, make_view


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
    """Escala apenas o eixo Y (req. 7 — escala em UM eixo só)."""
    obj.scale[1] *= factor


def key_callback(camera, input_mgr, state, window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        # Só persiste se estiver em modo edit — assim a demonstração da req. 7
        # (mover boo, rotacionar estrela, etc.) não sobrescreve o layout salvo.
        if state["mode"] == "edit":
            save_layout(state["editor_objects"], camera)
        else:
            print("[modo viz] alterações não salvas (use modo edit para salvar)")
        glfw.set_window_should_close(window, True)
        return

    if key == glfw.KEY_P and action == glfw.PRESS:
        state["polygonal_mode"] = not state["polygonal_mode"]
        return

    # T — alterna entre modo viz (req. trabalho) e modo edit
    if key == glfw.KEY_T and action == glfw.PRESS:
        state["mode"] = "edit" if state["mode"] == "viz" else "viz"
        print(f"[modo] {state['mode']}")
        return

    # TAB / SHIFT+TAB — só funciona no modo edit
    if key == glfw.KEY_TAB and action == glfw.PRESS and state["mode"] == "edit":
        objs = state["editor_objects"]
        delta = -1 if (mods & glfw.MOD_SHIFT) else 1
        state["editor_idx"] = (state["editor_idx"] + delta) % len(objs)
        name, _ = objs[state["editor_idx"]]
        print(f"[editor] Selecionado: {name}  (TAB = próximo, SHIFT+TAB = anterior)")
        return

    if action in (glfw.PRESS, glfw.REPEAT):
        dt = state["delta_time"]
        # Câmera — WASD
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
    camera = Camera(position=(0.0, 2.0, 3.0))
    scene = Scene(camera=camera)
    input_mgr = InputManager()

    # ===================================================================
    # SKYBOX (req. 8)
    # ===================================================================
    skybox_h = registry.register(
        os.path.join(ASSETS_DIR, "skybox/skybox.obj"),
        [os.path.join(ASSETS_DIR, "skybox/skybox.png")],
    )
    scene.skybox = Skybox(skybox_h, scale=1.0)

    # ===================================================================
    # AMBIENTE INTERNO — sala do castelo
    # ===================================================================
    castleroom = _add_model(registry, scene, "castleroom64/castleroom64.obj",
                            "castleroom64/castleroom64_tex.png",
                            position=(0.0, 0.0, 0.0))

    quadro = _add_model(registry, scene, "quadro64/quadro64.obj",
                        "quadro64/quadro64_tex.png",
                        position=(0.0, 2.0, -4.0))

    torch1 = _add_model(registry, scene, "torch64/torch64.obj",
                        "torch64/torch64_tex.png",
                        position=(-3.0, 1.5, -4.0))
    torch2 = _add_model(registry, scene, "torch64/torch64.obj",
                        "torch64/torch64_tex.png",
                        position=(3.0, 1.5, -4.0))

    toad = _add_model(registry, scene, "toad64/toad64.obj",
                      "toad64/toad64_tex.png",
                      position=(-3.0, 0.0, 0.5))

    # ===================================================================
    # AMBIENTE EXTERNO
    # ===================================================================
    chao = _add_model(registry, scene, "chao64/chao64.obj",
                      "chao64/char64_tex.png",
                      position=(0.0, 0.0, -20.0))

    boo = _add_model(registry, scene, "boo64/boo64.obj",
                     "boo64/boo64_tex.png",
                     position=(-3.0, 2.0, -18.0))

    pipe = _add_model(registry, scene, "pipe64/pipe64.obj",
                      "pipe64/pipe64_tex.png",
                      position=(5.0, 0.0, -22.0))
    pipe2 = _add_model(registry, scene, "pipe64/pipe64.obj",
                       "pipe64/pipe64_tex.png",
                       position=(-5.0, 0.0, -22.0))
    pipe3 = _add_model(registry, scene, "pipe64/pipe64.obj",
                       "pipe64/pipe64_tex.png",
                       position=(0.0, 0.0, -25.0))

    # ===================================================================
    # Objetos com transformação por teclado
    # ===================================================================
    mario = _add_model(registry, scene, "mario64/mario64.obj",
                       "mario64/mario64_tex.png",
                       position=(0.0, 0.0, -15.0))

    estrela = _add_model(registry, scene, "estrela/estrela.obj",
                         "estrela/estrela.png",
                         position=(3.0, 2.0, -15.0),
                         rotation_axis=(0, 1, 0))

    arvore = _add_model(registry, scene, "arvore64/arvore64.obj",
                        "arvore64/arvore64_tex.png",
                        position=(-5.0, 0.0, -22.0))

    plataforma1 = _add_model(registry, scene, "plataforma64/plataforma64.obj",
                             "plataforma64/plataforma64_tex.png",
                             position=(3.0, 0.0, -20.0))
    plataforma2 = _add_model(registry, scene, "plataforma64/plataforma64.obj",
                             "plataforma64/plataforma64_tex.png",
                             position=(-3.0, 0.0, -20.0))

    boo2 = _add_model(registry, scene, "boo64/boo64.obj",
                      "boo64/boo64_tex.png",
                      position=(3.0, 2.0, -20.0))
    boo3 = _add_model(registry, scene, "boo64/boo64.obj",
                      "boo64/boo64_tex.png",
                      position=(-3.0, 2.0, -20.0))
    boo4 = _add_model(registry, scene, "boo64/boo64.obj",
                      "boo64/boo64_tex.png",
                      position=(0.0, 2.0, -25.0))
    boo5 = _add_model(registry, scene, "boo64/boo64.obj",
                      "boo64/boo64_tex.png",
                      position=(5.0, 2.0, -25.0))

    porta = _add_model(registry, scene, "porta64/porta64.obj",
                       "porta64/Inside_baseColor.png",
                       position=(0.0, 0.0, -4.0))

    # 16 moedinhas — todas giram continuamente no loop
    coins = []
    for i in range(16):
        c = _add_model(registry, scene, "coin64/coin.obj",
                       "coin64/coin.png",
                       position=(float(i) * 2.0, 1.0, -18.0),
                       rotation_axis=(0, 1, 0))
        coins.append(c)

    # 15 árvores
    trees = []
    for i in range(15):
        t = _add_model(registry, scene, "arvore64/arvore64.obj",
                       "arvore64/arvore64_tex.png",
                       position=(float(i) * 3.0, 0.0, -30.0))
        trees.append(t)

    # CRÍTICO: upload_to_gpu APÓS todos os register().
    registry.upload_to_gpu(program)

    # ===================================================================
    # Editor de cena — lista de objetos nomeados
    # ===================================================================
    editor_objects = [
        ("castleroom", castleroom),
        ("quadro",     quadro),
        ("torch1",     torch1),
        ("torch2",     torch2),
        ("toad",       toad),
        ("chao",       chao),
        ("boo",        boo),
        ("pipe",       pipe),
        ("pipe2",      pipe2),
        ("pipe3",      pipe3),
        ("mario",      mario),
        ("estrela",    estrela),
        ("arvore",     arvore),
        ("plataforma1", plataforma1),
        ("plataforma2", plataforma2),
        ("boo2",        boo2),
        ("boo3",        boo3),
        ("boo4",        boo4),
        ("boo5",        boo5),
        ("porta",       porta),
        *[(f"coin{i+1}",  coins[i])  for i in range(16)],
        *[(f"arvore{i+2}", trees[i]) for i in range(15)],
    ]

    # Aplica layout salvo anteriormente (se existir)
    load_layout(editor_objects, camera)

    state = {
        "polygonal_mode": False,
        "delta_time": 0.0,
        "last_frame": 0.0,
        "editor_objects": editor_objects,
        "editor_idx": 0,
        "mode": "viz",  # padrão = modo dos requisitos do trabalho
    }

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

    # Bindings com chaveamento por modo (uma callback por tecla, ramifica internamente)
    def _up():
        if state["mode"] == "edit": _sel(state).translate(0,  _T, 0)
        else:                       boo.translate(0, 0, -_T)
    def _down():
        if state["mode"] == "edit": _sel(state).translate(0, -_T, 0)
        else:                       boo.translate(0, 0,  _T)
    def _left():
        if state["mode"] == "edit": _sel(state).translate(-_T, 0, 0)
        else:                       boo.translate(-_T, 0, 0)
    def _right():
        if state["mode"] == "edit": _sel(state).translate( _T, 0, 0)
        else:                       boo.translate( _T, 0, 0)
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

    camera.set_bounds((-65, 0.5, -65), (65, 65, 65))

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

        for coin in coins:
            coin.rotate(90.0 * state["delta_time"])

        glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_TRUE, view_mat)
        glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_TRUE, proj_mat)

        scene.draw(program)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
