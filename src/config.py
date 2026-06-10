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


# Modos de uso da cena final
MODE_VIZ = "viz"
MODE_LIGHT = "light"
MODE_EDIT = "edit"
