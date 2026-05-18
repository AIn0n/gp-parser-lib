from parsers.lr.lr0 import LR0Parser
from parsers.lr.lr_types import LRItem, LRState
from parsers.example_grammars import GRAMMAR_3_20, GRAMMAR_3_23


def test_closure_given_grammar_3_20_should_return_valid_set_for_first_rule() -> None:
    # figure 3.21, page 62
    expected_items = [
        LRItem.from_rule_str("S' -> S $", dot_pos=0),
        LRItem.from_rule_str("S -> ( L )", dot_pos=0),
        LRItem.from_rule_str("S -> x", dot_pos=0),
    ]
    p = LR0Parser(*GRAMMAR_3_20)

    given_items = p.closure(frozenset([LRItem.from_ruletype(p.get_start_rule())]))

    assert len(expected_items) == len(given_items)

    for item in expected_items:
        assert item in given_items


def test_goto_given_grammar_3_20_returns_valid_set() -> None:
    # same as above, figure 3.21, page 62
    expected_items = [
        LRItem.from_rule_str("S -> ( L )", dot_pos=1),
        LRItem.from_rule_str("L -> S", dot_pos=0),
        LRItem.from_rule_str("L -> L , S", dot_pos=0),
        LRItem.from_rule_str("S -> ( L )", dot_pos=0),
        LRItem.from_rule_str("S -> x", dot_pos=0),
    ]
    p = LR0Parser(*GRAMMAR_3_20)

    first_closure = p.closure(frozenset([LRItem.from_ruletype(p.get_start_rule())]))
    given_items = p.goto(first_closure, "(")

    for item in expected_items:
        assert item in given_items

    assert len(expected_items) == len(given_items)


def test_lr0_for_grammar_3_20_returns_9_unique_states() -> None:
    p = LR0Parser(*GRAMMAR_3_20)

    assert len(p.states) == 9


def test_lr0_for_grammar_3_20_returns_12_state_edges() -> None:
    p = LR0Parser(*GRAMMAR_3_20)

    assert len(p.edges) == 12


def test_lr0_for_grammar_3_20_returns_valid_start_state() -> None:
    p = LR0Parser(*GRAMMAR_3_20)

    # figure 3.21, page 62
    expected_start_state: LRState = frozenset(
        [
            LRItem.from_rule_str("S' -> S $", dot_pos=0),
            LRItem.from_rule_str("S -> ( L )", dot_pos=0),
            LRItem.from_rule_str("S -> x", dot_pos=0),
        ]
    )
    assert expected_start_state in p.states.values()

    given_idx = -1
    for idx, state in p.states.items():
        if state == expected_start_state:
            given_idx = idx

    assert p.get_starting_state_idx() == given_idx


def test_lr0_for_grammar_3_23_returns_duplicate_entry_in_parsing_table() -> None:
    # from figure 3.24, page 63 parsing table
    # for plus symbol, we have one double entry, two with one action and three empty
    p = LR0Parser(*GRAMMAR_3_23)

    table = p.parsing_table

    states_idxs = set(p.states.keys())

    assert len(states_idxs) == 6

    expected_double_entry_sym = "+"
    all_sym_entries_len = [
        len(table[idx][expected_double_entry_sym]) for idx in states_idxs
    ]

    assert sorted(all_sym_entries_len) == [0, 0, 0, 1, 1, 2]
