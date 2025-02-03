import spltools
import streamlit as st

st.title("spltools")
st.header("Battle configuration summarizer")
st.text("")


@st.cache_resource
def get_card_data():
    return spltools.get_card_data()


def generate_summary():
    b = spltools.Battle(str(st.session_state.bqid_key).strip(),
                        card_data=st.session_state.card_data)
    st.session_state['battle_summary'] = b.markdown_summary()
    st.session_state['battle_log'] = b.get_log(markdown=True)


st.session_state['card_data'] = get_card_data()
if 'battle_summary' not in st.session_state:
    st.session_state['battle_summary'] = None

bqid_entry = st.text_input("Enter battle queue id here:",
                           key='bqid_key',
                           on_change=generate_summary)
if st.session_state.battle_summary is not None:
    st.code(st.session_state.battle_summary, language='python')
    st.header("Battle log")
    st.markdown(st.session_state.battle_log)
    st.code(st.session_state.battle_log, language='python')
