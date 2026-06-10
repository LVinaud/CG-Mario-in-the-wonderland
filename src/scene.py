"""Scene: agrupa câmera, skybox e a lista de objetos. Quem chama draw é ela."""

from src.scene_editor import SceneEditor

class Scene:
    def __init__(self, camera, skybox=None):
        self.camera = camera
        self.skybox = skybox
        self.objects = []

        self.scene_editor = SceneEditor()

        # Atributos para a gerência do estado da cena
        self.is_at_polygonal_mode = False
        self.mode = "viz"

        # Atributos para calculos com framerate
        self.delta_time = 0.0
        self.last_frame = 0.0


    def add(self, obj):
        self.objects.append(obj)

    def draw(self, shader_program):
        # Renderiza primeiro o skybox e depois os objetos
        if self.skybox is not None:
            self.skybox.draw(shader_program)
        for obj in self.objects:
            obj.draw(shader_program)
