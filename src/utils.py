"""
Funções auxiliares para montar a cena
"""

import os

from src.config import ASSETS_DIR, MODE_EDIT, MODE_LIGHT, MODE_VIZ

import functools

import glfw
from OpenGL.GL import *



from src.camera import Camera
from src.gl_setup import init_window, setup_gl_state
from src.graphic_object import ObjetoGrafico
from src.mesh_registry import MeshRegistry
from src.scene import Scene
from src.shader import Shader
from src.skybox import Skybox
from src.transforms import make_projection, make_view



def generate_obj_paths(obj_name):
    """
    Auxiliar que gera o caminho o para um objeto dado a string do seu nome de registro.
    Retorna o caminho para o .obj e para o arquivo de textura respectivamente
    """

    folder_name = obj_name + "64/"
    obj_file_name = folder_name + obj_name +"64.obj"
    tex_file_name = folder_name + obj_name + "64_tex.png"

    return obj_file_name, tex_file_name


def add_model(registry, scene, obj_name, instance_idx=0, is_light_src=False):
    """Auxiliar para registrar mesh, criar ObjetoGrafico e adicionar à cena. Retornando o objeto."""

    # Criando os caminhos para os arquivos
    obj_path, tex_path = generate_obj_paths(obj_name)

    # Carregando em Registry
    handle = registry.register(
        os.path.join(ASSETS_DIR, obj_path),
        [os.path.join(ASSETS_DIR, tex_path)],
    )

    # Adcionando referencia as estruturas de controle do código
    obj = ObjetoGrafico(mesh_handle=handle)

    # Adcionando o objeto na lista correta da cena
    scene.add_object(obj, is_light_src)


    # Adcionando no editor com o nome correto
    if instance_idx > 0:
        scene.scene_editor.add_object(obj_name+str(instance_idx), obj)
    else:
        scene.scene_editor.add_object(obj_name, obj)
    return obj


def framebuffer_size_callback(window, w, h):
    glViewport(0, 0, w, h)


def print_commands_list():
    """Auxiliar para informar os controles do programa"""

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

def create_scene_binds(scene: Scene):
    # Comandos do modo de edição
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_G,
        scene.scene_editor.move_editing_obj_minus_z
    )
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_H,
        scene.scene_editor.move_editing_obj_plus_z
    )
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_R,
        scene.scene_editor.rotate_editing_obj_clockwise
    )
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_F,
        scene.scene_editor.rotate_editing_not_clockwise
    )
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_EQUAL,
        scene.scene_editor.scale_up_editing_obj
    )
    scene.input_mngr.on_hold(
        MODE_EDIT,
        glfw.KEY_MINUS,
        scene.scene_editor.scale_down_editing_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_UP,
        scene.scene_editor.move_editing_obj_plus_y
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_DOWN,
        scene.scene_editor.move_editing_obj_minus_y
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_LEFT,
        scene.scene_editor.move_editing_obj_minus_x
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_RIGHT,
        scene.scene_editor.move_editing_obj_plus_x
    )

    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_1,
        scene.scene_editor.decrease_k_diffuse_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_2,
        scene.scene_editor.increase_k_diffuse_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_3,
        scene.scene_editor.decrease_k_specular_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_4,
        scene.scene_editor.increase_k_specular_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_5,
        scene.scene_editor.decrease_shininess_obj
    )
    scene.input_mngr.on_press(
        MODE_EDIT,
        glfw.KEY_6,
        scene.scene_editor.increase_shininess_obj
    )
