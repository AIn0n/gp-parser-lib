from dataclasses import dataclass
from typing import NamedTuple


class RuleType(NamedTuple):
    lhs: str
    rhs: tuple[str, ...]

    @staticmethod
    def from_str(s: str, eol: str, is_start: bool = False) -> RuleType:
        lhs, rhs = s.split("->")
        rhs = rhs.strip().split()
        if is_start:
            rhs.append(eol)
        return RuleType(lhs=lhs.strip(), rhs=tuple(rhs))

    def __str__(self) -> str:
        return f"{self.lhs} -> " + " ".join(self.rhs)


@dataclass(frozen=True, slots=True)
class RuleSet:
    start_rule_idx: int
    rules: dict[int, RuleType]
    # end symbol for any parser, representing end of file
    eol: str
