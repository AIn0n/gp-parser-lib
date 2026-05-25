# TODO: Remove all logging code, or wrap it better before release

from loguru import logger

from parsers.base_parser import ParserPrintStyler
from parsers.lr.lr0 import LR0Parser
from parsers.lr.lr_types import (
    LRParsingTable,
    LRAction,
    LRItem,
    LRState,
    are_states_equal_wo_lookahead,
    IndexedLREdge,
    lr_state_to_str,
)
from parsers.parser_types import RuleSet


class LR1Parser(LR0Parser):
    def __init__(
        self,
        ruleset: RuleSet,
        styling: ParserPrintStyler | None = None,
    ):
        super().__init__(ruleset, styling=styling)

    def goto(self, i: LRState, x: str) -> LRState:  # type: ignore[override]
        j = frozenset([el.advance_dot() for el in i if el.peek_after_dot() == x])
        return self.closure(j)

    def closure(self, i: LRState) -> LRState:  # type: ignore[override]
        while True:
            new_i: set[LRItem] = set(i)
            for item in i:
                x: str | None = item.peek_after_dot()
                if x is None or x in self.terminals:
                    continue
                for rule in self.ruleset.rules.values():
                    if rule.lhs != x:
                        continue
                    # omitting X, getting all the elements after it
                    b = item.rule.rhs[item.dot_pos + 1 :]
                    z = item.lookahead
                    col = b if z is None else (*b, z)
                    for w in self.first_rhs(col):
                        new_i.add(LRItem(rule=rule, dot_pos=0, lookahead=w))
            if len(new_i) == len(i):
                break
            i = frozenset(new_i)
        return frozenset(i)

    def get_start_states(self):
        start_rule = self.get_start_rule()
        return set(
            [
                self.closure(
                    frozenset([LRItem(rule=start_rule, dot_pos=0, lookahead=None)])
                )
            ]
        )

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
                if item.is_dot_at_end() and item.lookahead is not None:
                    # main difference from SLR here - we reduce based on
                    # already computed lookahead values
                    # page 64
                    rule_idx = rule_lookup[item.to_rule()]
                    t[idx][item.lookahead].add(LRAction.reduce(rule_idx))
                if item.peek_after_dot() == self.ruleset.eol:
                    t[idx][self.ruleset.eol].add(LRAction.accept())

        self._add_edges_to_parsing_table(t)
        return t

    def to_lalr(self, verbose: bool = False) -> LR1Parser:
        mapping: dict[int, int] = dict()

        len_states = len(self.states)
        merges_count = 0
        # states already consumed into other state - no need to check them twice
        marked_states = []
        for fidx in range(len_states):
            if fidx in marked_states:
                continue
            for sidx in range(fidx + 1, len_states):
                if sidx in marked_states:
                    continue
                if are_states_equal_wo_lookahead(self.states[fidx], self.states[sidx]):
                    mapping[sidx] = fidx
                    merges_count += 1
                    self.states[fidx] |= self.states[sidx]
                    marked_states.append(sidx)
                    if verbose:
                        logger.debug("-= merging states =-")
                        logger.debug(f"state {sidx}")
                        logger.debug(lr_state_to_str(self.states[sidx]))
                        logger.debug(f"into state {fidx}")
                        logger.debug(lr_state_to_str(self.states[fidx]))

        if verbose:
            logger.debug(f"{merges_count=}")

        new_edges = set()
        for edge in self.edges:
            new_from = mapping.get(edge.from_, edge.from_)
            new_to = mapping.get(edge.to, edge.to)
            new_edges.add(IndexedLREdge(from_=new_from, to=new_to, symbol=edge.symbol))
            if verbose:
                logger.debug("-= moving edge =- ")
                logger.debug(
                    "prev_from={prev_from}, new_from={new_from}",
                    prev_from=edge.from_,
                    new_from=new_from,
                )
                logger.debug(
                    "prev_to={prev_to}, new_to={new_to}", prev_to=edge.to, new_to=new_to
                )
                logger.debug("symbol={sym}", sym=edge.symbol)

        self.edges = new_edges
        self.states = {k: v for k, v in self.states.items() if k not in mapping.keys()}
        self.parsing_table = self._compute_parsing_table()
        return self
