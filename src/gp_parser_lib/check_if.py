from loguru import logger

from datetime import datetime

from parsers.lr.lr1 import LR1Parser
from parsers.lr.lr_types import LRItem
from parsers.lr.helpers import get_conflicts
from parsers.grammars.appel_grammar_parser import appel_to_ruleset

# current time as HH-MM-SS
time_str = datetime.now().strftime("%H-%M-%S")
logger.add(f"log_{time_str}.log", format="{message}")


grammar = [
    "P -> L",
    "S -> id := id",
    "S -> if id then S",
    "S -> if id then S else S",
    "L -> S",
    "L -> L ; S",
]

p = LR1Parser(appel_to_ruleset(grammar)).to_lalr(verbose=True)
p.print_rules_and_states()

print(p)
print(p.to_tabulate())
logger.debug("{conflicts}", conflicts=get_conflicts(p.parsing_table))

if __name__ == "__main__":
    dummy_grammar = [
        "S' -> S",
    ]
    parser = LR1Parser(appel_to_ruleset(dummy_grammar))
    parser.states = {
        1: frozenset(
            [
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", is_start=True),
                LRItem.from_rule_str(
                    "S' -> S", dot_pos=0, eol="ANOTHER", is_start=True
                ),
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="SYMBOL", is_start=True),
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="AT", is_start=True),
                LRItem.from_rule_str(
                    "S' -> S", dot_pos=0, eol="LOOKAHEAD", is_start=True
                ),
            ]
        ),
        0: frozenset(
            [
                LRItem.from_rule_str("S' -> S", dot_pos=0, eol="$end", is_start=True),
            ]
        ),
    }
    parser = parser.to_lalr()
    parser.print_rules_and_states()
    assert len(parser.states) == 1
    assert len(parser.states[0]) == 5
