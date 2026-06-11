import functools
import os

import glfw
from OpenGL.GL import *

from src.config import  *
from src.utils import add_model, print_commands_list, create_scene_binds
from src.camera import Camera
from src.gl_setup import init_window, setup_gl_state, mouse_callback, framebuffer_size_callback
from src.mesh_registry import MeshRegistry
from src.scene import Scene
from src.shader import Shader
from src.skybox import Skybox
from src.transforms import make_projection, make_view


MODE_VIZ = "viz"
MODE_LIGHT = "light"
MODE_EDIT = "edit"

def _scale_y(obj, factor):
    """Escala apenas o eixo Y. Função usada para escalar um dos canos externos da cena"""
    obj.scale[1] *= factor


def key_callback(camera, scene: Scene, window, key, scancode, action, mods):
    """Callback dos inputs da Window GFLW para a lógica interna do código"""

    # Configurando as ações na edição ao fechar a cena com ESC
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        # Só persiste se estiver em modo edit
        # Alterações em viz não sobrescrevem o .json da configuração inicial da cena.
        if scene.get_mode() == MODE_EDIT:
            scene.scene_editor.save_layout(camera)
        else:
            print("[modo viz] alterações não salvas (use modo edit para salvar)")
        glfw.set_window_should_close(window, True)
        return

    # P - Ativa o modo poligonal
    if key == glfw.KEY_P and action == glfw.PRESS:
        scene.is_at_polygonal_mode = not scene.is_at_polygonal_mode
        return

    # T - alterna entre modo viz e modo edit
    if key == glfw.KEY_T and action == glfw.PRESS:
        if scene.get_mode() == MODE_VIZ:
            scene.set_mode(MODE_EDIT)
        else:
            scene.set_mode(MODE_VIZ)
        return

    # TAB / SHIFT+TAB. Só funciona no modo edit
    if key == glfw.KEY_TAB and action == glfw.PRESS and scene.get_mode() == "edit":
        # Se shift, volta para o objeto anterior
        if mods & glfw.MOD_SHIFT:
            scene.scene_editor.set_previous_object_to_edit()
        else:
            scene.scene_editor.set_next_object_to_edit()

        # Mostrando o objeto em edição na tela
        name = scene.scene_editor.get_editing_object_name()
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

    scene.input_mngr.dispatch(key, action)


def main():
    window = init_window(WIDTH, HEIGHT, TITLE)

    # Inicialicando o OpenGl e os shaders
    setup_gl_state()
    lightable_shader = Shader(
        os.path.join(SHADER_DIR, "lightable_vertex_shader.vs"),
        os.path.join(SHADER_DIR, "lightable_fragment_shader.fs"),
    )
    light_src_shader = Shader(
        os.path.join(SHADER_DIR, "light_src_vertex_shader.vs"),
        os.path.join(SHADER_DIR, "light_src_fragment_shader.fs"),
    )

    # Criando os objetos singletons para construir a cena
    registry = MeshRegistry()
    camera = Camera(position=(0.0, 2.0, 3.0))
    scene = Scene(camera, MODE_VIZ)

    # Configurando o skybox e os limites da câmera
    skybox_h = registry.register(
        os.path.join(ASSETS_DIR, "skybox/skybox.obj"),
        [os.path.join(ASSETS_DIR, "skybox/skybox.png")],
    )
    scene.skybox = Skybox(skybox_h, scale=1.0)
    camera.set_bounds((-65, 0.5, -65), (65, 65, 65))

    # Carregando objetos do ambiente interno (sala do castelo)
    add_model(registry, scene, "castleroom")
    add_model(registry, scene, "chao")
    add_model(registry, scene, "torch", 1, True)
    add_model(registry, scene, "torch", 2, True)
    add_model(registry, scene, "quadro")

    # Carregando objetos que são personagens no ambiente interno
    add_model(registry, scene, "toad")
    add_model(registry, scene, "mario")
    add_model(registry, scene, "porta")

    # Carregando objetos do ambiente externo
    add_model(registry, scene, "pipe", 1)
    add_model(registry, scene, "pipe", 2)
    add_model(registry, scene, "plataforma", 1)
    add_model(registry, scene, "plataforma", 2)
    estrela = add_model(registry, scene, "estrela", 0, True)

    boos = []
    for i in range(4):
        boo = add_model(registry, scene, "boo", i+1)
        boos.append(boo)

    trees = []
    for i in range(16):
        t = add_model(registry, scene, "arvore", i+1)
        trees.append(t)

    # Objetos especiais que se movem pela cena
    coins = []
    for i in range(16):
        c = add_model(registry, scene, "coin", i+1)
        coins.append(c)

    boo_movable = add_model(registry, scene, "boo") #especial
    pipe3 = add_model(registry, scene, "pipe", 3) #especial

    # Upload final dos objetos na GPU e carregamento dos seus estados na cena
    registry.upload_to_gpu()
    scene.scene_editor.load_layout(camera)

    # Bindings das teclas no input manager por modo e callback
    create_scene_binds(scene)
    print_commands_list()

    # Configurando callbacks da janela
    glfw.set_key_callback(window, functools.partial(key_callback, camera, scene))
    glfw.set_cursor_pos_callback(window, functools.partial(mouse_callback, camera))
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Loop de renderização
    glfw.show_window(window)
    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        scene.delta_time = current_frame - scene.last_frame
        scene.last_frame = current_frame

        glfw.poll_events()

        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if scene.is_at_polygonal_mode else GL_FILL)


        for coin in coins:
            coin.rotate(90.0 * scene.delta_time)

        camera.update(scene.delta_time)
        scene.draw(light_src_shader, lightable_shader, WIDTH / HEIGHT, registry)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
