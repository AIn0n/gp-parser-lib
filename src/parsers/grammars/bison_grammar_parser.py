"""
Module to parse parser's rules defined in similar way to bison. My goal here is
not 100% compatibility, rather, I need it to be compatible enough to copy-paste
most of the code written for bison with minor tweaks
"""

from parsers.parser_types import RuleSet
import re

from parsers.parser_types import RuleType


def _find_start_symbol(dec_raw: str) -> str | None:
    kw_match = re.search(r"%start", dec_raw)
    if kw_match is not None:
        kw_end = kw_match.end()
        kw_line_end_match = re.search(r"\n", dec_raw[kw_end:])

        assert kw_line_end_match is not None

        kw_line_end = kw_line_end_match.start()
        return dec_raw[kw_end : kw_end + kw_line_end].strip()

    return None


def _remove_sem_actions(grm_raw: str) -> str:
    comment_re = re.compile(r"{.*}")
    return comment_re.sub("", grm_raw)


def bison_to_ruleset(grm: str, eol: str = "$end") -> RuleSet:
    splitted_text = grm.split("%%")

    assert len(splitted_text) >= 2, "Grammar with minimum two sections supported"

    dec_raw, grm_raw, *_ = splitted_text

    # look for the start rule in the first part with declarations
    start_sym = _find_start_symbol(dec_raw)
    assert start_sym is not None

    unparsed_rules = _remove_sem_actions(grm_raw).split(";")
    rules: dict[int, RuleType] = {0: RuleType("$accept", tuple([start_sym, "$end"]))}
    idx = 1
    for unprs_rule in unparsed_rules:
        if len(unprs_rule) == 0 or unprs_rule.isspace():
            continue
        lhs, rhs_col = unprs_rule.split(":")
        lhs = lhs.strip()
        if start_sym is None:
            start_sym = lhs
        for el in rhs_col.split("|"):
            rhs = el.strip().split()
            rules[idx] = RuleType(lhs=lhs, rhs=tuple(rhs))
            idx += 1

    assert len(rules) >= 1, "no rules found!"

    return RuleSet(start_rule_idx=0, rules=rules, eol=eol)


if __name__ == "__main__":
    with open("examples_yacc/simple_grammar.y", mode="r") as f:
        ruleset = bison_to_ruleset(f.read())
        for rule in ruleset.rules.values():
            print(rule)
