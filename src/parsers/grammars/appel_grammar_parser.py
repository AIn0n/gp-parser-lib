"""
Used to parse the grammars defined in syntax similar to one from MCI book
eg.
A -> a b c
A ->

"""

from parsers.parser_types import RuleSet, RuleType


def appel_to_ruleset(
    grm: list[str], start_rule_idx: int = 0, eol: str = "$end"
) -> RuleSet:
    rules: dict[int, RuleType] = dict()
    for idx, el in enumerate(grm):
        rules[idx] = RuleType.from_str(el, eol, idx == start_rule_idx)

    return RuleSet(rules=rules, start_rule_idx=start_rule_idx, eol=eol)
