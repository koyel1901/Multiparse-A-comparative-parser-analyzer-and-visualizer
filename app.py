import streamlit as st
import sys
import os
import pandas as pd

# Allow importing from the same directory
sys.path.insert(0, os.path.dirname(__file__))

from grammar import Grammar
from first_follow import FirstFollow
from ll1_table import LL1Table
from parser import LL1Parser
from lr0_engine import LR0Engine, LR0Item
from lr0_table import LR0Table
from slr1_table import SLR1Table
from slr1_parser import SLR1Parser

# ─────────────────────────────────────────────
st.set_page_config(page_title="Parser Visualizer", layout="wide")
st.title("🔍 Parser Visualizer")
st.caption("LL(1) · LR(0) · SLR(1) — interactive grammar analysis")

# ─────────────────────────────────────────────
# SIDEBAR — Grammar Input
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📝 Grammar Input")

    default_grammar = """E -> T E'
E' -> + T E' | ε
T -> F T'
T' -> * F T' | ε
F -> ( E ) | id"""

    grammar_text = st.text_area(
        "Enter productions (one per line, use | for alternatives):",
        value=default_grammar,
        height=200,
    )

    st.markdown("**Format:** `LHS -> RHS1 | RHS2`  \nUse `ε` for epsilon.")

    parse_input = st.text_input(
        "Input string to parse (space-separated):",
        value="id + id * id",
    )

    run = st.button("▶ Run Analysis", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def build_grammar(text):
    g = Grammar()
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        rhs_list = [r.strip() for r in rhs.split("|")]
        g.add_production(lhs, rhs_list)
    return g


def sorted_items(items, grammar, order):
    return sorted(
        items,
        key=lambda x: (
            0 if x.lhs == grammar.start_symbol else 1,
            order.get(x.lhs, 100),
            " ".join(x.rhs),
        ),
    )


def capture_ll1_trace(grammar, table_obj, input_string):
    rows = []
    stack = ["$", grammar.start_symbol]
    tokens = input_string.split() + ["$"]
    pos = 0

    while stack:
        top = stack[-1]
        current = tokens[pos]
        stack_str = " ".join(stack)
        inp_str = " ".join(tokens[pos:])

        if top == current == "$":
            rows.append([stack_str, inp_str, "✅ ACCEPT"])
            break
        elif top in grammar.terminals or top == "$":
            if top == current:
                rows.append([stack_str, inp_str, f"Match '{top}'"])
                stack.pop()
                tokens.pop(0)
            else:
                rows.append([stack_str, inp_str, "❌ ERROR"])
                break
        else:
            if current in table_obj.table.get(top, {}):
                prod = table_obj.table[top][current]
                rows.append([stack_str, inp_str, f"{top} → {' '.join(prod)}"])
                stack.pop()
                if prod != ["ε"]:
                    stack.extend(reversed(prod))
            else:
                rows.append([stack_str, inp_str, "❌ ERROR"])
                break
    return rows


def capture_slr1_trace(grammar, action, goto_table, input_string):
    rows = []
    tokens = input_string.split() + ["$"]
    state_stack = [0]
    symbol_stack = ["$"]
    pos = 0

    while True:
        state = state_stack[-1]
        current = tokens[pos]
        state_str = " ".join(str(s) for s in state_stack)
        sym_str = " ".join(symbol_stack)
        inp_str = " ".join(tokens[pos:])
        act = action.get((state, current))

        if act is None:
            rows.append([state_str, sym_str, inp_str, "❌ ERROR"])
            break
        elif act == "acc":
            rows.append([state_str, sym_str, inp_str, "✅ ACCEPT"])
            break
        elif act.startswith("s"):
            next_state = int(act[1:])
            rows.append([state_str, sym_str, inp_str, f"Shift → s{next_state}"])
            state_stack.append(next_state)
            symbol_stack.append(current)
            pos += 1
        elif act.startswith("r"):
            rule_str = act[2:-1]
            arrow = rule_str.index("->")
            lhs = rule_str[:arrow].strip()
            rhs_str = rule_str[arrow + 2:].strip()
            rhs = rhs_str.split() if rhs_str != "ε" else []
            rows.append([state_str, sym_str, inp_str, f"Reduce: {rule_str}"])
            for _ in rhs:
                state_stack.pop()
                symbol_stack.pop()
            symbol_stack.append(lhs)
            top_state = state_stack[-1]
            gs = goto_table.get((top_state, lhs))
            if gs is None:
                rows.append([state_str, sym_str, inp_str, f"❌ GOTO ERROR"])
                break
            state_stack.append(gs)
        else:
            rows.append([state_str, sym_str, inp_str, f"❌ Unknown: {act}"])
            break

    return rows


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if not run:
    st.info("👈 Enter a grammar in the sidebar and click **Run Analysis**.")
    st.stop()

try:
    grammar = build_grammar(grammar_text)
except Exception as e:
    st.error(f"Grammar parse error: {e}")
    st.stop()

# Tabs
tab_grammar, tab_ff, tab_ll1, tab_lr0, tab_slr1, tab_compare = st.tabs([
    "Grammar", "FIRST / FOLLOW", "LL(1)", "LR(0)", "SLR(1)", "Comparison"
])

order = {nt: i for i, nt in enumerate(grammar.productions)}

# ── FIRST / FOLLOW ──────────────────────────
ff = FirstFollow(grammar)
ff.compute_first()
ff.compute_follow()

# ── LL(1) Table ──────────────────────────────
ll1_table = LL1Table(grammar, ff.first, ff.follow)
ll1_table.build_table()

# ── LR(0) ────────────────────────────────────
engine = LR0Engine(grammar)
engine.augment_grammar()
states, transitions = engine.build_canonical_collection()

lr0_table = LR0Table(grammar, states, transitions)
lr0_table.build_table()

# ── SLR(1) ───────────────────────────────────
slr1 = SLR1Table(grammar, states, transitions, ff.follow)
slr1.build_table()


# ════════════════════════════════════════════
# TAB: Grammar
# ════════════════════════════════════════════
with tab_grammar:
    st.subheader("Grammar Productions")
    rows = []
    for lhs, prods in grammar.productions.items():
        for rhs in prods:
            rows.append({"LHS": lhs, "→": " ".join(rhs)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Non-terminals", len(grammar.non_terminals))
    col2.metric("Terminals", len(grammar.terminals))
    col3.metric("Productions", sum(len(v) for v in grammar.productions.values()))


# ════════════════════════════════════════════
# TAB: FIRST / FOLLOW
# ════════════════════════════════════════════
with tab_ff:
    st.subheader("FIRST and FOLLOW Sets")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**FIRST Sets**")
        ff_rows = [{"Non-terminal": nt, "FIRST": ", ".join(sorted(ff.first[nt]))}
                   for nt in sorted(ff.first)]
        st.dataframe(pd.DataFrame(ff_rows), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**FOLLOW Sets**")
        follow_rows = [{"Non-terminal": nt, "FOLLOW": ", ".join(sorted(ff.follow[nt]))}
                       for nt in sorted(ff.follow)]
        st.dataframe(pd.DataFrame(follow_rows), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════
# TAB: LL(1)
# ════════════════════════════════════════════
with tab_ll1:
    st.subheader("LL(1) Parsing Table")

    terminals = sorted(grammar.terminals) + ["$"]
    non_terminals_ll1 = [nt for nt in grammar.non_terminals
                         if nt in ll1_table.table]

    table_data = {}
    for t in terminals:
        col_data = {}
        for nt in non_terminals_ll1:
            cell = ll1_table.table.get(nt, {}).get(t, "")
            if cell:
                cell = " ".join(cell)
            col_data[nt] = cell
        table_data[t] = col_data

    df_ll1 = pd.DataFrame(table_data, index=non_terminals_ll1)
    st.dataframe(df_ll1, use_container_width=True)

    if ll1_table.conflicts:
        st.error(f"⚠ {len(ll1_table.conflicts)} conflict(s) — grammar is NOT LL(1)")
        for lhs, t in ll1_table.conflicts:
            st.write(f"  Conflict at M[{lhs}, {t}]")
    else:
        st.success("✓ No conflicts — grammar IS LL(1)")

    st.subheader("LL(1) Parse Trace")
    st.caption(f"Input: `{parse_input}`")
    trace = capture_ll1_trace(grammar, ll1_table, parse_input)
    df_trace = pd.DataFrame(trace, columns=["Stack", "Input", "Action"])
    st.dataframe(df_trace, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════
# TAB: LR(0)
# ════════════════════════════════════════════
with tab_lr0:
    st.subheader("LR(0) Canonical Collection")

    for i, state in enumerate(states):
        with st.expander(f"State I{i}"):
            items_str = [str(item) for item in sorted_items(set(state), grammar, order)]
            for s in items_str:
                st.code(s)

    st.subheader("LR(0) DFA Transitions")
    trans_rows = [{"From": f"I{s}", "Symbol": sym, "To": f"I{t}"}
                  for (s, sym), t in sorted(transitions.items())]
    st.dataframe(pd.DataFrame(trans_rows), use_container_width=True, hide_index=True)

    st.subheader("LR(0) Parsing Table")
    terminals_lr = sorted(grammar.terminals) + ["$"]
    nts_lr = sorted(grammar.non_terminals - {grammar.start_symbol})

    lr0_rows = []
    for i in range(len(states)):
        row = {"State": i}
        for t in terminals_lr:
            row[t] = lr0_table.action.get((i, t), "")
        for nt in nts_lr:
            row[nt] = lr0_table.goto.get((i, nt), "")
        lr0_rows.append(row)

    df_lr0 = pd.DataFrame(lr0_rows).set_index("State")
    st.dataframe(df_lr0, use_container_width=True)


# ════════════════════════════════════════════
# TAB: SLR(1)
# ════════════════════════════════════════════
with tab_slr1:
    st.subheader("SLR(1) Parsing Table")

    slr_rows = []
    for i in range(len(states)):
        row = {"State": i}
        for t in terminals_lr:
            row[t] = slr1.action.get((i, t), "")
        for nt in nts_lr:
            row[nt] = slr1.goto.get((i, nt), "")
        slr_rows.append(row)

    df_slr1 = pd.DataFrame(slr_rows).set_index("State")
    st.dataframe(df_slr1, use_container_width=True)

    if slr1.conflicts:
        st.error(f"⚠ {len(slr1.conflicts)} conflict(s) — grammar is NOT SLR(1)")
        for state, terminal, old, new in slr1.conflicts:
            st.write(f"  State {state}, '{terminal}': `{old}` vs `{new}`")
    else:
        st.success("✓ No conflicts — grammar IS SLR(1)")

    st.subheader("SLR(1) Parse Trace")
    st.caption(f"Input: `{parse_input}`")
    slr_trace = capture_slr1_trace(grammar, slr1.action, slr1.goto, parse_input)
    df_slr_trace = pd.DataFrame(slr_trace, columns=["State Stack", "Symbol Stack", "Input", "Action"])
    st.dataframe(df_slr_trace, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════
# TAB: Comparison
# ════════════════════════════════════════════
with tab_compare:
    st.subheader("LL(1) vs LR(0) vs SLR(1) — Comparison")

    ll1_ok = len(ll1_table.conflicts) == 0
    lr0_ok = True  # LR(0) doesn't track conflicts explicitly here
    slr1_ok = len(slr1.conflicts) == 0

    col1, col2, col3 = st.columns(3)
    col1.metric("LL(1)", "✅ Yes" if ll1_ok else "❌ No", "Conflicts: " + str(len(ll1_table.conflicts)))
    col2.metric("LR(0)", "Builds states", f"{len(states)} states")
    col3.metric("SLR(1)", "✅ Yes" if slr1_ok else "❌ No", "Conflicts: " + str(len(slr1.conflicts)))

    st.markdown("---")
    st.markdown("""
| Property | LL(1) | LR(0) | SLR(1) |
|---|---|---|---|
| Parsing direction | Top-down | Bottom-up | Bottom-up |
| Lookahead | 1 token | None | FOLLOW sets |
| Conflict resolution | FIRST/FOLLOW | None | FOLLOW(A) on reduce |
| Power | Weakest | Intermediate | Stronger than LR(0) |
| Stack contents | Symbols | States + Symbols | States + Symbols |
""")

    if slr1_ok and not ll1_ok:
        st.info("💡 This grammar is SLR(1) but not LL(1) — a common case for left-recursive or ambiguous-looking grammars.")
    elif ll1_ok and slr1_ok:
        st.success("🎉 Grammar is both LL(1) and SLR(1).")
    elif not slr1_ok:
        st.warning("⚠ Grammar is neither LL(1) nor SLR(1). Consider LALR(1) or GLR parsing.")

    st.subheader("Reduce Action Coverage")
    st.caption("SLR(1) reduces only on FOLLOW(A), while LR(0) reduces on all terminals — fewer reduce entries = fewer conflicts.")

    coverage_rows = []
    for lhs in grammar.productions:
        if lhs == grammar.start_symbol:
            continue
        follow_size = len(ff.follow.get(lhs, set()))
        all_terms = len(grammar.terminals) + 1  # +1 for $
        coverage_rows.append({
            "Non-terminal": lhs,
            "FOLLOW size": follow_size,
            "All terminals": all_terms,
            "SLR(1) reduces on": follow_size,
            "LR(0) reduces on": all_terms,
        })

    if coverage_rows:
        st.dataframe(pd.DataFrame(coverage_rows), use_container_width=True, hide_index=True)