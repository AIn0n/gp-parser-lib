from parsers.lr.lr_types import LRParsingTable, LRAction


def get_conflicts(table: LRParsingTable) -> list[tuple[int, str, set[LRAction]]]:
    result = []
    for state, col in table.items():
        for sym, actions in col.items():
            if len(actions) > 1:
                result.append(tuple([state, sym, actions]))

    return result
