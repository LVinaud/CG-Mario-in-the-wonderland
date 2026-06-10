"""Scene: agrupa câmera, skybox e a lista de objetos. Quem chama draw é ela."""

from src.scene_editor import SceneEditor

class Scene:
    def __init__(self, camera, skybox=None):
        self.camera = camera
        self.skybox = skybox
        self.objects = []

        self.scene_editor = SceneEditor()

        # Dicionaário que gerencia o estado da cena
        self.state = {
            "polygonal_mode": False,
            "delta_time": 0.0,
            "last_frame": 0.0,
            "mode": "viz",  # Garante que a cena comece no modo de visualização
        }

    def add(self, obj):
        self.objects.append(obj)

    def draw(self, shader_program):
        # Renderiza primeiro o skybox e depois os objetos
        if self.skybox is not None:
            self.skybox.draw(shader_program)
        for obj in self.objects:
            obj.draw(shader_program)
