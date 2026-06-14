# TODO: fix the test - the main difference right now is the
#       amount of the states, for bison grammar format I'm
#       adding starting rule, which I'm not doing for appel
#       grammar type.

from parsers.grammars import appel_to_ruleset, bison_to_ruleset


def test_given_the_same_grammar_in_different_formats_both_grammar_formats_returns_same_ruleset():
    appel = [
        "P -> L",
        "S -> id assign id",
        "S -> if id then S",
        "S -> if id then S else S",
        "L -> S",
        "L -> L sem S",
    ]

    bison = r"""
%token id assign then if else sem

%start P

%%

    P
        : L ;
    S 
        : id assign id
        | if id then S
        | if id then S else S
        ;
    L
        : S 
        | L sem S ;
"""

    assert appel_to_ruleset(appel) == bison_to_ruleset(bison)
