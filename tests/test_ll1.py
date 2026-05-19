from parsers.ll import LL1Parser
from parsers.grammars.appel_grammar_parser import appel_to_ruleset
from parsers.grammars.example_grammars import GRAMMAR_3_12, GRAMMAR_3_15


def test_example_grammar_3_12() -> None:
    p = LL1Parser(appel_to_ruleset(GRAMMAR_3_12))
    non_terminals = p.non_terminals
    assert non_terminals == set(["X", "Y", "Z"])
    assert p.nullables == set(["X", "Y"])

    # Literally table from page n 50
    assert p.first["X"] == set(["a", "c"])
    assert p.first["Y"] == set(["c"])
    assert p.first["Z"] == set(["a", "c", "d"])

    assert p.follow["X"] == set(["a", "c", "d"])
    assert p.follow["Y"] == set(["a", "c", "d"])
    assert len(p.follow["Z"]) == 0


def test_ll_parser_on_grammar_3_15() -> None:
    p = LL1Parser(appel_to_ruleset(GRAMMAR_3_15))
    # Table 3.16

    ## nullables
    assert {"E'", "T'"} == p.nullables

    ## first
    assert {"(", "id", "num"} == p.first["S"]
    assert {"(", "id", "num"} == p.first["E"]
    assert {"(", "id", "num"} == p.first["T"]
    assert {"(", "id", "num"} == p.first["F"]

    assert {"/", "*"} == p.first["T'"]
    assert {"-", "+"} == p.first["E'"]

    ## follows
    assert len(p.follow["S"]) == 0

    assert {")", "$"} == p.follow["E"]
    assert {")", "$"} == p.follow["E'"]

    assert {")", "+", "-", "$"} == p.follow["T"]
    assert {")", "+", "-", "$"} == p.follow["T'"]

    assert {")", "+", "-", "*", "/", "$"} == p.follow["F"]
