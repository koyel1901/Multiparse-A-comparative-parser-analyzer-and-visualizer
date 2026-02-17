class LL1Parser:
    def __init__(self, grammar, table):
        self.grammar = grammar
        self.table = table

    def parse(self, input_string):
        stack = ["$", self.grammar.start_symbol]
        input_tokens = input_string.split() + ["$"]

        print("\nParsing Trace:")
        print(f"{'Stack':<25}{'Input':<25}{'Action'}")
        print("-" * 60)

        while stack:
            top = stack[-1]
            current_input = input_tokens[0]

            print(f"{' '.join(stack):<25}{' '.join(input_tokens):<25}", end="")

            # Accept condition
            if top == current_input == "$":
                print("ACCEPT")
                return True

            # If terminal or $
            elif top in self.grammar.terminals or top == "$":
                if top == current_input:
                    stack.pop()
                    input_tokens.pop(0)
                    print("Match")
                else:
                    print("ERROR")
                    return False

            # If non-terminal
            else:
                if current_input in self.table[top]:
                    production = self.table[top][current_input]
                    stack.pop()

                    if production != ["ε"]:
                        stack.extend(reversed(production))

                    print(f"{top} -> {' '.join(production)}")
                else:
                    print("ERROR")
                    return False

        return False
