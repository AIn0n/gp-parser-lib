from parsers.lr.lr_types import LRParsingTable, LRAction
from parsers.lr.lr0 import LR0Parser


class SLRParser(LR0Parser):
    def _compute_parsing_table(self) -> LRParsingTable:
        """
        Returns parsing table for given grammar. Table is row-first, and the
        first dict is representing the states number, dict inside it stores
        symbols and actions mapping.
        """

        rule_lookup = {r: i for i, r in self.indexed_rules.items()}
        t: LRParsingTable = self._init_parsing_table()
        for idx, i in self.states.items():
            for item in i:
                if item.is_dot_at_end():
                    rule_idx = rule_lookup[item.to_rule()]
                    # main difference from LR(0) here - we reduce based on
                    # what's follows the rule
                    # page 63
                    for non_term in self.follow[item.rule.lhs]:
                        t[idx][non_term].add(LRAction.reduce(rule_idx))
                if item.peek_after_dot() == self.eol:
                    t[idx][self.eol].add(LRAction.accept())

        self._add_edges_to_parsing_table(t)
        return t
