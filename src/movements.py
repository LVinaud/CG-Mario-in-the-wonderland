import math
from src.graphic_object import ObjetoGrafico

def orbit_around_xz(obj, center_x, center_z, radius, speed, delta_time):
        """
        Translada o objeto em um movimento circular ao redor de um centro coordenado (X, Z).
        Garante que o objeto não seja estático.
        """
        if obj.static:
            return

        # Se o objeto ainda não possui um ângulo de órbita interno, inicializa ele
        if not hasattr(obj, "_orbit_angle"):
            # Tenta deduzir o ângulo inicial com base na posição atual do objeto
            dx = obj.position[0] - center_x
            dz = obj.position[2] - center_z
            obj._orbit_angle = math.atan2(dz, dx)

        # Atualiza o ângulo acumulado com base na velocidade e no tempo decorrido
        obj._orbit_angle += speed * delta_time

        # Calcula as novas coordenadas X e Z com base nas equações polares
        obj.position[0] = center_x + radius * math.cos(obj._orbit_angle)
        obj.position[2] = center_z + radius * math.sin(obj._orbit_angle)

        # Efeito flutuação em Y (Para dar um aspecto fantasmagórico flutuante)
        # Faz o Boo subir e descer de leve usando uma onda senoidal baseada no próprio ângulo
        if not hasattr(obj, "_base_y"):
            obj._base_y = obj.position[1]
        obj.position[1] = obj._base_y + math.sin(obj._orbit_angle * 8.0) * 0.3

def orbit_arount_zy(obj, center_z, center_y, radius, speed, delta_time, fixed_x):
        """
        Translada o objeto em um movimento circular vertical no plano Z-Y.
        Garante que o objeto não seja estático.
        """
        if obj.static:
            return

        # Se o objeto ainda não possui um ângulo de órbita interno para esse plano, inicializa ele
        if not hasattr(obj, "_orbit_angle_zy"):
            # Deduz o ângulo inicial com base na posição Z e Y atual do objeto
            dz = obj.position[2] - center_z
            dy = obj.position[1] - center_y
            obj._orbit_angle_zy = math.atan2(dy, dz)

        # Atualiza o ângulo acumulado com base na velocidade e no tempo decorrido
        obj._orbit_angle_zy += speed * delta_time

        # Trava o eixo X na profundidade escolhida
        obj.position[0] = fixed_x

        # Calcula as novas coordenadas Z e Y (movimento circular vertical)
        obj.position[2] = center_z + radius * math.cos(obj._orbit_angle_zy)
        obj.position[1] = center_y + radius * math.sin(obj._orbit_angle_zy)


def _scale_y(obj, factor):
    """Escala apenas o eixo Y. Função usada para escalar um dos canos externos da cena"""
    obj.scale[1] *= factor
