import streamlit as st
import pandas as pd
import re
import time
import html
import my_parser  
import graphviz


# ---------- Lexer Function ----------
def lexical_analyzer(code):
    keywords = {'int', 'float', 'if', 'else', 'return', 'while', 'for', 'main'}
    operators = {'+', '-', '*', '/', '=', '==', '!=', '<', '<=', '>', '>='}
    delimiters = {';', ',', '(', ')', '{', '}'}

    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),
        ('IDENTIFIER', r'[A-Za-z_]\w*'),
        ('OPERATOR', '|'.join(map(re.escape, operators))),
        ('DELIMITER', '|'.join(map(re.escape, delimiters))),
        ('SKIP',     r'[ \t]+'),
        ('NEWLINE',  r'\n'),
        ('MISMATCH', r'.'),
    ]

    tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
    line_num = 1
    symbol_table = {}
    tokens = []

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'NUMBER':
            tokens.append(("NUMBER", value, line_num))
        elif kind == 'IDENTIFIER':
            if value in keywords:
                tokens.append(("KEYWORD", value, line_num))
            else:
                tokens.append(("IDENTIFIER", value, line_num))
                if value not in symbol_table:
                    symbol_table[value] = {"type": "", "line": line_num}
        elif kind == 'OPERATOR':
            tokens.append(("OPERATOR", value, line_num))
        elif kind == 'DELIMITER':
            tokens.append(("DELIMITER", value, line_num))
        elif kind == 'NEWLINE':
            line_num += 1
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            tokens.append(("INVALID", value, line_num))

    return tokens, symbol_table

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Lexical Analyzer UI", layout="wide")
st.title("🧠 Lexical Analyzer & Symbol Table")
st.markdown("Analyze code into tokens and generate a symbol table interactively.")

if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "code_input" not in st.session_state:
    st.session_state.code_input = ""

with st.sidebar:
    st.header("📁 Upload or Load Code")
    uploaded_file = st.file_uploader("Upload code (.txt)", type=["txt"])
    if uploaded_file:
        st.session_state.code_input = uploaded_file.read().decode("utf-8")
        st.success("File uploaded successfully!")

    if st.button("📌 Load Example"):
        st.session_state.code_input = """int main() {
    int a = 5;
    float b = 2.5;
    if (a > b) {
        return a;
    }
    return 0;
}"""

code_input = st.session_state.code_input

st.markdown("### 🎞️ Token Animation Walkthrough")
if code_input:
    tokens, _ = lexical_analyzer(code_input)

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Prev") and st.session_state.current_index > 0:
            st.session_state.current_index -= 1

    with col2:
        if st.button("➡️ Next") and st.session_state.current_index < len(tokens) - 1:
            st.session_state.current_index += 1

    idx = st.session_state.current_index
    token = tokens[idx]

    escaped_code = html.escape(code_input)
    lines = escaped_code.split('\n')
    current_line = token[2] - 1    #highligh current token
    lines[current_line] = re.sub(
        re.escape(token[1]),
        f'<span style="background-color: #d3d3d3; color: black; padding:2px; border-radius:4px;">{token[1]}</span>',
        lines[current_line], count=1
    )
    highlighted_code = '\n'.join(lines)

    with st.expander("🔍 Token Animation View", expanded=True):
        st.markdown(f"### 🔦 Highlighted Code")
        st.markdown(f"<div style='background-color:#0e1117; color:white; padding:10px; border-radius:8px;'><pre style='white-space:pre-wrap;'>{highlighted_code}</pre></div>", unsafe_allow_html=True)

        st.markdown("### 🪄 Current Token Details")
        st.dataframe(pd.DataFrame([token], columns=["Type", "Value", "Line"]), use_container_width=True, hide_index=True)

        st.markdown("### 🧩 Tokens Seen So Far")
        st.dataframe(pd.DataFrame(tokens[:idx + 1], columns=["Type", "Value", "Line"]), use_container_width=True, hide_index=True)
else:
    st.warning("Upload or enter some code to begin the walkthrough.")

st.markdown("---")
tabs = st.tabs(["📝 Code Editor", "🧩 Tokens", "📊 Symbol Table","Tree Graph"])

with tabs[0]:
    st.subheader("Edit or Paste Your Code")

    with st.form("code_form"):
        new_code = st.text_area("Write your code here", value=st.session_state.code_input, height=300)
        submitted = st.form_submit_button("🔄 Update Code")

        if submitted:
            st.session_state.code_input = new_code
            st.session_state.current_index = 0
            st.rerun()  # Updated for latest Streamlit
    if st.session_state.code_input:
        st.code(st.session_state.code_input, language="c")



with tabs[1]:
    if st.session_state.code_input:
        tokens, _ = lexical_analyzer(st.session_state.code_input)
        df_tokens = pd.DataFrame(tokens, columns=["Type", "Value", "Line"])
        st.subheader("🧩 Tokens")
        st.dataframe(df_tokens.style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#333'), ('color', 'white')]},
            {'selector': 'tbody', 'props': [('background-color', '#111'), ('color', 'white')]}
        ]), use_container_width=True, hide_index=True)

        st.download_button("📥 Download Tokens", df_tokens.to_csv(index=False), "tokens.csv")
        st.metric("🔢 Total Tokens", len(tokens))
    else:
        st.info("Add code first to see tokens.")

with tabs[2]:
    if st.session_state.code_input:
        _, symbol_table = lexical_analyzer(st.session_state.code_input)
        df_symbols = pd.DataFrame.from_dict(symbol_table, orient='index')
        df_symbols.reset_index(inplace=True)
        df_symbols.columns = ['Identifier', 'Type', 'Line']
        st.subheader("📊 Symbol Table")
        st.dataframe(df_symbols.style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#333'), ('color', 'white')]},
            {'selector': 'tbody', 'props': [('background-color', '#111'), ('color', 'white')]}
        ]), use_container_width=True, hide_index=True)

        st.download_button("📥 Download Symbol Table", df_symbols.to_csv(index=False), "symbol_table.csv")
        st.metric("🧾 Unique Identifiers", len(symbol_table))
    else:
        st.info("Paste some code to extract the symbol table.")
with tabs[3]:
    st.subheader("🌲 Visual Parse Tree")
    code = st.session_state.code_input
    if code:
        try:
            parse_tree = my_parser.parse(code)

            dot = parse_tree.to_graphviz()
            st.graphviz_chart(dot.source)
        except Exception as e:
            st.error(f"Parsing failed: {e}")
    else:
        st.info("Paste code above to generate a parse tree.")
