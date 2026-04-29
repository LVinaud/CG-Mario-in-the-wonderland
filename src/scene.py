"""Scene: agrupa câmera, skybox e a lista de objetos. Quem chama draw é ela."""


class Scene:
    def __init__(self, camera, skybox=None):
        self.camera = camera
        self.skybox = skybox
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def draw(self, shader_program):
        # skybox primeiro: fica "atrás" no depth buffer e os objetos a sobrepõem
        if self.skybox is not None:
            self.skybox.draw(shader_program)
        for obj in self.objects:
            obj.draw(shader_program)
