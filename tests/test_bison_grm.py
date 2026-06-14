# TODO: fix these tests - the difference lies now at
#       the amount of states. I should count the states
#       in bison result and compare mine

from parsers.grammars.bison_grammar_parser import bison_to_ruleset


SIMPLE_GRM = r"""
%union {
	int pos;
	int ival;
	string sval;
	}

%token <sval> ID STRING
%token <ival> INT

%token
    COMMA COLON SEMICOLON
    LPAREN RPAREN
    L_SQR_BRCK R_SQR_BRCK
    L_MO_BRCK R_MO_BRCK DOT
    PLUS MINUS TIMES DIVIDE EQ NEQ LT LE GT GE
    AND OR ASSIGN
    ARRAY IF ELSE WHILE FOR RETURN
    BREAK STRUCT
    ARROW REF

%start expression_list

%%


s_expression
    : STRING
    | INT
    ;

expression
    : s_expression
    | ID ASSIGN expression
    | open_if
    ;


open_if
    : IF LPAREN expression RPAREN expression
    | IF LPAREN expression RPAREN closed_if ELSE expression
    ;

closed_if
    : IF LPAREN expression RPAREN closed_if ELSE closed_if
    | s_expression
    ;


expression_list
    : expression expression_list_aux ;

expression_list_aux
    : SEMICOLON expression expression_list_aux
    |
    ;
"""


def test_given_valid_yacc_grammar_example_func_returns_valid_amount_of_rules():
    ruleset = bison_to_ruleset(SIMPLE_GRM)
    assert len(ruleset.rules) == 12


def test_given_valid_yacc_grammar_with_empty_rule_returns_empty_parsed_rule():
    ruleset = bison_to_ruleset(SIMPLE_GRM)

    empty_rule_lhs = "expression_list_aux"
    empty_rules_with_given_lhs = [
        el
        for el in ruleset.rules.values()
        if el.lhs == empty_rule_lhs and len(el.rhs) == 0
    ]
    assert len(empty_rules_with_given_lhs) == 1


def test_given_grammar_with_defined_start_function_returns_valid_start_sym_idx():
    ruleset = bison_to_ruleset(SIMPLE_GRM)

    assert ruleset.start_rule_idx == 9
