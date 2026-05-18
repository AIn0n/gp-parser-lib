from typing import Callable

from parsers.lr.lr0 import LR0Parser
from parsers.lr.slr import SLRParser
from parsers.lr.lr_types import LRAction, LRActionEnum


class LREngine:
    def __init__(self, p: LR0Parser | SLRParser) -> None:
        self.indexed_rules = p.indexed_rules
        self.table = p.parsing_table
        self.start_state = p.get_starting_state_idx()
        self.states: list[int] = [self.start_state]

    def curr_state(self) -> int:
        return self.states[-1]

    def get_action(self, sym: str) -> LRAction:
        # Given the valid grammar for LR parser, actions should have inside
        # only one action. We check it, if that's true we unpack the value
        # TODO: that's suboptimal, also creating the collection from set
        # seems to me like wild idea in terms of memory
        actions = self.table[self.curr_state()][sym]
        assert len(actions) == 1, f"{actions=}, {self.curr_state()=}, {sym=}"
        return next(iter(actions))

    def parse(
        self, input_: list[str], iteration_callback: Callable | None = None
    ) -> dict:
        self.states = [self.start_state]
        stack: list[str | dict] = []
        # states is stack of the states. The first element on it is starting state.
        # We will pop states accordingly to popping symbols during reduce.

        while True:
            sym = input_[0]
            action = self.get_action(sym)
            if iteration_callback is not None:
                iteration_callback(stack, self.states, sym, action)

            match action:
                case LRAction(type_=LRActionEnum.ACCEPT):
                    assert len(stack) == 1 and isinstance(stack[0], dict)
                    return stack[0]
                case LRAction(type_=LRActionEnum.REDUCE, to=n):
                    rule = self.indexed_rules[n]
                    reduced = {}
                    for el in reversed(rule.rhs):
                        reduced[el] = stack.pop()
                        self.states.pop()
                    stack.append({rule.lhs: reduced})

                    action = self.get_action(rule.lhs)
                    assert action.type_ == LRActionEnum.GOTO
                    self.states.append(action.to)
                case LRAction(type_=LRActionEnum.SHIFT, to=n):
                    stack.append(sym)
                    input_.pop(0)
                    self.states.append(n)
