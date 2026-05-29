from itertools import chain

from parsers.lr.lr_types import LRParsingTable, LRAction


def get_conflicts(table: LRParsingTable) -> list[tuple[int, str, set[LRAction]]]:
    result = []
    for state, col in table.items():
        for sym, actions in col.items():
            if len(actions) > 1:
                result.append(tuple([state, sym, actions]))

    return result


def pretify_stack(stack, intend: int = 0) -> str:
    # TODO: not tested yet, found bigger problem
    res = ""
    if isinstance(stack, dict):
        res += pretify_stack(list(stack.keys())[0], intend=intend)
        for el in stack.values():
            res += pretify_stack(el, intend=intend + 2)
    elif isinstance(stack, list):
        assert len(stack) == 1
        for el in chain.from_iterable(stack):
            pretify_stack(el, intend=intend + 2)
    elif isinstance(stack, str):
        res += " " * intend + stack + "\n"
    return res
