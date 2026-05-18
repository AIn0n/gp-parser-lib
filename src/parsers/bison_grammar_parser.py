"""
Module to parse parser's rules defined in similar way to bison. My goal here is
not 100% compatibility, rather, I need it to be compatible enough to copy-paste
most of the code written for bison with minor tweaks
"""

from dataclasses import dataclass
from pathlib import Path
import re

from parsers.base_parser import RuleType


@dataclass(frozen=True, slots=True)
class RuleSet:
    start_rule_idx: int
    rules: dict[int, RuleType]


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


def bison_load_as_rules(grm: Path) -> RuleSet:
    with open(grm, mode="r", encoding="utf-8") as f:
        splitted_text: list[str] = f.read().split("%%")

    assert len(splitted_text) >= 2, "Grammar with minimum two sections supported"

    dec_raw, grm_raw, *_ = splitted_text

    unparsed_rules = _remove_sem_actions(grm_raw).split(";")
    rules: dict[int, RuleType] = dict()
    for idx, unprs_rule in enumerate(unparsed_rules):
        if len(unprs_rule) == 0 or unprs_rule.isspace():
            continue
        lhs, rhs = unprs_rule.split(":")
        rules[idx] = RuleType(
            lhs=lhs.strip(), rhs=tuple([el.strip() for el in rhs.split("|")])
        )

    assert len(rules) >= 1, "no rules found!"

    # look for the start rule in the first part with declarations
    if start_sym := _find_start_symbol(dec_raw):
        start_sym_idxs = [k for k, v in rules.items() if v.lhs == start_sym]
        assert len(start_sym_idxs) == 1, "Only one grammar start rule supported"
        start_sym_idx = start_sym_idxs[0]
    else:
        start_sym_idx = 0

    return RuleSet(start_rule_idx=start_sym_idx, rules=rules)


if __name__ == "__main__":
    p = Path("/Users/szymongorka/git/gp-parser-lib/examples_yacc/mci.y")
    print(bison_load_as_rules(p))
    p = Path("/Users/szymongorka/git/gp-parser-lib/examples_yacc/code.y")
    print(bison_load_as_rules(p))
    p = Path("/Users/szymongorka/git/gp-parser-lib/examples_yacc/simple_grammar.y")
    print(bison_load_as_rules(p))
