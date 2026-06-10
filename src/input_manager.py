"""InputManager: roteia eventos de tecla para callbacks específicos.

Usado para associar uma tecla a uma transformação de UM objeto específico na cena final
"""
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any
import glfw


@dataclass
class InputCallback:
    """
    Tipo criado apenas para formalizar que cada input guardado precisam de uma função
    e uma referencia ao modo no input manager que a tecla usa
    """

    mode_to_use: str
    callback: Callable[..., Any]


class InputManager:
    def __init__(self, mode):
        self.curr_mode = mode
        self._on_press = {}   # Para ações disparadas uma vez no PRESS
        self._on_hold = {}    # Para ações disparadas em PRESS e em REPEAT (segurar tecla)

    def on_press(self, mode_to_use, key, callback):
        """Registra um callback de tecla no dicionário de ações que ocorrem uma vez por pressionamento"""

        self._on_press[key] = InputCallback(mode_to_use, callback)

    def on_hold(self, mode_to_use, key, callback):
        """Registra um callback de tecla no dicionário de ações que ocorrem uma vez por pressionamento"""

        self._on_hold[key] = InputCallback(mode_to_use, callback)

    def dispatch(self, key, action):
        """Recebe a tecla clicada e o tipo de ação do GLFW pela função callback da window e chama a função registrada exata"""

        if action == glfw.PRESS:
            if key in self._on_press and self.curr_mode == self._on_press[key].mode_to_use:
                self._on_press[key].callback()

        elif action == glfw.REPEAT:
            if key in self._on_hold and self.curr_mode == self._on_hold[key].mode_to_use:
                self._on_hold[key].callback()
