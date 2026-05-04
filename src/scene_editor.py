"""Garante a persistência do layout da cena: salva/carrega posição, rotação e escala de cada objeto."""

import json
import os
import glm, math

LAYOUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scene_layout.json",
)


def load_layout(named_objects, camera=None):
    """Aplica posições salvas nos objetos e, opcionalmente, restaura a câmera."""
    if not os.path.exists(LAYOUT_PATH):
        return
    with open(LAYOUT_PATH) as f:
        data = json.load(f)
    for name, obj in named_objects:
        if name in data:
            d = data[name]
            obj.position = d["position"]
            obj.rotation_angle = d["rotation_angle"]
            obj.scale = d["scale"]
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


def save_layout(named_objects, camera=None):
    """Serializa o estado atual de todos os objetos e da câmera para JSON."""
    data = {}
    for name, obj in named_objects:
        data[name] = {
            "position": obj.position,
            "rotation_angle": obj.rotation_angle,
            "scale": obj.scale,
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
