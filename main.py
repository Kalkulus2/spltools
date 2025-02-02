import spltools
import streamlit as st

st.title("spltools")
st.header("Battle configuration summarizer")

def generate_summary():
    b = spltools.Battle(str(st.session_state.bqid_key).strip())
    st.session_state['battle_summary'] = b.markdown_summary()


if 'battle_summary' not in st.session_state:
    st.session_state['battle_summary'] = None

bqid_entry = st.text_input("Enter battle queue id here:",
                           key='bqid_key',
                           on_change=generate_summary)
if st.session_state.battle_summary is not None:
    st.code(st.session_state.battle_summary, language='python')