"""Persistência do layout da cena: salva/carrega posição, rotação e escala de cada objeto."""
import json
import os

LAYOUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scene_layout.json",
)


def load_layout(named_objects):
    """Aplica posições salvas nos objetos. Chamada após criar todos os objetos."""
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
    print(f"[editor] Layout carregado de {LAYOUT_PATH}")


def save_layout(named_objects):
    """Serializa o estado atual de todos os objetos para JSON."""
    data = {}
    for name, obj in named_objects:
        data[name] = {
            "position": obj.position,
            "rotation_angle": obj.rotation_angle,
            "scale": obj.scale,
        }
    with open(LAYOUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[editor] Layout salvo em {LAYOUT_PATH}")
