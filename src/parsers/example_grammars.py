GRAMMAR_3_12: list[str] = [
    "Z -> d",
    "Z -> X Y Z",
    "Y -> ",
    "Y -> c",
    "X -> Y",
    "X -> a",
]

GRAMMAR_3_15: list[str] = [
    "S -> E $",
    "T -> F T'",
    "E -> T E'",
    "E' -> + T E'",
    "E' -> - T E'",
    "E' ->",
    "T' -> * F T'",
    "T' -> / F T'",
    "T' ->",
    "F -> id",
    "F -> num",
    "F -> ( E )",
]

GRAMMAR_3_20: list[str] = [
    "S' -> S $",
    "S -> ( L )",
    "S -> x",
    "L -> S",
    "L -> L , S",
]

GRAMMAR_3_23: list[str] = [
    "S -> E $",
    "E -> T + E",
    "E -> T",
    "T -> x",
]

GRAMMAR_3_26: list[str] = [
    "S` -> S $",
    "S -> V = E",
    "E -> V",
    "V -> x",
    "S -> E",
    "V -> * E",
]
