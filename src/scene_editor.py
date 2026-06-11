"""Garante a persistência do layout da cena: salva/carrega posição, rotação e escala de cada objeto."""

import json
import os
import glm, math

LAYOUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scene_layout.json",
)

# Passo de edição por quadro (enquanto a tecla está pressionada).
_T = 0.25   # translação (unidades)
_R = 1.0    # rotação (graus)
_S = 1.02   # escala (fator multiplicativo)
_K_LIGHT_PARAMS = 0.1
_SHININESS = 1.0

class SceneEditor():
    def __init__(self):
        self._named_objects = []  # Lista com
        self.curr_edit_idx = 0

    # Metodos para manipular a estrutura de dados interna
    def add_object(self, name, obj):
        """Adciona um novo objeto na lista"""

        registry = (name, obj)
        self._named_objects.append(registry)

    def get_editing_object(self):
        """Retorna a referencia ao objeto sendo atualmente editado"""

        return self._named_objects[self.curr_edit_idx][1]

    def get_editing_object_name(self):
        """Retorna o nome do atual objeto em edição"""

        return self._named_objects[self.curr_edit_idx][0]

    def set_next_object_to_edit(self):
        """Altera o estado para tornar editar o próximo objeto na lista"""

        self.curr_edit_idx += 1 % len(self._named_objects)

    def set_previous_object_to_edit(self):
        """Altera o estado para tornar editar o objeto anterior na lista"""

        self.curr_edit_idx -= 1 % len(self._named_objects)


    # Metodos para carregar o objeto
    def load_layout(self, camera=None):
        """Aplica posições salvas nos objetos e, opcionalmente, restaura a câmera."""
        if not os.path.exists(LAYOUT_PATH):
            return

        # Carregando o arquivo
        with open(LAYOUT_PATH) as f:
            data = json.load(f)

        # Passando os dados salvos para o objeto na memória
        for name, obj in self._named_objects:
            if name in data:
                d = data[name]
                obj.position = d["position"]
                obj.rotation_angle = d["rotation_angle"]
                obj.scale = d["scale"]
                obj.k_diffuse = d["k_diffuse"]
                obj.k_specular = d["k_specular"]
                obj.shininess = d["shininess"]

        if camera is not None and "_camera" in data:
            c = data["_camera"]
            camera.position.x, camera.position.y, camera.position.z = c["position"]
            camera.yaw = c["yaw"]
            camera.pitch = c["pitch"]

            # reconstroi front a partir de yaw/pitch restaurados
            front = glm.vec3()
            front.x = math.cos(math.radians(camera.yaw)) * math.cos(math.radians(camera.pitch))
            front.y = math.sin(math.radians(camera.pitch))
            front.z = math.sin(math.radians(camera.yaw)) * math.cos(math.radians(camera.pitch))
            camera.front = glm.normalize(front)
        print(f"[editor] Layout carregado de {LAYOUT_PATH}")


    def save_layout(self, camera=None):
        """Serializa o estado atual de todos os objetos e da câmera para JSON."""
        data = {}
        for name, obj in self._named_objects:
            data[name] = {
                "position": obj.position,
                "rotation_angle": obj.rotation_angle,
                "scale": obj.scale,
                "k_diffuse": obj.k_diffuse,
                "k_specular": obj.k_specular,
                "shininess": obj.shininess
            }
        if camera is not None:
            data["_camera"] = {
                "position": [camera.position.x, camera.position.y, camera.position.z],
                "yaw": camera.yaw,
                "pitch": camera.pitch,
            }
        with open(LAYOUT_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[editor] Layout salvo em {LAYOUT_PATH}")


    # Métodos para a edição das posições
    def move_editing_obj_plus_y(self):
        self.get_editing_object().translate(0,  _T, 0)

    def move_editing_obj_minus_y(self):
        self.get_editing_object().translate(0, -_T, 0)

    def move_editing_obj_minus_x(self):
        self.get_editing_object().translate(-_T, 0, 0)

    def move_editing_obj_plus_x(self):
        self.get_editing_object().translate( _T, 0, 0)

    def move_editing_obj_minus_z(self):
        self.get_editing_object().translate(0, 0, -_T)

    def move_editing_obj_plus_z(self):
        self.get_editing_object().translate(0, 0,  _T)

    # Métodos para a edição de rotação e escala
    def rotate_editing_obj_clockwise(self):
        self.get_editing_object().rotate( _R)

    def rotate_editing_not_clockwise(self):
        self.get_editing_object().rotate(-_R)

    def scale_up_editing_obj(self):
        self.get_editing_object().scale_by(_S)

    def scale_down_editing_obj(self):
        self.get_editing_object().scale_by(1.0 / _S)


    # Métodos para a edição de parametros de luz em objetos individuais
    def increase_k_specular_obj(self):
        if self.get_editing_object().k_specular < 1.0:
            self.get_editing_object().k_specular += _K_LIGHT_PARAMS

    def decrease_k_specular_obj(self):
        if self.get_editing_object().k_specular > 0.0:
            self.get_editing_object().k_specular -= _K_LIGHT_PARAMS

    def increase_k_diffuse_obj(self):
        if self.get_editing_object().k_diffuse < 1.0:
            self.get_editing_object().k_specular += _K_LIGHT_PARAMS

    def decrease_k_diffuse_obj(self):
        if self.get_editing_object().k_diffuse > 0.0:
            self.get_editing_object().k_specular -= _K_LIGHT_PARAMS

    def increase_shininess_obj(self):
        if self.get_editing_object().shininess < 128.0:
            self.get_editing_object().shininess += _SHININESS

    def decrease_shininess_obj(self):
        if self.get_editing_object().shininess > 0.0:
            self.get_editing_object().shininess -= _SHININESS
