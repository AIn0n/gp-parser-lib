from parsers.lr.lr_types import are_states_equal_wo_lookahead, LRItem
from parsers.lr.lr1 import LR1Parser

from parsers.grammars.example_grammars import GRAMMAR_3_26
from parsers.grammars.appel_grammar_parser import appel_to_ruleset


def test_function_to_compare_states_given_two_equal_states_return_true() -> None:
    first = frozenset(
        [
            LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", is_start=True),
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
            LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", is_start=True),
        ]
    )
    assert are_states_equal_wo_lookahead(first, second)


def test_function_to_compare_states_given_two_same_states_with_different_dot_return_false() -> (
    None
):
    first = frozenset(
        [
            LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", is_start=True),
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
            LRItem.from_rule_str("S' -> S", dot_pos=1, eol="$end", is_start=True),
        ]
    )
    assert not are_states_equal_wo_lookahead(first, second)


def test_given_two_same_states_with_other_lookahead_compare_return_true() -> None:
    first = frozenset(
        [
            LRItem.from_rule_str(
                "S' -> S", dot_pos=0, eol="$end", is_start=True, lookahead="?"
            ),
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
        ]
    )
    second = frozenset(
        [
            LRItem.from_rule_str(
                "S' -> S", dot_pos=0, eol="$end", is_start=True, lookahead="#"
            ),
            LRItem.from_rule_str("S -> P G", dot_pos=1, eol="$end"),
        ]
    )
    assert are_states_equal_wo_lookahead(first, second)


def test_given_grammar_3_26_when_converted_to_lalr_return_valid_num_of_states() -> None:
    parser = LR1Parser(appel_to_ruleset(GRAMMAR_3_26))
    parser.parsing_table

    expected_count_LR1 = 14
    expected_count_LALR1 = 10

    assert len(parser.states) == expected_count_LR1

    lalr1 = parser.to_lalr()

    assert len(lalr1.states) == expected_count_LALR1


def test_grammar_3_26_converted_to_lalr_returns_no_conflict() -> None:
    parser = LR1Parser(appel_to_ruleset(GRAMMAR_3_26))
    parser.to_lalr()

    counts: list[bool] = []
    for row in parser.parsing_table.values():
        counts.extend(map(lambda x: len(x) <= 1, row.values()))

    assert all(counts)


def test_grammar_3_26_converted_to_lalr_returns_parsing_table_with_10_states() -> None:
    parser = LR1Parser(appel_to_ruleset(GRAMMAR_3_26))

    assert len(parser.parsing_table.keys()) == 14

    parser.to_lalr()

    assert len(parser.parsing_table.keys()) == 10


def test_given_two_states_with_the_same_items_but_different_lookaheads_lalr1_merges_lookaheads():
    dummy_grammar = [
        "S' -> S",
    ]
    parser = LR1Parser(appel_to_ruleset(dummy_grammar))
    parser.states = {
        0: frozenset(
            [
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end"),
            ]
        ),
        1: frozenset(
            [
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end"),
                LRItem.from_rule_str(
                    "S' -> S", dot_pos=0, eol="$end", lookahead="ANOTHER"
                ),
                LRItem.from_rule_str(
                    "S' -> S", dot_pos=0, eol="$end", lookahead="SYMBOL"
                ),
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", lookahead="AT"),
                LRItem.from_rule_str(
                    "S' -> S", dot_pos=0, eol="$end", lookahead="LOOKAHEAD"
                ),
            ]
        ),
    }
    parser = parser.to_lalr()
    assert len(parser.states) == 1
    assert len(parser.states[0]) == 5


def test_given_two_states_one_with_more_lookaheads_but_the_same_rules_comparison_returns_true():
    # figure 3.27
    # based on what is described at page 65, these two states should be the same
    more_lookaheads = frozenset(
        [
            LRItem.from_rule_str("V -> * E", eol="$end", dot_pos=1, lookahead="="),
            LRItem.from_rule_str("T -> * E", eol="$end", dot_pos=0, lookahead="="),
            LRItem.from_rule_str("E -> V", eol="$end", dot_pos=0, lookahead="="),
            LRItem.from_rule_str("V -> X", eol="$end", dot_pos=0, lookahead="="),
            LRItem.from_rule_str("V -> * E", eol="$end", dot_pos=1, lookahead="&"),
            LRItem.from_rule_str("T -> * E", eol="$end", dot_pos=0, lookahead="&"),
            LRItem.from_rule_str("E -> V", eol="$end", dot_pos=0, lookahead="&"),
            LRItem.from_rule_str("V -> X", eol="$end", dot_pos=0, lookahead="&"),
        ]
    )
    less_lookaheads = frozenset(
        [
            LRItem.from_rule_str("V -> * E", eol="$end", dot_pos=1, lookahead="&"),
            LRItem.from_rule_str("T -> * E", eol="$end", dot_pos=0, lookahead="&"),
            LRItem.from_rule_str("E -> V", eol="$end", dot_pos=0, lookahead="&"),
            LRItem.from_rule_str("V -> X", eol="$end", dot_pos=0, lookahead="&"),
        ]
    )
    assert are_states_equal_wo_lookahead(more_lookaheads, less_lookaheads)
