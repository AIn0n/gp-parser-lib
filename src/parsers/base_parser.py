from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from collections import defaultdict
from typing import MutableMapping

from parsers.parser_types import RuleSet


@dataclass(frozen=True, slots=True)
class ParserPrintStyler:
    epsilon: str = "ε"
    hor_line: str = "─"
    pipe_wne: str = "┬"
    pipe_nes: str = "├"
    pipe_ne: str = "└"


class BaseParser:
    """
    Class with the logic for adding new rules, printing the rules, handling the
    printing styling, etc.
    """

    def __init__(
        self, ruleset: RuleSet, styling: ParserPrintStyler | None = None
    ) -> None:
        if styling is None:
            styling = ParserPrintStyler()
        self.ruleset: RuleSet = ruleset
        self.styling = styling

        self.nullables: set[str] = set()
        self.first: MutableMapping[str, set[str]] = defaultdict(set)
        self.follow: MutableMapping[str, set[str]] = defaultdict(set)
        self.compute_first_follow_nullable()

    def first_rhs(self, y: tuple[str, ...]) -> set[str]:
        if len(y) == 0:
            return set()
        if y[0] in self.nullables:
            return self.first[y[0]].union(self.first_rhs(y[1:]))
        return self.first[y[0]]

    def _is_sequence_nullable(self, seq: tuple[str, ...]) -> bool:
        if len(seq) == 0:
            return True
        return all(map(lambda x: x in self.nullables, seq))

    def _count_first_follow_nullables(self) -> int:
        return sum(
            map(len, [self.nullables, *self.follow.values(), *self.first.values()])
        )

    def compute_first_follow_nullable(self, one_iteration: bool = False) -> None:
        self.nullables = set()
        self.follow = defaultdict(set)
        self.first = defaultdict(set)

        for terminal in self.terminals:
            self.first[terminal] = set([terminal])

        while True:
            changed = self._count_first_follow_nullables()
            for x, y in self.ruleset.rules.values():
                k = len(y)
                if self._is_sequence_nullable(y):
                    self.nullables.add(x)
                for i in range(k):
                    if self._is_sequence_nullable(y[0:i]):
                        self.first[x] = self.first[x].union(self.first[y[i]])
                    if self._is_sequence_nullable(y[i + 1 :]):
                        self.follow[y[i]] = self.follow[y[i]].union(self.follow[x])
                    for j in range(i + 1, k):
                        if self._is_sequence_nullable(y[i + 1 : j]):
                            self.follow[y[i]] = self.follow[y[i]].union(
                                self.first[y[j]]
                            )
            if one_iteration or (changed == self._count_first_follow_nullables()):
                break

    @cached_property
    def non_terminals(self) -> set[str]:
        return set([el.lhs for el in self.ruleset.rules.values()])

    @cached_property
    def terminals(self) -> set[str]:
        all_rhs_symbols = set(
            chain.from_iterable([el.rhs for el in self.ruleset.rules.values()])
        )
        # everything from the rules, except right hands side
        return all_rhs_symbols - self.non_terminals

    def _rhs2str(self, rhs: tuple[str, ...]) -> str:
        return " ".join(rhs) if len(rhs) else self.styling.epsilon

    def __str__(self) -> str:
        rules_dict = defaultdict(list)
        for lhs, rhs in self.ruleset.rules.values():
            rules_dict[lhs].append(rhs)

        left_pad = max(map(len, rules_dict.keys())) + 1
        offset_sym = self.styling.hor_line
        res = ""
        offset = left_pad * " "
        for k, v in rules_dict.items():
            prefix = f"{k:{offset_sym}<{left_pad}}"
            if len(v) == 1:
                res += f"{prefix}{offset_sym * 2} {self._rhs2str(v[0])}\n"
                continue

            first, *rest, last = v
            res += (
                f"{prefix}{self.styling.pipe_wne}{offset_sym} {self._rhs2str(first)}\n"
            )

            for rule in rest:
                res += f"{offset}{self.styling.pipe_nes}{offset_sym} {self._rhs2str(rule)}\n"

            res += f"{offset}{self.styling.pipe_ne}{offset_sym} {self._rhs2str(last)}\n"

        return res
