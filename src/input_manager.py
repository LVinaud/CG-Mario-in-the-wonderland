"""InputManager: roteia eventos de tecla para callbacks específicos.

Usado para associar uma tecla a uma transformação de UM objeto específico na cena final
"""
import glfw


class InputManager:
    def __init__(self):
        self._on_press = {}   # Para ações disparadas uma vez no PRESS
        self._on_hold = {}    # Para ações disparadas em PRESS e em REPEAT (segurar tecla)

    def on_press(self, key, callback):
        """Registra um callback de tecla no dicionário de ações que ocorrem uma vez por pressionamento"""

        self._on_press[key] = callback

    def on_hold(self, key, callback):
        """Registra um callback de tecla no dicionário de ações que ocorrem uma vez por pressionamento"""

        self._on_hold[key] = callback

    def dispatch(self, key, action):
        """Recebe a tecla clicada e o tipo de ação do GLFW pela função callback da window e chama a função registrada exata"""

        if action == glfw.PRESS:
            if key in self._on_press:
                self._on_press[key]()
            if key in self._on_hold:
                self._on_hold[key]()
        elif action == glfw.REPEAT:
            if key in self._on_hold:
                self._on_hold[key]()
