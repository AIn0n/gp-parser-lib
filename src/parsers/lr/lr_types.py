from enum import StrEnum
from dataclasses import dataclass
from typing import Mapping, Sequence
from collections import defaultdict

from parsers.base_parser import RuleType


class LRActionEnum(StrEnum):
    REDUCE = "r"
    GOTO = "g"
    SHIFT = "s"
    ACCEPT = "a"


@dataclass(slots=True, frozen=True)
class LRAction:
    type_: LRActionEnum
    to: int

    def __str__(self) -> str:
        if self.type_ == LRActionEnum.ACCEPT:
            return "a"
        return f"{self.type_.value}{self.to}"

    @staticmethod
    def reduce(n: int) -> LRAction:
        return LRAction(LRActionEnum.REDUCE, n)

    @staticmethod
    def shift(n: int) -> LRAction:
        return LRAction(LRActionEnum.SHIFT, n)

    @staticmethod
    def accept() -> LRAction:
        return LRAction(LRActionEnum.ACCEPT, -1)

    @staticmethod
    def goto(n: int) -> LRAction:
        return LRAction(LRActionEnum.GOTO, n)


@dataclass(slots=True, frozen=True)
class LRItem:
    rule: RuleType
    # Assume 0 dot_pos is dot on the beginning of rhs
    # R -> . A B C
    # dot_pos = 0
    # R -> A . B C
    # dot_pos = 1
    # and so on...
    dot_pos: int
    lookahead: str | None = None

    def peek_after_dot(self) -> str | None:
        if self.dot_pos >= len(self.rule.rhs):
            return None
        return self.rule.rhs[self.dot_pos]

    def advance_dot(self) -> LRItem:
        return LRItem(
            rule=self.rule, dot_pos=self.dot_pos + 1, lookahead=self.lookahead
        )

    def is_dot_at_end(self) -> bool:
        return self.dot_pos == len(self.rule.rhs)

    def to_rule(self) -> RuleType:
        return self.rule

    def _to_str_with_dot(self) -> str:
        pre_dot = self.rule.rhs[: self.dot_pos]
        post_dot = self.rule.rhs[self.dot_pos :]
        return f"{self.rule.lhs} -> " + " ".join([*pre_dot, ".", *post_dot])

    def __str__(self) -> str:
        return self.to_str_with_lookaheads([self.lookahead])

    def to_str_with_lookaheads(
        self, lookaheads: None | Sequence[None | str] = None
    ) -> str:
        res = self._to_str_with_dot()
        if (
            lookaheads is not None
            and len(fla := [el for el in lookaheads if el is not None]) > 0
        ):
            lh_str = " ".join(sorted(fla))
            res += f" ({lh_str})"
        return res

    @staticmethod
    def from_ruletype(rule: RuleType) -> LRItem:
        """
        Turn rule into LR item, by default setting the dot at the first position
        on left-hand side.
        """
        return LRItem(rule=rule, dot_pos=0, lookahead=None)

    @staticmethod
    def from_rule_str(rule: str, dot_pos: int = 0, lookahead: str | None = None):
        return LRItem(
            rule=RuleType.from_str(rule), dot_pos=dot_pos, lookahead=lookahead
        )


LRState = frozenset[LRItem]
LRParsingTable = dict[int, dict[str, set[LRAction]]]


@dataclass(slots=True, frozen=True)
class IndexedLREdge:
    """
    Stores connections between states: from and to states, in form of indexes, and
    symbol on connection.
    """

    from_: int
    to: int
    symbol: str


@dataclass(slots=True, frozen=True)
class LREdge:
    """
    Stores states from and to indexes and symbol on the given edge. Also can store
    whole LRState inside, but it seems to be bad idea during parsing table building.
    """

    from_: LRState
    to: LRState
    symbol: str

    def convert_to_indexed(self, lookup: Mapping[LRState, int]) -> IndexedLREdge:
        """
        Convert states in edge from whole objects to indexes.
        """
        return IndexedLREdge(
            from_=lookup[self.from_], to=lookup[self.to], symbol=self.symbol
        )


def lr_state_to_str(
    state: LRState, prefix: str | None = None, linebreak: str = "\n"
) -> str:
    if prefix is None:
        prefix = ""
    res = ""

    lookahead_map: dict[tuple[RuleType, int], list[str]] = defaultdict(list)
    item_map: dict[tuple[RuleType, int], LRItem] = {}

    for item in state:
        k = (item.rule, item.dot_pos)
        item_map[k] = item
        if item.lookahead is not None:
            lookahead_map[k].append(item.lookahead)

    for k in item_map.keys():
        res += prefix + item_map[k].to_str_with_lookaheads(lookahead_map[k]) + linebreak

    return res


def are_states_equal_wo_lookahead(first: LRState, second: LRState) -> bool:
    first_set = frozenset((el.rule, el.dot_pos) for el in first)
    second_set = frozenset((el.rule, el.dot_pos) for el in second)
    return first_set == second_set
