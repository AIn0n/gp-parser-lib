from parsers.lr.lr1 import LR1Parser
from parsers.example_grammars import GRAMMAR_3_26


def test_given_grammar_3_26_lr1_parser_returns_no_conflict() -> None:
    p = LR1Parser(*GRAMMAR_3_26)

    counts: list[bool] = []
    for row in p.parsing_table.values():
        counts.extend(map(lambda x: len(x) <= 1, row.values()))

    # page 66 of the book - we can clearly see there is 14 states
    assert len(p.states) == 14

    assert all(counts)
