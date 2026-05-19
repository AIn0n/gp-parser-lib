from parsers.lr.slr import SLRParser
from parsers.lr.lr_types import LRActionEnum
from parsers.grammars.example_grammars import GRAMMAR_3_23
from parsers.grammars.appel_grammar_parser import appel_to_ruleset


def test_for_grammar_3_23_SLR_parser_returns_non_conflicted_table() -> None:
    p = SLRParser(appel_to_ruleset(GRAMMAR_3_23))

    t = p.parsing_table
    for state in p.states.keys():
        for sym in p.symbols:
            assert len(t[state][sym]) <= 1


def test_for_grammar_3_23_SLR_parser_return_one_or_more_reduce_actions() -> None:
    p = SLRParser(appel_to_ruleset(GRAMMAR_3_23))

    t = p.parsing_table
    count = 0
    for state in p.states.keys():
        for sym in p.symbols:
            actions = t[state][sym]
            if len(actions) and actions.pop().type_ == LRActionEnum.REDUCE:
                count += 1

    assert count >= 1
