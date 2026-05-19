from collections import defaultdict
from typing import Collection

from parsers.base_parser import BaseParser, ParserPrintStyler
from parsers.parser_types import RuleSet

from tabulate import tabulate


class LL1Parser(BaseParser):
    def __init__(
        self, ruleset: RuleSet, styling: ParserPrintStyler | None = None
    ) -> None:
        super().__init__(ruleset, styling=styling)

    def nullable_rhs(self, y: Collection[str]) -> bool:
        return (not len(y)) or all(map(lambda x: x in self.nullables, y))

    @property
    def parsing_table(self):
        table = defaultdict(lambda: defaultdict(set))

        for x, y in self.ruleset.rules.values():
            for t in self.first_rhs(y):
                table[x][t].add((x, y))
            if not self.nullable_rhs(y):
                continue
            for t in self.follow[x]:
                table[x][t].add((x, y))
        return table

    def _table_cell2str(self, x: str, t: str) -> str:
        if t not in self.parsing_table[x]:
            return ""
        line = [f"{x} -> {self._rhs2str(y)}" for _, y in self.parsing_table[x][t]]
        return "\n".join(line)

    def to_tabulate(self, fmt: str = "simple_grid") -> str:
        rows = sorted(self.non_terminals)
        cols = sorted(list(self.terminals))

        list_table = []
        for row in rows:
            list_table.append([row] + [self._table_cell2str(row, col) for col in cols])

        return tabulate(list_table, headers=[""] + cols, tablefmt=fmt)
