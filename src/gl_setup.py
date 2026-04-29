"""Helpers para inicializar a janela GLFW e o estado base do OpenGL."""
import glfw
from OpenGL.GL import *


def init_window(width, height, title):
    """Inicializa GLFW, cria a janela invisível e retorna o handle.

    Mantemos a janela escondida até o setup de buffers terminar (igual à base do prof).
    """
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")
    glfw.make_context_current(window)
    return window


def setup_gl_state():
    """Liga as flags de GL usadas pela cena: textura 2D, blending, line-smooth, depth-test."""
    glEnable(GL_TEXTURE_2D)
    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_DEPTH_TEST)
