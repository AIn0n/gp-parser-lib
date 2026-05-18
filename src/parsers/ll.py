from collections import defaultdict

from parsers.base_parser import BaseParser, ParserPrintStyler
from parsers.example_grammars import GRAMMAR_3_12

from tabulate import tabulate


class LL1Parser(BaseParser):
    def __init__(self, *rules: str, styling: ParserPrintStyler | None = None) -> None:
        super().__init__(*rules, styling=styling)
        self.compute_first_follow_nullable()

    def nullable_rhs(self, y: list[str]) -> bool:
        return (not len(y)) or all(map(lambda x: x in self.nullables, y))

    @property
    def parsing_table(self):
        table = defaultdict(lambda: defaultdict(set))

        for x, y in self.rules:
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


if __name__ == "__main__":
    # Example from grammar 3.12
    p = LL1Parser(*GRAMMAR_3_12)
    non_terminals = p.non_terminals
    print(f"{non_terminals=}")
    print(f"{p.nullables=}")
    interesting_first = {k: v for k, v in p.first.items() if k in non_terminals}
    print(f"first = {interesting_first}")
    interesting_follows = {k: v for k, v in p.follow.items() if k in non_terminals}
    print(f"{interesting_follows=}")
    p.parsing_table
    print(f"{p.to_tabulate()}")
