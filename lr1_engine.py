from lr0_engine import LR0Item

class LR1Item(LR0Item):
    def __init__(self, lhs, rhs, dot, lookahead):
        super().__init__(lhs, rhs, dot)
        self.lookahead = lookahead

    def __repr__(self):
        rhs = self.rhs.copy()
        rhs.insert(self.dot, "•")
        return f"[{self.lhs} -> {' '.join(rhs)}, {self.lookahead}]"

    def __eq__(self, other):
        return (
            super().__eq__(other) and
            self.lookahead == other.lookahead
        )

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot, self.lookahead))

class LR1Engine:
    def __init__(self, grammar, first_sets):
        self.grammar = grammar
        self.first_sets = first_sets
        self._closure_cache = {}
        self._goto_cache = {}

    def get_first_of_string(self, symbols):
        res = set()
        if not symbols:
            return {"ε"}
            
        for sym in symbols:
            if sym == "ε":
                continue
            
            # terminals and $ are their own FIRST set
            if sym in self.grammar.terminals or sym == "$":
                res.add(sym)
                return res
            
            # safety check for non-terminals
            if sym in self.first_sets:
                res |= (self.first_sets[sym] - {"ε"})
                if "ε" not in self.first_sets[sym]:
                    return res
            else:
                # unknown symbol, treat as terminal
                res.add(sym)
                return res
        
        res.add("ε")
        return res

    def closure(self, items):
        key = frozenset(items)
        if key in self._closure_cache:
            return self._closure_cache[key]

        closure_set = set(items)
        changed = True
        while changed:
            changed = False
            new_items = set()
            for item in closure_set:
                if item.dot < len(item.rhs):
                    symbol = item.rhs[item.dot]
                    if symbol in self.grammar.non_terminals:
                        # Beta is the part after the symbol
                        beta = item.rhs[item.dot + 1:]
                        # Lookahead for new items: FIRST(beta + lookahead)
                        for b_lookahead in self.get_first_of_string(beta + [item.lookahead]):
                            if b_lookahead == "ε": continue
                            for prod in self.grammar.productions[symbol]:
                                new_item = LR1Item(symbol, prod, 0, b_lookahead)
                                if new_item not in closure_set:
                                    new_items.add(new_item)
            if new_items:
                closure_set |= new_items
                changed = True
        
        res = frozenset(closure_set)
        self._closure_cache[key] = res
        return res

    def goto(self, items, symbol):
        key = (frozenset(items), symbol)
        if key in self._goto_cache:
            return self._goto_cache[key]

        moved_items = set()
        for item in items:
            if item.dot < len(item.rhs) and item.rhs[item.dot] == symbol:
                moved_items.add(
                    LR1Item(item.lhs, item.rhs, item.dot + 1, item.lookahead)
                )

        res = self.closure(moved_items)
        self._goto_cache[key] = res
        return res

    def build_canonical_collection(self):
        start_symbol = self.grammar.start_symbol
        start_prod = self.grammar.productions[start_symbol][0]
        # Augmented start always has $ as lookahead
        start_item = LR1Item(start_symbol, start_prod, 0, "$")

        I0 = self.closure({start_item})

        states = [I0]
        states_map = {I0: 0}
        transitions = {}

        symbols = self.grammar.terminals.union(self.grammar.non_terminals)

        i = 0
        while i < len(states):
            state = states[i]
            for symbol in symbols:
                goto_state = self.goto(state, symbol)
                if not goto_state:
                    continue

                if goto_state not in states_map:
                    states_map[goto_state] = len(states)
                    states.append(goto_state)

                transitions[(i, symbol)] = states_map[goto_state]
            i += 1

        return states, transitions
