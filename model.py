from __future__ import annotations
from typing import *
from abc import ABC, abstractmethod
from z3.z3util import BoolRef, Or, And
from dataclasses import dataclass

from z3types import *

@dataclass(frozen=True)
class Transition:
    state_func: Callable[Tuple[Z3State, Z3State], BoolLike]
    condition: Callable[[Z3Variables], BoolLike]

class Z3Model:
    def __init__(self,
                 initial_states: FrozenSet[Z3FuncState],
                 states: FrozenSet[Z3FuncState],
                 transitions: FrozenSet[Transition]):

        self._initial_states = initial_states
        self._states = states
        self._transitions = transitions

    def exists_initial(self, state: Z3State):
        return Or(*(state_func(state) for state_func in self._initial_states))

    def exists_state(self, state: Z3State):
        return Or(*(state_func(state) for state_func in self._states))

    def exists_transition(self, state1: Z3State, state2: Z3State):
        return Or(*(state_func(state1, state2) for state_func in self._transitions))

    def label(self, state: Z3State):
        return Or(*(state_func(state) for state_func in self._states)) # placeholder

    def state_count(self):
        return len(self._states)
