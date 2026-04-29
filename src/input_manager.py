"""InputManager: roteia eventos de tecla para callbacks específicos.

Usado para amarrar uma tecla a uma transformação de UM objeto específico
(req. 7: cada transformação ligada a um modelo distinto).
"""
import glfw


class InputManager:
    def __init__(self):
        self._on_press = {}   # disparado uma vez no PRESS
        self._on_hold = {}    # disparado em PRESS e em REPEAT (segurar tecla)

    def on_press(self, key, callback):
        self._on_press[key] = callback

    def on_hold(self, key, callback):
        self._on_hold[key] = callback

    def dispatch(self, key, action):
        if action == glfw.PRESS:
            if key in self._on_press:
                self._on_press[key]()
            if key in self._on_hold:
                self._on_hold[key]()
        elif action == glfw.REPEAT:
            if key in self._on_hold:
                self._on_hold[key]()
