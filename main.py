from grammar import Grammar
from first_follow import FirstFollow
from ll1_table import LL1Table
from parser import LL1Parser


def main():
    grammar = Grammar()

    # Example Grammar (Expression Grammar)
    grammar.add_production("E", ["T E'"])
    grammar.add_production("E'", ["+ T E'", "ε"])
    grammar.add_production("T", ["F T'"])
    grammar.add_production("T'", ["* F T'", "ε"])
    grammar.add_production("F", ["( E )", "id"])
    grammar.display()

    # FIRST & FOLLOW
    ff = FirstFollow(grammar)
    ff.compute_first()
    ff.compute_follow()
    ff.display()

    # LL(1) Table
    table = LL1Table(grammar, ff.first, ff.follow)
    table.build_table()
    table.display()

    # Parsing
    parser = LL1Parser(grammar, table.table)

    input_string = input("\nEnter input string (space separated): ")
    parser.parse(input_string)

if __name__ == "__main__":
    main()
