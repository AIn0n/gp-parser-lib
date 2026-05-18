from parsers.lr.lr_types import are_states_equal_wo_lookahead, LRItem
from parsers.lr.lr1 import LR1Parser

from parsers.example_grammars import GRAMMAR_3_26


def test_function_to_compare_states_given_two_equal_states_return_true() -> None:
    first = frozenset(
        [
            LRItem.from_rule_str("S' -> S $", dot_pos=0),
            LRItem.from_rule_str("S -> P G", dot_pos=1),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str("S -> P G", dot_pos=1),
            LRItem.from_rule_str("S' -> S $", dot_pos=0),
        ]
    )
    assert are_states_equal_wo_lookahead(first, second)


def test_function_to_compare_states_given_two_same_states_with_different_dot_return_false() -> (
    None
):
    first = frozenset(
        [
            LRItem.from_rule_str("S' -> S $", dot_pos=0),
            LRItem.from_rule_str("S -> P G", dot_pos=1),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str("S -> P G", dot_pos=1),
            LRItem.from_rule_str("S' -> S $", dot_pos=1),
        ]
    )
    assert not are_states_equal_wo_lookahead(first, second)


def test_given_two_same_states_with_other_lookahead_compare_return_true() -> None:
    first = frozenset(
        [
            LRItem.from_rule_str("S' -> S $", dot_pos=0, lookahead="?"),
            LRItem.from_rule_str("S -> P G", dot_pos=1),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str("S' -> S $", dot_pos=0, lookahead="#"),
            LRItem.from_rule_str("S -> P G", dot_pos=1),
        ]
    )
    assert are_states_equal_wo_lookahead(first, second)


def test_given_grammar_3_26_when_converted_to_lalr_return_valid_num_of_states() -> None:
    parser = LR1Parser(*GRAMMAR_3_26)
    parser.parsing_table

    expected_count_LR1 = 14
    expected_count_LALR1 = 10

    assert len(parser.states) == expected_count_LR1

    lalr1 = parser.to_lalr()

    assert len(lalr1.states) == expected_count_LALR1


def test_grammar_3_26_converted_to_lalr_returns_no_conflict() -> None:
    parser = LR1Parser(*GRAMMAR_3_26)
    parser.to_lalr()

    counts: list[bool] = []
    for row in parser.parsing_table.values():
        counts.extend(map(lambda x: len(x) <= 1, row.values()))

    assert all(counts)


def test_grammar_3_26_converted_to_lalr_returns_parsing_table_with_10_states() -> None:
    parser = LR1Parser(*GRAMMAR_3_26)

    assert len(parser.parsing_table.keys()) == 14

    parser.to_lalr()

    assert len(parser.parsing_table.keys()) == 10
