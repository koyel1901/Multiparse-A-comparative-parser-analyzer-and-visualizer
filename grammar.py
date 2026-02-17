class Grammar:
    def __init__(self):
        self.productions = {}
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None

    def add_production(self, lhs, rhs_list):
        if self.start_symbol is None:
            self.start_symbol = lhs

        self.non_terminals.add(lhs)

        if lhs not in self.productions:
            self.productions[lhs] = []

        for rhs in rhs_list:
            symbols = rhs.split()
            self.productions[lhs].append(symbols)

            for symbol in symbols:
                if symbol == "ε":
                    continue
                if symbol[0].isupper():
                    self.non_terminals.add(symbol)
                else:
                    self.terminals.add(symbol)

    def display(self):
        print("\nGrammar:")
        for lhs in self.productions:
            right = [" ".join(prod) for prod in self.productions[lhs]]
            print(f"{lhs} -> {' | '.join(right)}")
