"""
Constantes para a configuração do código
"""

import os

# Caminhos para assets e shaders
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHADER_DIR = os.path.join(PROJECT_ROOT, "shaders")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Configurações da janela GFLW
WIDTH, HEIGHT = 1280, 720
TITLE = "Mario in the Wonderland"

# Configurações globais da iluminação
POINT_LIGHTS_NMR = 3

# Modos de uso da cena final
MODES = {
    "viz": 0,
    "light": 1,
    "edit": 2,
}
