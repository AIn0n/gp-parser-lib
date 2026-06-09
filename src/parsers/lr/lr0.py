from tabulate import tabulate

from typing import Optional
from functools import cached_property

from parsers.base_parser import ParserPrintStyler, BaseParser
from parsers.parser_types import RuleSet, RuleType
from parsers.lr.lr_types import (
    LRAction,
    LRActionEnum,
    LREdge,
    LRItem,
    LRState,
    IndexedLREdge,
    LRParsingTable,
    lr_state_to_str,
)


class LR0Parser(BaseParser):
    def __init__(self, ruleset: RuleSet, styling: Optional[ParserPrintStyler] = None):
        super().__init__(ruleset, styling=styling)
        self.states: dict[int, LRState] = dict()
        self.edges: set[IndexedLREdge] = set()
        self.compute_states_and_edges()
        self.parsing_table = self._compute_parsing_table()

    def get_start_rule(self) -> RuleType:
        return self.ruleset.rules[self.ruleset.start_rule_idx]

    def closure(self, i: LRState) -> LRState:
        while True:
            new_i: set[LRItem] = set(i)
            for el in i:
                # closure works only for in cases where next to dot (at X position)
                # is non terminal element. Thanks to this statement we will not
                # unnecessarily scan thru rules
                x: Optional[str] = el.peek_after_dot()
                if x is None or x in self.terminals:
                    continue
                for rule in self.ruleset.rules.values():
                    # check lhs
                    if rule.lhs != x:
                        continue
                    new_i.add(LRItem.from_ruletype(rule))
            # break when I does not change
            if len(new_i) == len(i):
                break
            i = frozenset(new_i)
        return frozenset(i)

    def goto(self, i: LRState, x: str) -> LRState:
        # from page 60-61
        j = frozenset(el.advance_dot() for el in i if el.peek_after_dot() == x)
        return self.closure(j)

    def get_starting_state_idx(self) -> int:
        start_item = LRItem.from_ruletype(self.get_start_rule())
        for idx, state in self.states.items():
            if start_item in state:
                return idx

        assert False

    def get_start_states(self) -> set[LRState]:
        """
        Built state set to start computing states and edges.

        first state is just starting rule (one with terminal symbol at end)
        converted into LR item - rule with dot representing current position
        at given rule
        """
        start_rule = self.get_start_rule()
        return set([self.closure(frozenset([LRItem.from_ruletype(start_rule)]))])

    def compute_states_and_edges(self) -> None:
        # state collection
        t: set[LRState] = self.get_start_states()
        # edges collection
        e: set[LREdge] = set()
        while True:
            new_e = set()
            new_t: set[LRState] = set()
            for i in t:
                for item in i:
                    x = item.peek_after_dot()
                    # However, for the symbol $ we do not compute Goto(I, $); instead we will
                    # make an accept action
                    if x is None or x == self.ruleset.eol:
                        continue
                    j = self.goto(i, x)
                    new_t.add(j)
                    new_e.add(LREdge(from_=i, to=j, symbol=x))
            old_t_len = len(t)
            old_e_len = len(e)
            t.update(new_t)
            e.update(new_e)

            if old_e_len == len(e) and old_t_len == len(t):
                break

        self.states = {idx: state for idx, state in enumerate(t)}
        lookup = {v: k for k, v in self.states.items()}
        self.edges = set(map(lambda x: x.convert_to_indexed(lookup), e))

    @cached_property
    def symbols(self) -> set[str]:
        return self.terminals | self.non_terminals

    def _init_parsing_table(self) -> LRParsingTable:
        return {i: {sym: set() for sym in self.symbols} for i in self.states.keys()}

    def _add_edges_to_parsing_table(self, t: LRParsingTable) -> None:
        """
        Add edges to the parsing table.

        Process looks literally the same in every type of parser, this function
        is used to DRY up the code.
        """
        for edge in self.edges:
            action = LRAction.shift if edge.symbol in self.terminals else LRAction.goto
            t[edge.from_][edge.symbol].add(action(edge.to))

    def _compute_parsing_table(self) -> LRParsingTable:
        """
        Returns parsing table for given grammar. Table is row-first, and the
        first dict is representing the states number, dict inside it stores
        symbols and actions mapping.
        """

        rule_lookup = {r: i for i, r in self.ruleset.rules.items()}
        t: LRParsingTable = self._init_parsing_table()
        for idx, i in self.states.items():
            for item in i:
                if item.is_dot_at_end():
                    rule_idx = rule_lookup[item.to_rule()]
                    for non_term in self.terminals:
                        t[idx][non_term].add(LRAction.reduce(rule_idx))
                if item.peek_after_dot() == self.ruleset.eol:
                    t[idx][self.ruleset.eol].add(LRAction.accept())

        self._add_edges_to_parsing_table(t)
        return t

    def _table_cell2str(self, c: set[LRAction]) -> str:
        return ", ".join(map(str, c))

    def to_tabulate(self) -> str:
        list_table = []
        # columns in the same order like in book - first terminals
        headers = [*self.terminals, *self.non_terminals]
        for idx, row in self.parsing_table.items():
            r: list[int | str] = [idx]
            for col in headers:
                r.append(self._table_cell2str(row[col]))
            list_table.append(r)

        return tabulate(list_table, headers=[""] + headers, tablefmt="simple_grid")

    def print_rules_and_states(self) -> None:
        print("---=== Rules ===---")
        for idx, rule in self.ruleset.rules.items():
            print(f"{idx:04} {rule}")

        print("\n---=== States ===---")
        for idx, state in self.states.items():
            print(f"state {idx}")
            print(lr_state_to_str(state, "    "))

    def get_conflicts(self) -> list[tuple[int, str, set[LRAction]]]:
        result = []
        for state, col in self.parsing_table.items():
            for sym, actions in col.items():
                if len(actions) > 1:
                    result.append(tuple([state, sym, actions]))

        return result

    def bison_like_report(self) -> None:
        for state, _, actions in self.get_conflicts():
            conflict = [action.type_ for action in actions]
            print(f"State {state} conflict: {conflict}")

        print("Grammar\n")
        for idx, rule in self.ruleset.rules.items():
            print(f"  {idx:04} {rule}")

        print("\n\nTerminals, with rules where they appear\n")
        for el in sorted(self.terminals):
            appearances = []
            for k, v in self.ruleset.rules.items():
                if el in v or el in el in v.rhs:
                    appearances.append(k)
            print(f"{el}: {' '.join(map(str, appearances))}")

        print("\n\nNonterminals, with rules where they appear\n")
        for el in self.non_terminals:
            appearances_left = []
            appearnaces_right = []
            for k, v in self.ruleset.rules.items():
                if el in v.lhs:
                    appearances_left.append(k)
                if el in v.rhs:
                    appearnaces_right.append(k)

            print(el)
            print(f"  on left: {' '.join(map(str, appearances_left))}", end="")
            if len(appearnaces_right) > 0:
                print(f", on right: {' '.join(map(str, appearnaces_right))}", end="")
            print()

        print("\n\n---=== States ===---\n")
        for idx, state in self.states.items():
            print(f"state {idx}")
            print(lr_state_to_str(state, "    "))

            action_list = []
            offset = 0
            for sym, actions in self.parsing_table[idx].items():
                if len(actions) == 0:
                    continue
                for action in actions:
                    s: str = ""
                    match action:
                        case LRAction(type_=LRActionEnum.ACCEPT):
                            s = "accept"
                        case LRAction(type_=LRActionEnum.REDUCE, to=n):
                            s = f"reduce using rule {n}"
                        case LRAction(type_=LRActionEnum.GOTO, to=n):
                            s = f"go to state {n}"
                        case LRAction(type_=LRActionEnum.SHIFT, to=n):
                            s = f"shift and go to state {n}"
                    action_list.append(tuple([sym, s]))
                offset = max(len(sym), offset)

            for sym, s in sorted(action_list, key=lambda x: len(x[1])):
                print(f"    {sym}", end="")
                print(" " * (offset - len(sym) + 2), end="")
                print(s)

            print("\n")
